# =============================================================================
# AlfaIA/ui/windows/login_window.py - Pantalla Completa Profesional
# =============================================================================

import sys
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QPushButton, QStackedWidget,
    QFrame, QCheckBox, QDateEdit, QComboBox,
    QMessageBox, QProgressBar, QApplication, QSizePolicy
)
from PyQt6.QtCore import Qt, QDate, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QPixmap, QPalette, QColor

# Agregar path para imports
sys.path.append(str(Path(__file__).parent.parent.parent))

try:
    from config.settings import Settings
    from core.auth.authentication import AuthenticationManager
    from core.database.models import NivelUsuario
except ImportError as e:
    print(f"Error importando dependencias: {e}")


    # Fallbacks simples
    class Settings:
        APP_NAME = "AlfaIA"
        APP_VERSION = "1.0.0"


    class NivelUsuario:
        @classmethod
        def __iter__(cls):
            return iter([cls()])

        def __init__(self):
            self.value = "Principiante"


class AuthWorker(QThread):
    """Worker thread para operaciones de autenticación"""
    auth_completed = pyqtSignal(bool, str)

    def __init__(self, operation, **kwargs):
        super().__init__()
        self.operation = operation
        self.kwargs = kwargs

    def run(self):
        """Ejecutar operación de autenticación"""
        try:
            from core.auth.authentication import AuthenticationManager
            auth_manager = AuthenticationManager()

            if self.operation == "login":
                success, message = auth_manager.login(
                    self.kwargs['email'],
                    self.kwargs['password']
                )
            elif self.operation == "register":
                success, message = auth_manager.register_user(**self.kwargs)
            else:
                success, message = False, "Operación no válida"

            self.auth_completed.emit(success, message)

        except Exception as e:
            self.auth_completed.emit(False, f"Error: {str(e)}")


class LoginForm(QWidget):
    """Formulario de inicio de sesión para pantalla completa"""
    login_success = pyqtSignal()
    switch_to_register = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.auth_worker = None
        self.setup_ui()

    def setup_ui(self):
        """Configurar interfaz del formulario de login"""
        # Layout principal horizontal
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Panel izquierdo - Información
        left_panel = self.create_info_panel()
        main_layout.addWidget(left_panel, 1)  # 50% del ancho

        # Panel derecho - Formulario
        right_panel = self.create_form_panel()
        main_layout.addWidget(right_panel, 1)  # 50% del ancho

    def create_info_panel(self):
        """Crear panel informativo izquierdo"""
        panel = QFrame()
        panel.setStyleSheet("""
            QFrame {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #1e40af,
                    stop: 0.5 #3b82f6,
                    stop: 1 #7c3aed
                );
                border: none;
            }
        """)

        layout = QVBoxLayout(panel)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(40)

        # Logo grande
        logo = QLabel("🎓")
        logo.setStyleSheet("""
            QLabel {
                font-size: 120px;
                color: white;
                margin: 0;
            }
        """)
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo)

        # Título principal
        title = QLabel("AlfaIA")
        title.setStyleSheet("""
            QLabel {
                font-size: 64px;
                font-weight: bold;
                color: white;
                margin: 0;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            }
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Subtítulo
        subtitle = QLabel("Aprende español con\ninteligencia artificial")
        subtitle.setStyleSheet("""
            QLabel {
                font-size: 24px;
                color: white;
                text-align: center;
                line-height: 1.4;
                margin: 0;
                text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
            }
        """)
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)

        # Características
        features = QLabel(
            "✨ Ejercicios interactivos\n🎮 Juegos educativos\n📊 Progreso personalizado\n🧠 Análisis inteligente")
        features.setStyleSheet("""
            QLabel {
                font-size: 18px;
                color: white;
                text-align: center;
                line-height: 2;
                margin: 20px 0;
                text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
            }
        """)
        features.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(features)

        return panel

    def create_form_panel(self):
        """Crear panel de formulario derecho"""
        panel = QFrame()
        panel.setStyleSheet("""
            QFrame {
                background-color: #f8fafc;
                border: none;
            }
        """)

        # Layout centrado que usa todo el ancho
        main_layout = QVBoxLayout(panel)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.setContentsMargins(100, 80, 100, 80)  # Márgenes más amplios

        # Contenedor del formulario - SIN máximo width
        form_container = QFrame()
        form_container.setMinimumWidth(500)  # Ancho mínimo generoso
        form_container.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 25px;
                padding: 60px 80px;
                border: 1px solid #e2e8f0;
                box-shadow: 0 10px 25px rgba(0,0,0,0.1);
            }
        """)

        form_layout = QVBoxLayout(form_container)
        form_layout.setSpacing(35)

        # Título del formulario
        form_title = QLabel("Iniciar Sesión")
        form_title.setStyleSheet("""
            QLabel {
                font-size: 42px;
                font-weight: bold;
                color: #1e293b;
                text-align: center;
                margin-bottom: 30px;
            }
        """)
        form_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        form_layout.addWidget(form_title)

        # Campo email
        email_label = QLabel("Correo Electrónico")
        email_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: 600;
                color: #374151;
                margin-bottom: 10px;
            }
        """)
        form_layout.addWidget(email_label)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("tu@email.com")
        self.email_input.setStyleSheet(self._get_input_style())
        self.email_input.setFixedHeight(65)  # Más alto
        form_layout.addWidget(self.email_input)

        # Campo contraseña
        password_label = QLabel("Contraseña")
        password_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: 600;
                color: #374151;
                margin-bottom: 10px;
            }
        """)
        form_layout.addWidget(password_label)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("••••••••••")
        self.password_input.setStyleSheet(self._get_input_style())
        self.password_input.setFixedHeight(65)  # Más alto
        form_layout.addWidget(self.password_input)

        # Espaciado extra
        form_layout.addSpacing(20)

        # Barra de progreso
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)
        self.progress_bar.hide()
        self.progress_bar.setFixedHeight(10)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                border-radius: 5px;
                background-color: #e2e8f0;
            }
            QProgressBar::chunk {
                background-color: #3b82f6;
                border-radius: 5px;
            }
        """)
        form_layout.addWidget(self.progress_bar)

        # Botón de login
        self.login_button = QPushButton("Iniciar Sesión")
        self.login_button.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                color: white;
                border: none;
                border-radius: 15px;
                padding: 20px;
                font-size: 20px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #2563eb;
                transform: scale(1.02);
            }
            QPushButton:pressed {
                background-color: #1d4ed8;
            }
            QPushButton:disabled {
                background-color: #94a3b8;
            }
        """)
        self.login_button.setFixedHeight(70)  # Más alto
        self.login_button.clicked.connect(self.handle_login)
        form_layout.addWidget(self.login_button)

        # Separador más elegante
        separator_layout = QHBoxLayout()
        separator_layout.setContentsMargins(20, 25, 20, 25)

        line1 = QFrame()
        line1.setFrameShape(QFrame.Shape.HLine)
        line1.setStyleSheet("QFrame { color: #cbd5e1; background-color: #cbd5e1; height: 2px; }")

        or_label = QLabel("o")
        or_label.setStyleSheet("""
            QLabel { 
                color: #64748b; 
                font-size: 16px; 
                font-weight: 500;
                margin: 0 25px;
                background-color: #f8fafc;
                padding: 0 15px;
            }
        """)

        line2 = QFrame()
        line2.setFrameShape(QFrame.Shape.HLine)
        line2.setStyleSheet("QFrame { color: #cbd5e1; background-color: #cbd5e1; height: 2px; }")

        separator_layout.addWidget(line1)
        separator_layout.addWidget(or_label)
        separator_layout.addWidget(line2)

        form_layout.addLayout(separator_layout)

        # Botón crear cuenta
        register_button = QPushButton("Crear Cuenta Nueva")
        register_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #3b82f6;
                border: 3px solid #3b82f6;
                border-radius: 15px;
                padding: 20px;
                font-size: 20px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #3b82f6;
                color: white;
                transform: scale(1.02);
            }
        """)
        register_button.setFixedHeight(70)  # Más alto
        register_button.clicked.connect(self.switch_to_register.emit)
        form_layout.addWidget(register_button)

        main_layout.addWidget(form_container)

        # Conectar Enter
        self.email_input.returnPressed.connect(self.handle_login)
        self.password_input.returnPressed.connect(self.handle_login)

        return panel

    def _get_input_style(self):
        """Estilo para campos de entrada"""
        return """
            QLineEdit {
                border: 3px solid #e2e8f0;
                border-radius: 15px;
                padding: 20px;
                font-size: 18px;
                background-color: #f8fafc;
                color: #1e293b;
                font-weight: 500;
            }
            QLineEdit:focus {
                border-color: #3b82f6;
                background-color: white;
                box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
            }
            QLineEdit::placeholder {
                color: #94a3b8;
                font-style: italic;
            }
        """

    def handle_login(self):
        """Manejar login"""
        email = self.email_input.text().strip()
        password = self.password_input.text()

        if not email or not password:
            QMessageBox.warning(self, "Campos requeridos", "Por favor ingrese email y contraseña")
            return

        self.login_button.setEnabled(False)
        self.login_button.setText("Iniciando...")
        self.progress_bar.show()

        self.auth_worker = AuthWorker("login", email=email, password=password)
        self.auth_worker.auth_completed.connect(self.on_login_completed)
        self.auth_worker.start()

    def on_login_completed(self, success: bool, message: str):
        """Resultado del login"""
        self.login_button.setEnabled(True)
        self.login_button.setText("Iniciar Sesión")
        self.progress_bar.hide()

        if success:
            QMessageBox.information(self, "¡Bienvenido!", "Login exitoso")
            self.login_success.emit()
        else:
            QMessageBox.warning(self, "Error", message)
            self.password_input.clear()


class RegisterForm(QWidget):
    """Formulario de registro para pantalla completa"""
    register_success = pyqtSignal()
    switch_to_login = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.auth_worker = None
        self.setup_ui()

    def setup_ui(self):
        """Configurar interfaz del formulario de registro"""
        # Layout principal horizontal
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Panel izquierdo - Formulario
        left_panel = self.create_form_panel()
        main_layout.addWidget(left_panel, 1)

        # Panel derecho - Información
        right_panel = self.create_info_panel()
        main_layout.addWidget(right_panel, 1)

    def create_info_panel(self):
        """Crear panel informativo derecho"""
        panel = QFrame()
        panel.setStyleSheet("""
            QFrame {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #059669,
                    stop: 0.5 #10b981,
                    stop: 1 #34d399
                );
                border: none;
            }
        """)

        layout = QVBoxLayout(panel)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(40)

        # Logo
        logo = QLabel("✨")
        logo.setStyleSheet("""
            QLabel {
                font-size: 120px;
                color: white;
                margin: 0;
            }
        """)
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo)

        # Título
        title = QLabel("¡Únete a AlfaIA!")
        title.setStyleSheet("""
            QLabel {
                font-size: 48px;
                font-weight: bold;
                color: white;
                margin: 0;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            }
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Texto motivacional
        motivational_text = QLabel("Comienza tu viaje de\naprendizaje del español\ncon inteligencia artificial")
        motivational_text.setStyleSheet("""
            QLabel {
                font-size: 24px;
                color: white;
                text-align: center;
                line-height: 1.4;
                margin: 0;
                text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
            }
        """)
        motivational_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(motivational_text)

        return panel

    def create_form_panel(self):
        """Crear panel de formulario izquierdo"""
        panel = QFrame()
        panel.setStyleSheet("""
            QFrame {
                background-color: #f8fafc;
                border: none;
            }
        """)

        # Layout centrado que usa más ancho
        main_layout = QVBoxLayout(panel)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.setContentsMargins(100, 40, 100, 40)  # Márgenes más amplios

        # Contenedor del formulario - SIN máximo width
        form_container = QFrame()
        form_container.setMinimumWidth(550)  # Ancho mínimo generoso
        form_container.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 25px;
                padding: 50px 70px;
                border: 1px solid #e2e8f0;
                box-shadow: 0 10px 25px rgba(0,0,0,0.1);
            }
        """)

        form_layout = QVBoxLayout(form_container)
        form_layout.setSpacing(25)

        # Título del formulario
        form_title = QLabel("Crear Cuenta")
        form_title.setStyleSheet("""
            QLabel {
                font-size: 42px;
                font-weight: bold;
                color: #1e293b;
                text-align: center;
                margin-bottom: 20px;
            }
        """)
        form_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        form_layout.addWidget(form_title)

        # Función helper para campos
        def add_field(label_text, placeholder, is_password=False, is_combo=False):
            label = QLabel(label_text)
            label.setStyleSheet("""
                QLabel {
                    font-size: 16px;
                    font-weight: 600;
                    color: #374151;
                    margin-bottom: 8px;
                }
            """)
            form_layout.addWidget(label)

            if is_combo:
                field = QComboBox()
                try:
                    field.addItems([nivel.value for nivel in NivelUsuario])
                except:
                    field.addItems(["Principiante", "Intermedio", "Avanzado"])
                field.setStyleSheet(self._get_combo_style())
            else:
                field = QLineEdit()
                field.setPlaceholderText(placeholder)
                if is_password:
                    field.setEchoMode(QLineEdit.EchoMode.Password)
                field.setStyleSheet(self._get_input_style())

            field.setFixedHeight(60)  # Más alto
            form_layout.addWidget(field)
            return field

        # Crear campos
        self.email_input = add_field("Correo Electrónico", "tu@email.com")
        self.nombre_input = add_field("Nombre", "Tu nombre")
        self.apellido_input = add_field("Apellido", "Tu apellido")
        self.password_input = add_field("Contraseña", "Mínimo 8 caracteres", is_password=True)
        self.confirm_password_input = add_field("Confirmar Contraseña", "Repetir contraseña", is_password=True)
        self.nivel_combo = add_field("Nivel Inicial", "", is_combo=True)

        # Espaciado extra
        form_layout.addSpacing(15)

        # Barra de progreso
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)
        self.progress_bar.hide()
        self.progress_bar.setFixedHeight(10)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                border-radius: 5px;
                background-color: #e2e8f0;
            }
            QProgressBar::chunk {
                background-color: #10b981;
                border-radius: 5px;
            }
        """)
        form_layout.addWidget(self.progress_bar)

        # Botón crear cuenta
        self.register_button = QPushButton("Crear Mi Cuenta")
        self.register_button.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                color: white;
                border: none;
                border-radius: 15px;
                padding: 20px;
                font-size: 20px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #059669;
                transform: scale(1.02);
            }
            QPushButton:pressed {
                background-color: #047857;
            }
            QPushButton:disabled {
                background-color: #94a3b8;
            }
        """)
        self.register_button.setFixedHeight(70)  # Más alto
        self.register_button.clicked.connect(self.handle_register)
        form_layout.addWidget(self.register_button)

        # Espaciado
        form_layout.addSpacing(15)

        # Botón volver
        back_button = QPushButton("Ya tengo cuenta")
        back_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #10b981;
                border: 3px solid #10b981;
                border-radius: 15px;
                padding: 20px;
                font-size: 20px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #10b981;
                color: white;
                transform: scale(1.02);
            }
        """)
        back_button.setFixedHeight(70)  # Más alto
        back_button.clicked.connect(self.switch_to_login.emit)
        form_layout.addWidget(back_button)

        main_layout.addWidget(form_container)

        return panel

    def _get_input_style(self):
        """Estilo para campos de entrada"""
        return """
            QLineEdit {
                border: 3px solid #e2e8f0;
                border-radius: 15px;
                padding: 20px;
                font-size: 18px;
                background-color: #f8fafc;
                color: #1e293b;
                font-weight: 500;
            }
            QLineEdit:focus {
                border-color: #10b981;
                background-color: white;
                box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1);
            }
            QLineEdit::placeholder {
                color: #94a3b8;
                font-style: italic;
            }
        """

    def _get_combo_style(self):
        """Estilo para ComboBox"""
        return """
            QComboBox {
                border: 3px solid #e2e8f0;
                border-radius: 15px;
                padding: 20px;
                font-size: 18px;
                background-color: #f8fafc;
                color: #1e293b;
                font-weight: 500;
            }
            QComboBox:focus {
                border-color: #10b981;
                background-color: white;
                box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1);
            }
            QComboBox::drop-down {
                border: none;
                background-color: #10b981;
                width: 35px;
                border-radius: 10px;
            }
            QComboBox::down-arrow {
                image: none;
                border: 3px solid white;
                width: 10px;
                height: 10px;
                border-top: none;
                border-right: none;
                transform: rotate(-45deg);
                margin-top: -7px;
            }
        """

    def handle_register(self):
        """Manejar registro"""
        email = self.email_input.text().strip()
        nombre = self.nombre_input.text().strip()
        apellido = self.apellido_input.text().strip()
        password = self.password_input.text()
        confirm_password = self.confirm_password_input.text()
        nivel_inicial = self.nivel_combo.currentText()

        if not all([email, nombre, apellido, password]):
            QMessageBox.warning(self, "Campos requeridos", "Complete todos los campos obligatorios")
            return

        if password != confirm_password:
            QMessageBox.warning(self, "Error", "Las contraseñas no coinciden")
            self.confirm_password_input.clear()
            return

        self.register_button.setEnabled(False)
        self.register_button.setText("Creando cuenta...")
        self.progress_bar.show()

        self.auth_worker = AuthWorker(
            "register",
            email=email,
            password=password,
            nombre=nombre,
            apellido=apellido,
            nivel_inicial=nivel_inicial
        )
        self.auth_worker.auth_completed.connect(self.on_register_completed)
        self.auth_worker.start()

    def on_register_completed(self, success: bool, message: str):
        """Resultado del registro"""
        self.register_button.setEnabled(True)
        self.register_button.setText("Crear Mi Cuenta")
        self.progress_bar.hide()

        if success:
            QMessageBox.information(self, "¡Éxito!", "Cuenta creada exitosamente.\nAhora puedes iniciar sesión.")
            self.register_success.emit()
        else:
            QMessageBox.warning(self, "Error", message)


class LoginWindow(QWidget):
    """Ventana principal de login en pantalla completa"""
    login_successful = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        """Configurar interfaz principal"""
        self.setWindowTitle("AlfaIA - Sistema de Autenticación")
        self.showMaximized()  # Pantalla completa

        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Stack para formularios
        self.stack = QStackedWidget()
        self.login_form = LoginForm()
        self.register_form = RegisterForm()

        self.stack.addWidget(self.login_form)
        self.stack.addWidget(self.register_form)

        # Conectar señales
        self.login_form.switch_to_register.connect(self.show_register)
        self.register_form.switch_to_login.connect(self.show_login)
        self.login_form.login_success.connect(self.on_login_success)
        self.register_form.register_success.connect(self.show_login)

        main_layout.addWidget(self.stack)

        # Mostrar login por defecto
        self.stack.setCurrentWidget(self.login_form)

    def show_login(self):
        """Mostrar formulario de login"""
        self.stack.setCurrentWidget(self.login_form)
        self.login_form.email_input.clear()
        self.login_form.password_input.clear()

    def show_register(self):
        """Mostrar formulario de registro"""
        self.stack.setCurrentWidget(self.register_form)
        # Limpiar campos
        for field in [self.register_form.email_input, self.register_form.nombre_input,
                      self.register_form.apellido_input, self.register_form.password_input,
                      self.register_form.confirm_password_input]:
            field.clear()

    def on_login_success(self):
        """Manejar login exitoso"""
        self.login_successful.emit()
        self.close()

    def keyPressEvent(self, event):
        """Manejar teclas especiales"""
        if event.key() == Qt.Key.Key_Escape:
            reply = QMessageBox.question(self, "Salir", "¿Desea salir de AlfaIA?")
            if reply == QMessageBox.StandardButton.Yes:
                self.close()
        else:
            super().keyPressEvent(event)


# =============================================================================
# CÓDIGO DE PRUEBA
# =============================================================================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec())
# =============================================================================
# AlfaIA/ui/windows/login_window.py - Ventana de Login y Registro
# =============================================================================

import sys
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QPushButton, QStackedWidget,
    QFrame, QCheckBox, QDateEdit, QComboBox,
    QMessageBox, QProgressBar, QTextEdit
)
from PyQt6.QtCore import Qt, QDate, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QPixmap, QPalette, QColor

# Agregar path para imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from config.settings import Settings
from core.auth.authentication import AuthenticationManager, ValidationError
from core.database.models import NivelUsuario


class AuthWorker(QThread):
    """Worker thread para operaciones de autenticación"""

    # Señales
    auth_completed = pyqtSignal(bool, str)

    def __init__(self, operation, **kwargs):
        super().__init__()
        self.operation = operation
        self.kwargs = kwargs
        self.auth_manager = AuthenticationManager()

    def run(self):
        """Ejecutar operación de autenticación en thread separado"""
        try:
            if self.operation == "login":
                success, message = self.auth_manager.login(
                    self.kwargs['email'],
                    self.kwargs['password']
                )
            elif self.operation == "register":
                success, message = self.auth_manager.register_user(**self.kwargs)
            else:
                success, message = False, "Operación no válida"

            self.auth_completed.emit(success, message)

        except Exception as e:
            self.auth_completed.emit(False, f"Error: {str(e)}")


class LoginForm(QWidget):
    """Formulario de inicio de sesión"""

    # Señales
    login_success = pyqtSignal()
    switch_to_register = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = Settings()
        self.auth_worker = None
        self.setup_ui()

    def setup_ui(self):
        """Configurar interfaz del formulario de login"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)

        # Título
        title = QLabel("Iniciar Sesión")
        title.setStyleSheet(f"""
            QLabel {{
                font-size: 28px;
                font-weight: bold;
                color: {self.settings.COLORS['blue_educational']};
                margin-bottom: 20px;
            }}
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Subtítulo
        subtitle = QLabel("Accede a tu cuenta de AlfaIA")
        subtitle.setStyleSheet(f"""
            QLabel {{
                font-size: 14px;
                color: {self.settings.COLORS['text_secondary']};
                margin-bottom: 30px;
            }}
        """)
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)

        # Formulario
        form_frame = QFrame()
        form_frame.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 2px solid {self.settings.COLORS['blue_light']};
                border-radius: 12px;
                padding: 30px;
            }}
        """)
        form_layout = QFormLayout(form_frame)
        form_layout.setSpacing(15)

        # Campo email
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("correo@ejemplo.com")
        self.email_input.setStyleSheet(self._get_input_style())
        form_layout.addRow("📧 Correo electrónico:", self.email_input)

        # Campo contraseña
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("••••••••")
        self.password_input.setStyleSheet(self._get_input_style())
        form_layout.addRow("🔒 Contraseña:", self.password_input)

        # Recordar sesión
        self.remember_checkbox = QCheckBox("Recordar mi sesión")
        self.remember_checkbox.setStyleSheet(f"""
            QCheckBox {{
                color: {self.settings.COLORS['text_secondary']};
                font-size: 12px;
            }}
        """)
        form_layout.addRow("", self.remember_checkbox)

        layout.addWidget(form_frame)

        # Barra de progreso (oculta inicialmente)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminado
        self.progress_bar.hide()
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: 2px solid {self.settings.COLORS['blue_light']};
                border-radius: 5px;
                text-align: center;
            }}
            QProgressBar::chunk {{
                background-color: {self.settings.COLORS['blue_educational']};
                border-radius: 3px;
            }}
        """)
        layout.addWidget(self.progress_bar)

        # Botón de login
        self.login_button = QPushButton("🚀 Iniciar Sesión")
        self.login_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.settings.COLORS['blue_educational']};
                color: white;
                border: none;
                border-radius: 10px;
                padding: 15px;
                font-size: 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {self.settings.COLORS['blue_educational']}DD;
            }}
            QPushButton:pressed {{
                background-color: {self.settings.COLORS['blue_educational']}BB;
            }}
            QPushButton:disabled {{
                background-color: {self.settings.COLORS['gray_neutral']};
            }}
        """)
        self.login_button.clicked.connect(self.handle_login)
        layout.addWidget(self.login_button)

        # Separador
        separator = QLabel("──────  o  ──────")
        separator.setStyleSheet(f"color: {self.settings.COLORS['gray_neutral']};")
        separator.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(separator)

        # Botón de registro
        register_button = QPushButton("✨ Crear Cuenta Nueva")
        register_button.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {self.settings.COLORS['blue_educational']};
                border: 2px solid {self.settings.COLORS['blue_educational']};
                border-radius: 10px;
                padding: 15px;
                font-size: 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {self.settings.COLORS['blue_light']};
            }}
        """)
        register_button.clicked.connect(self.switch_to_register.emit)
        layout.addWidget(register_button)

        # Conectar Enter key
        self.email_input.returnPressed.connect(self.handle_login)
        self.password_input.returnPressed.connect(self.handle_login)

    def _get_input_style(self) -> str:
        """Obtener estilo para campos de entrada"""
        return f"""
            QLineEdit {{
                border: 2px solid {self.settings.COLORS['blue_light']};
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
                background-color: white;
            }}
            QLineEdit:focus {{
                border-color: {self.settings.COLORS['blue_educational']};
            }}
        """

    def handle_login(self):
        """Manejar intento de inicio de sesión"""
        email = self.email_input.text().strip()
        password = self.password_input.text()

        # Validación básica
        if not email or not password:
            QMessageBox.warning(self, "Campos Requeridos",
                                "Por favor ingrese email y contraseña")
            return

        # Deshabilitar botón y mostrar progreso
        self.login_button.setEnabled(False)
        self.progress_bar.show()

        # Ejecutar login en thread separado
        self.auth_worker = AuthWorker("login", email=email, password=password)
        self.auth_worker.auth_completed.connect(self.on_login_completed)
        self.auth_worker.start()

    def on_login_completed(self, success: bool, message: str):
        """Manejar resultado del login"""
        # Restaurar UI
        self.login_button.setEnabled(True)
        self.progress_bar.hide()

        if success:
            # Login exitoso
            QMessageBox.information(self, "¡Bienvenido!",
                                    "Inicio de sesión exitoso")
            self.login_success.emit()
        else:
            # Error en login
            QMessageBox.warning(self, "Error de Inicio de Sesión", message)
            self.password_input.clear()
            self.password_input.setFocus()


class RegisterForm(QWidget):
    """Formulario de registro"""

    # Señales
    register_success = pyqtSignal()
    switch_to_login = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = Settings()
        self.auth_worker = None
        self.setup_ui()

    def setup_ui(self):
        """Configurar interfaz del formulario de registro"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(40, 20, 40, 20)

        # Título
        title = QLabel("Crear Cuenta")
        title.setStyleSheet(f"""
            QLabel {{
                font-size: 28px;
                font-weight: bold;
                color: {self.settings.COLORS['green_success']};
                margin-bottom: 10px;
            }}
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Subtítulo
        subtitle = QLabel("Únete a la comunidad de aprendizaje AlfaIA")
        subtitle.setStyleSheet(f"""
            QLabel {{
                font-size: 14px;
                color: {self.settings.COLORS['text_secondary']};
                margin-bottom: 20px;
            }}
        """)
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)

        # Formulario en frame con scroll
        form_frame = QFrame()
        form_frame.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 2px solid {self.settings.COLORS['green_mint']};
                border-radius: 12px;
                padding: 25px;
            }}
        """)
        form_layout = QFormLayout(form_frame)
        form_layout.setSpacing(12)

        # Campos del formulario
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("correo@ejemplo.com")
        self.email_input.setStyleSheet(self._get_input_style())
        form_layout.addRow("📧 Correo electrónico:", self.email_input)

        self.nombre_input = QLineEdit()
        self.nombre_input.setPlaceholderText("Tu nombre")
        self.nombre_input.setStyleSheet(self._get_input_style())
        form_layout.addRow("👤 Nombre:", self.nombre_input)

        self.apellido_input = QLineEdit()
        self.apellido_input.setPlaceholderText("Tu apellido")
        self.apellido_input.setStyleSheet(self._get_input_style())
        form_layout.addRow("👥 Apellido:", self.apellido_input)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Mínimo 8 caracteres")
        self.password_input.setStyleSheet(self._get_input_style())
        form_layout.addRow("🔒 Contraseña:", self.password_input)

        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_password_input.setPlaceholderText("Repetir contraseña")
        self.confirm_password_input.setStyleSheet(self._get_input_style())
        form_layout.addRow("🔐 Confirmar contraseña:", self.confirm_password_input)

        # Fecha de nacimiento (opcional)
        self.birth_date = QDateEdit()
        self.birth_date.setDate(QDate(2000, 1, 1))
        self.birth_date.setMaximumDate(QDate.currentDate())
        self.birth_date.setMinimumDate(QDate(1900, 1, 1))
        self.birth_date.setStyleSheet(self._get_input_style())
        form_layout.addRow("🎂 Fecha de nacimiento:", self.birth_date)

        # Nivel inicial
        self.nivel_combo = QComboBox()
        self.nivel_combo.addItems([nivel.value for nivel in NivelUsuario])
        self.nivel_combo.setStyleSheet(self._get_input_style())
        form_layout.addRow("📊 Nivel inicial:", self.nivel_combo)

        layout.addWidget(form_frame)

        # Información de seguridad
        security_info = QLabel(
            "🔐 La contraseña debe tener al menos 8 caracteres,\n"
            "incluir mayúsculas, minúsculas y números"
        )
        security_info.setStyleSheet(f"""
            QLabel {{
                color: {self.settings.COLORS['text_secondary']};
                font-size: 11px;
                background-color: {self.settings.COLORS['blue_light']};
                padding: 8px;
                border-radius: 5px;
            }}
        """)
        layout.addWidget(security_info)

        # Barra de progreso
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)
        self.progress_bar.hide()
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: 2px solid {self.settings.COLORS['green_mint']};
                border-radius: 5px;
                text-align: center;
            }}
            QProgressBar::chunk {{
                background-color: {self.settings.COLORS['green_success']};
                border-radius: 3px;
            }}
        """)
        layout.addWidget(self.progress_bar)

        # Botón de registro
        self.register_button = QPushButton("✨ Crear Mi Cuenta")
        self.register_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.settings.COLORS['green_success']};
                color: white;
                border: none;
                border-radius: 10px;
                padding: 15px;
                font-size: 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {self.settings.COLORS['green_success']}DD;
            }}
            QPushButton:pressed {{
                background-color: {self.settings.COLORS['green_success']}BB;
            }}
            QPushButton:disabled {{
                background-color: {self.settings.COLORS['gray_neutral']};
            }}
        """)
        self.register_button.clicked.connect(self.handle_register)
        layout.addWidget(self.register_button)

        # Separador
        separator = QLabel("──────  o  ──────")
        separator.setStyleSheet(f"color: {self.settings.COLORS['gray_neutral']};")
        separator.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(separator)

        # Botón volver al login
        back_button = QPushButton("🔙 Ya tengo cuenta")
        back_button.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {self.settings.COLORS['green_success']};
                border: 2px solid {self.settings.COLORS['green_success']};
                border-radius: 10px;
                padding: 15px;
                font-size: 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {self.settings.COLORS['green_mint']};
            }}
        """)
        back_button.clicked.connect(self.switch_to_login.emit)
        layout.addWidget(back_button)

    def _get_input_style(self) -> str:
        """Obtener estilo para campos de entrada"""
        return f"""
            QLineEdit, QDateEdit, QComboBox {{
                border: 2px solid {self.settings.COLORS['green_mint']};
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
                background-color: white;
            }}
            QLineEdit:focus, QDateEdit:focus, QComboBox:focus {{
                border-color: {self.settings.COLORS['green_success']};
            }}
        """

    def handle_register(self):
        """Manejar intento de registro"""
        # Obtener datos del formulario
        email = self.email_input.text().strip()
        nombre = self.nombre_input.text().strip()
        apellido = self.apellido_input.text().strip()
        password = self.password_input.text()
        confirm_password = self.confirm_password_input.text()
        fecha_nacimiento = self.birth_date.date().toString("yyyy-MM-dd")
        nivel_inicial = self.nivel_combo.currentText()

        # Validaciones básicas
        if not all([email, nombre, apellido, password]):
            QMessageBox.warning(self, "Campos Requeridos",
                                "Por favor complete todos los campos obligatorios")
            return

        if password != confirm_password:
            QMessageBox.warning(self, "Error de Contraseña",
                                "Las contraseñas no coinciden")
            self.confirm_password_input.clear()
            self.confirm_password_input.setFocus()
            return

        # Deshabilitar botón y mostrar progreso
        self.register_button.setEnabled(False)
        self.progress_bar.show()

        # Ejecutar registro en thread separado
        self.auth_worker = AuthWorker(
            "register",
            email=email,
            password=password,
            nombre=nombre,
            apellido=apellido,
            fecha_nacimiento=fecha_nacimiento,
            nivel_inicial=nivel_inicial
        )
        self.auth_worker.auth_completed.connect(self.on_register_completed)
        self.auth_worker.start()

    def on_register_completed(self, success: bool, message: str):
        """Manejar resultado del registro"""
        # Restaurar UI
        self.register_button.setEnabled(True)
        self.progress_bar.hide()

        if success:
            # Registro exitoso
            QMessageBox.information(
                self, "¡Cuenta Creada!",
                "Tu cuenta ha sido creada exitosamente.\n"
                "Ahora puedes iniciar sesión."
            )
            self.register_success.emit()
        else:
            # Error en registro
            QMessageBox.warning(self, "Error de Registro", message)


class LoginWindow(QWidget):
    """Ventana principal de login y registro"""

    # Señales
    login_successful = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.settings = Settings()
        self.setup_ui()

    def setup_ui(self):
        """Configurar interfaz principal"""
        # Configuración de ventana
        self.setWindowTitle(f"{self.settings.APP_NAME} - Iniciar Sesión")
        self.setFixedSize(500, 700)
        self.setStyleSheet(f"""
            QWidget {{
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 {self.settings.COLORS['blue_light']},
                    stop: 1 {self.settings.COLORS['white_pure']}
                );
                font-family: 'Segoe UI', 'Inter', 'Roboto', sans-serif;
            }}
        """)

        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Header con logo y branding
        self.create_header(main_layout)

        # Stack widget para cambiar entre login y registro
        self.stack = QStackedWidget()

        # Crear formularios
        self.login_form = LoginForm()
        self.register_form = RegisterForm()

        # Agregar formularios al stack
        self.stack.addWidget(self.login_form)
        self.stack.addWidget(self.register_form)

        # Conectar señales
        self.setup_connections()

        main_layout.addWidget(self.stack)

        # Footer
        self.create_footer(main_layout)

        # Mostrar formulario de login por defecto
        self.stack.setCurrentWidget(self.login_form)

    def create_header(self, layout):
        """Crear header con branding"""
        header_frame = QFrame()
        header_frame.setFixedHeight(120)
        header_frame.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 {self.settings.COLORS['blue_educational']},
                    stop: 1 {self.settings.COLORS['purple_creative']}
                );
                border: none;
            }}
        """)

        header_layout = QVBoxLayout(header_frame)
        header_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Logo/Título
        app_title = QLabel("🎓 AlfaIA")
        app_title.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 36px;
                font-weight: bold;
                margin: 0;
            }
        """)
        app_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(app_title)

        # Subtítulo
        app_subtitle = QLabel("Aprende español con inteligencia artificial")
        app_subtitle.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 14px;
                margin: 0;
                opacity: 0.9;
            }
        """)
        app_subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(app_subtitle)

        layout.addWidget(header_frame)

    def create_footer(self, layout):
        """Crear footer con información"""
        footer_frame = QFrame()
        footer_frame.setFixedHeight(60)
        footer_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {self.settings.COLORS['blue_light']};
                border-top: 1px solid {self.settings.COLORS['gray_neutral']};
            }}
        """)

        footer_layout = QVBoxLayout(footer_frame)
        footer_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Información de versión
        version_label = QLabel(f"Versión {self.settings.APP_VERSION}")
        version_label.setStyleSheet(f"""
            QLabel {{
                color: {self.settings.COLORS['text_secondary']};
                font-size: 12px;
            }}
        """)
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer_layout.addWidget(version_label)

        # Copyright
        copyright_label = QLabel("© 2024 AlfaIA - Todos los derechos reservados")
        copyright_label.setStyleSheet(f"""
            QLabel {{
                color: {self.settings.COLORS['text_secondary']};
                font-size: 10px;
            }}
        """)
        copyright_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer_layout.addWidget(copyright_label)

        layout.addWidget(footer_frame)

    def setup_connections(self):
        """Configurar conexiones entre señales"""
        # Cambios entre formularios
        self.login_form.switch_to_register.connect(self.show_register)
        self.register_form.switch_to_login.connect(self.show_login)

        # Login exitoso
        self.login_form.login_success.connect(self.on_login_success)

        # Registro exitoso (volver a login)
        self.register_form.register_success.connect(self.show_login)

    def show_login(self):
        """Mostrar formulario de login"""
        self.stack.setCurrentWidget(self.login_form)
        self.setWindowTitle(f"{self.settings.APP_NAME} - Iniciar Sesión")

        # Limpiar campos
        self.login_form.email_input.clear()
        self.login_form.password_input.clear()
        self.login_form.email_input.setFocus()

    def show_register(self):
        """Mostrar formulario de registro"""
        self.stack.setCurrentWidget(self.register_form)
        self.setWindowTitle(f"{self.settings.APP_NAME} - Crear Cuenta")

        # Limpiar campos
        self.register_form.email_input.clear()
        self.register_form.nombre_input.clear()
        self.register_form.apellido_input.clear()
        self.register_form.password_input.clear()
        self.register_form.confirm_password_input.clear()
        self.register_form.email_input.setFocus()

    def on_login_success(self):
        """Manejar login exitoso"""
        # Emitir señal para cerrar ventana de login
        self.login_successful.emit()
        self.close()

    def closeEvent(self, event):
        """Manejar cierre de ventana"""
        # No cerrar si hay workers activos
        if (hasattr(self.login_form, 'auth_worker') and
                self.login_form.auth_worker and
                self.login_form.auth_worker.isRunning()):
            event.ignore()
            return

        if (hasattr(self.register_form, 'auth_worker') and
                self.register_form.auth_worker and
                self.register_form.auth_worker.isRunning()):
            event.ignore()
            return

        event.accept()


# =============================================================================
# WIDGET DE DEMOSTRACIÓN STANDALONE
# =============================================================================

class LoginDemo(QWidget):
    """Demo standalone para probar el sistema de login"""

    def __init__(self):
        super().__init__()
        self.login_window = None
        self.setup_ui()

    def setup_ui(self):
        """Configurar demo"""
        self.setWindowTitle("AlfaIA - Demo Sistema de Login")
        self.setFixedSize(300, 150)

        layout = QVBoxLayout(self)

        title = QLabel("Demo Sistema de Autenticación")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin: 20px;")
        layout.addWidget(title)

        # Botón para abrir login
        open_login_btn = QPushButton("🔑 Abrir Ventana de Login")
        open_login_btn.setStyleSheet("""
            QPushButton {
                background-color: #4A90E2;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #4A90E2DD;
            }
        """)
        open_login_btn.clicked.connect(self.open_login_window)
        layout.addWidget(open_login_btn)

        # Botón para probar BD
        test_db_btn = QPushButton("🗄️ Probar Conexión BD")
        test_db_btn.setStyleSheet("""
            QPushButton {
                background-color: #7ED321;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7ED321DD;
            }
        """)
        test_db_btn.clicked.connect(self.test_database)
        layout.addWidget(test_db_btn)

    def open_login_window(self):
        """Abrir ventana de login"""
        if not self.login_window:
            self.login_window = LoginWindow()
            self.login_window.login_successful.connect(self.on_login_success)

        self.login_window.show()
        self.login_window.raise_()
        self.login_window.activateWindow()

    def test_database(self):
        """Probar conexión a base de datos"""
        try:
            from core.database.connection import DatabaseManager
            db_manager = DatabaseManager()

            if db_manager.test_connection():
                QMessageBox.information(self, "✅ Base de Datos",
                                        "Conexión exitosa a la base de datos")
            else:
                QMessageBox.warning(self, "❌ Base de Datos",
                                    "No se pudo conectar a la base de datos")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error probando BD: {str(e)}")

    def on_login_success(self):
        """Manejar login exitoso"""
        QMessageBox.information(self, "¡Login Exitoso!",
                                "Usuario autenticado correctamente.\n"
                                "En la aplicación real se abriría la ventana principal.")


# =============================================================================
# CÓDIGO DE PRUEBA
# =============================================================================

if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)

    # Usar demo standalone
    demo = LoginDemo()
    demo.show()

    sys.exit(app.exec())
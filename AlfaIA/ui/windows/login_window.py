# =============================================================================
# AlfaIA/ui/windows/login_window.py - Fix Definitivo Fullscreen
# =============================================================================

import sys
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QPushButton, QStackedWidget,
    QFrame, QCheckBox, QDateEdit, QComboBox,
    QMessageBox, QProgressBar, QApplication, QSizePolicy,
    QScrollArea, QSpacerItem
)
from PyQt6.QtCore import Qt, QDate, QThread, pyqtSignal, QTimer, QSize, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QPixmap, QPalette, QColor, QPainter, QBrush, QLinearGradient, QScreen

from AlfaIA.core.auth.authentication import get_auth_manager

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
        COLORS = {
            'blue_educational': '#4A90E2',
            'green_success': '#7ED321',
            'orange_energetic': '#F5A623',
            'purple_creative': '#9013FE',
            'text_primary': '#2C3E50',
            'text_secondary': '#7F8C8D'
        }


    class NivelUsuario:
        @classmethod
        def __iter__(cls):
            return iter([cls()])

        def __init__(self):
            self.value = "Principiante"


class ResponsiveFrame(QFrame):
    """Frame que se adapta responsivamente al tamaño de la ventana"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ResponsiveFrame")

    def resizeEvent(self, event):
        """Manejar redimensionamiento responsivo"""
        super().resizeEvent(event)
        # Ajustar márgenes según el tamaño de la ventana
        width = self.width()
        height = self.height()

        # Calcular márgenes responsivos
        margin_h = max(50, min(200, width * 0.1))
        margin_v = max(30, min(100, height * 0.05))

        # Aplicar márgenes al layout si existe
        if self.layout():
            self.layout().setContentsMargins(int(margin_h), int(margin_v), int(margin_h), int(margin_v))


class AuthWorker(QThread):
    """Worker thread para operaciones de autenticación - SIN DEADLOCK"""
    auth_completed = pyqtSignal(bool, str, object)

    def __init__(self, operation, **kwargs):
        super().__init__()
        self.operation = operation
        self.kwargs = kwargs

    def run(self):
        """Ejecutar operación de autenticación - VERSIÓN SIN DEADLOCK"""
        try:
            from core.auth.authentication import get_auth_manager

            auth_manager = get_auth_manager()

            print(f"🔧 AuthWorker ejecutando operación: {self.operation}")
            print(f"🔍 AuthManager ID en worker: {id(auth_manager)}")

            if self.operation == "login":
                success, message = auth_manager.login(
                    self.kwargs['email'],
                    self.kwargs['password']
                )

                # Si el login fue exitoso, obtener el usuario de forma segura
                user = None
                if success:
                    print("✅ Login exitoso en AuthWorker, obteniendo usuario...")

                    # DEBUG sin lock para evitar deadlock
                    auth_manager.debug_status_no_lock()

                    # Usar método seguro para obtener usuario
                    user = auth_manager.get_current_user_safe()

                    if user:
                        print(f"✅ Usuario obtenido en AuthWorker: {user.email}")
                    else:
                        print("⚠️ Usuario no obtenido, pero login exitoso")
                        # Intentar una vez más después de un pequeño delay
                        import time
                        time.sleep(0.1)
                        user = auth_manager.get_current_user_safe()
                        if user:
                            print(f"✅ Usuario obtenido en segundo intento: {user.email}")

                print(f"🎯 Emitiendo señal: success={success}, user={'Sí' if user else 'No'}")
                self.auth_completed.emit(success, message, user)

            elif self.operation == "register":
                success, message = auth_manager.register_user(**self.kwargs)
                self.auth_completed.emit(success, message, None)
            else:
                self.auth_completed.emit(False, "Operación no válida", None)

        except Exception as e:
            print(f"❌ Error en AuthWorker: {e}")
            import traceback
            traceback.print_exc()
            self.auth_completed.emit(False, f"Error: {str(e)}", None)

        finally:
            print("🏁 AuthWorker terminado")


class LoginForm(QWidget):
    """Formulario de inicio de sesión optimizado y responsive"""
    login_success = pyqtSignal()
    switch_to_register = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = Settings()
        self.auth_worker = None
        self.setup_ui()

    def setup_ui(self):
        """Configurar interfaz del formulario de login"""
        # Layout principal horizontal con stretch factors apropiados
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Panel izquierdo - Información (40% del ancho)
        left_panel = self.create_info_panel()
        main_layout.addWidget(left_panel, 2)  # Factor 2

        # Panel derecho - Formulario (60% del ancho)
        right_panel = self.create_form_panel()
        main_layout.addWidget(right_panel, 3)  # Factor 3

    def create_info_panel(self):
        """Crear panel informativo izquierdo mejorado"""
        panel = ResponsiveFrame()
        panel.setStyleSheet(f"""
            ResponsiveFrame {{
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 {self.settings.COLORS['blue_educational']},
                    stop: 0.3 #5ba3f5,
                    stop: 0.7 #7c3aed,
                    stop: 1 {self.settings.COLORS['purple_creative']}
                );
                border: none;
            }}
        """)

        layout = QVBoxLayout(panel)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(30)

        # Espaciador superior
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # Logo grande con mejor proporción
        logo = QLabel("🎓")
        logo.setStyleSheet("""
            QLabel {
                font-size: 96px;
                color: white;
                margin: 0;
                padding: 20px;
            }
        """)
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        layout.addWidget(logo)

        # Título principal con mejor espaciado
        title = QLabel("AlfaIA")
        title.setStyleSheet(f"""
            QLabel {{
                font-size: 56px;
                font-weight: bold;
                color: white;
                margin: 10px 0;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
                font-family: 'Segoe UI', 'Arial', sans-serif;
            }}
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        layout.addWidget(title)

        # Subtítulo con mejor line-height
        subtitle = QLabel("Aprende español con\ninteligencia artificial")
        subtitle.setStyleSheet("""
            QLabel {
                font-size: 20px;
                color: white;
                text-align: center;
                line-height: 1.6;
                margin: 15px 20px;
                text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
                font-weight: 300;
            }
        """)
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)

        # Espaciador medio
        layout.addSpacerItem(QSpacerItem(20, 30, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed))

        # Características con mejor formato
        features = QLabel(
            "✨ Ejercicios interactivos\n🎮 Juegos educativos\n📊 Progreso personalizado\n🧠 Análisis inteligente")
        features.setStyleSheet("""
            QLabel {
                font-size: 16px;
                color: white;
                text-align: center;
                line-height: 2.2;
                margin: 20px 30px;
                text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
                font-weight: 400;
            }
        """)
        features.setAlignment(Qt.AlignmentFlag.AlignCenter)
        features.setWordWrap(True)
        layout.addWidget(features)

        # Espaciador inferior
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        return panel

    def create_form_panel(self):
        """Crear panel de formulario derecho mejorado"""
        panel = ResponsiveFrame()
        panel.setStyleSheet("""
            ResponsiveFrame {
                background-color: #f8fafc;
                border: none;
            }
        """)

        # Scroll area para contenido que puede ser largo
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")

        # Widget contenedor del scroll
        scroll_widget = QWidget()
        scroll_area.setWidget(scroll_widget)

        # Layout principal del panel
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(0, 0, 0, 0)
        panel_layout.addWidget(scroll_area)

        # Layout del contenido scrolleable
        main_layout = QVBoxLayout(scroll_widget)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Espaciador superior
        main_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # Contenedor del formulario con tamaño fijo pero responsivo
        form_container = QFrame()
        form_container.setObjectName("FormContainer")
        form_container.setFixedWidth(480)  # Ancho fijo para consistencia
        form_container.setStyleSheet("""
            QFrame#FormContainer {
                background-color: white;
                border-radius: 20px;
                padding: 40px;
                border: 1px solid #e2e8f0;
                box-shadow: 0 10px 25px rgba(0,0,0,0.1);
            }
        """)

        form_layout = QVBoxLayout(form_container)
        form_layout.setSpacing(25)

        # Título del formulario con mejor espaciado
        form_title = QLabel("Iniciar Sesión")
        form_title.setStyleSheet(f"""
            QLabel {{
                font-size: 36px;
                font-weight: bold;
                color: {self.settings.COLORS['text_primary']};
                text-align: center;
                margin-bottom: 20px;
                font-family: 'Segoe UI', 'Arial', sans-serif;
            }}
        """)
        form_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        form_layout.addWidget(form_title)

        # Función helper para campos con mejor UX
        def create_field_group(label_text, placeholder, is_password=False):
            # Container del grupo
            group = QWidget()
            group_layout = QVBoxLayout(group)
            group_layout.setContentsMargins(0, 0, 0, 0)
            group_layout.setSpacing(8)

            # Label
            label = QLabel(label_text)
            label.setStyleSheet(f"""
                QLabel {{
                    font-size: 16px;
                    font-weight: 600;
                    color: {self.settings.COLORS['text_primary']};
                    margin-bottom: 5px;
                }}
            """)
            group_layout.addWidget(label)

            # Input
            field = QLineEdit()
            field.setPlaceholderText(placeholder)
            if is_password:
                field.setEchoMode(QLineEdit.EchoMode.Password)
            field.setStyleSheet(self._get_input_style())
            field.setFixedHeight(55)
            group_layout.addWidget(field)

            return group, field

        # Crear campos de entrada
        email_group, self.email_input = create_field_group("Correo Electrónico", "tu@email.com")
        form_layout.addWidget(email_group)

        password_group, self.password_input = create_field_group("Contraseña", "••••••••••", True)
        form_layout.addWidget(password_group)

        # Espaciado extra
        form_layout.addSpacing(15)

        # Barra de progreso mejorada
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)
        self.progress_bar.hide()
        self.progress_bar.setFixedHeight(4)
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: none;
                border-radius: 2px;
                background-color: #e2e8f0;
            }}
            QProgressBar::chunk {{
                background-color: {self.settings.COLORS['blue_educational']};
                border-radius: 2px;
            }}
        """)
        form_layout.addWidget(self.progress_bar)

        # Botón de login mejorado
        self.login_button = QPushButton("Iniciar Sesión")
        self.login_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.settings.COLORS['blue_educational']};
                color: white;
                border: none;
                border-radius: 12px;
                padding: 16px 20px;
                font-size: 18px;
                font-weight: 600;
                font-family: 'Segoe UI', 'Arial', sans-serif;
            }}
            QPushButton:hover {{
                background-color: #3a7bd5;
                transform: translateY(-1px);
            }}
            QPushButton:pressed {{
                background-color: #2563eb;
                transform: translateY(0px);
            }}
            QPushButton:disabled {{
                background-color: #94a3b8;
            }}
        """)
        self.login_button.setFixedHeight(60)
        self.login_button.clicked.connect(self.handle_login)
        form_layout.addWidget(self.login_button)

        # Separador más elegante
        separator_widget = self.create_elegant_separator()
        form_layout.addWidget(separator_widget)

        # Botón crear cuenta mejorado
        register_button = QPushButton("Crear Cuenta Nueva")
        register_button.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {self.settings.COLORS['blue_educational']};
                border: 2px solid {self.settings.COLORS['blue_educational']};
                border-radius: 12px;
                padding: 16px 20px;
                font-size: 18px;
                font-weight: 600;
                font-family: 'Segoe UI', 'Arial', sans-serif;
            }}
            QPushButton:hover {{
                background-color: {self.settings.COLORS['blue_educational']};
                color: white;
                transform: translateY(-1px);
            }}
            QPushButton:pressed {{
                transform: translateY(0px);
            }}
        """)
        register_button.setFixedHeight(60)
        register_button.clicked.connect(self.switch_to_register.emit)
        form_layout.addWidget(register_button)

        # Centrar el form container
        main_layout.addWidget(form_container, 0, Qt.AlignmentFlag.AlignCenter)

        # Espaciador inferior
        main_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # Conectar Enter para mejor UX
        self.email_input.returnPressed.connect(self.password_input.setFocus)
        self.password_input.returnPressed.connect(self.handle_login)

        return panel

    def create_elegant_separator(self):
        """Crear separador elegante"""
        separator_widget = QWidget()
        separator_layout = QHBoxLayout(separator_widget)
        separator_layout.setContentsMargins(0, 20, 0, 20)

        # Línea izquierda
        line1 = QFrame()
        line1.setFrameShape(QFrame.Shape.HLine)
        line1.setStyleSheet("QFrame { color: #cbd5e1; background-color: #cbd5e1; height: 1px; }")

        # Texto central
        or_label = QLabel("o")
        or_label.setStyleSheet("""
            QLabel { 
                color: #64748b; 
                font-size: 14px; 
                font-weight: 500;
                margin: 0 20px;
                background-color: white;
                padding: 0 10px;
            }
        """)

        # Línea derecha
        line2 = QFrame()
        line2.setFrameShape(QFrame.Shape.HLine)
        line2.setStyleSheet("QFrame { color: #cbd5e1; background-color: #cbd5e1; height: 1px; }")

        separator_layout.addWidget(line1)
        separator_layout.addWidget(or_label, 0, Qt.AlignmentFlag.AlignCenter)
        separator_layout.addWidget(line2)

        return separator_widget

    def _get_input_style(self):
        """Estilo para campos de entrada mejorado"""
        return f"""
            QLineEdit {{
                border: 2px solid #e2e8f0;
                border-radius: 12px;
                padding: 16px 20px;
                font-size: 16px;
                background-color: #f8fafc;
                color: {self.settings.COLORS['text_primary']};
                font-weight: 400;
                font-family: 'Segoe UI', 'Arial', sans-serif;
            }}
            QLineEdit:focus {{
                border-color: {self.settings.COLORS['blue_educational']};
                background-color: white;
                box-shadow: 0 0 0 3px rgba(74, 144, 226, 0.1);
            }}
            QLineEdit::placeholder {{
                color: #94a3b8;
                font-style: normal;
            }}
        """

    def handle_login(self):
        """Manejar login con validación mejorada"""
        email = self.email_input.text().strip()
        password = self.password_input.text()

        # Validación de campos
        if not email:
            self.show_field_error(self.email_input, "El email es requerido")
            return

        if not password:
            self.show_field_error(self.password_input, "La contraseña es requerida")
            return

        # Validación básica de email
        if "@" not in email or "." not in email:
            self.show_field_error(self.email_input, "Formato de email inválido")
            return

        # Deshabilitar UI y mostrar progreso
        self.set_loading_state(True)

        self.auth_worker = AuthWorker("login", email=email, password=password)
        self.auth_worker.auth_completed.connect(self.on_login_completed)
        self.auth_worker.start()

    def show_field_error(self, field, message):
        """Mostrar error en campo específico"""
        field.setStyleSheet(self._get_input_style().replace("#e2e8f0", "#ff6b6b"))
        field.setFocus()
        QMessageBox.warning(self, "Error de validación", message)
        # Restaurar estilo después de 3 segundos
        QTimer.singleShot(3000, lambda: field.setStyleSheet(self._get_input_style()))

    def set_loading_state(self, loading):
        """Configurar estado de carga"""
        self.login_button.setEnabled(not loading)
        self.email_input.setEnabled(not loading)
        self.password_input.setEnabled(not loading)

        if loading:
            self.login_button.setText("Iniciando...")
            self.progress_bar.show()
        else:
            self.login_button.setText("Iniciar Sesión")
            self.progress_bar.hide()

    def on_login_completed(self, success: bool, message: str):
        """Resultado del login con mejor UX"""
        self.set_loading_state(False)

        if success:
            # Mostrar brevemente éxito antes de continuar
            self.login_button.setText("¡Éxito!")
            self.login_button.setStyleSheet(self.login_button.styleSheet().replace(
                self.settings.COLORS['blue_educational'], self.settings.COLORS['green_success']
            ))
            QTimer.singleShot(800, self.login_success.emit)
        else:
            QMessageBox.warning(self, "Error de inicio de sesión", message)
            self.password_input.clear()
            self.password_input.setFocus()


class RegisterForm(QWidget):
    """Formulario de registro mejorado y responsive"""
    register_success = pyqtSignal()
    switch_to_login = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = Settings()
        self.auth_worker = None
        self.setup_ui()

    def setup_ui(self):
        """Configurar interfaz del formulario de registro"""
        # Layout principal horizontal
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Panel izquierdo - Formulario (60%)
        left_panel = self.create_form_panel()
        main_layout.addWidget(left_panel, 3)

        # Panel derecho - Información (40%)
        right_panel = self.create_info_panel()
        main_layout.addWidget(right_panel, 2)

    def create_info_panel(self):
        """Crear panel informativo derecho"""
        panel = ResponsiveFrame()
        panel.setStyleSheet(f"""
            ResponsiveFrame {{
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 {self.settings.COLORS['green_success']},
                    stop: 0.3 #34d399,
                    stop: 0.7 #10b981,
                    stop: 1 #059669
                );
                border: none;
            }}
        """)

        layout = QVBoxLayout(panel)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(30)

        # Espaciador superior
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # Logo
        logo = QLabel("✨")
        logo.setStyleSheet("""
            QLabel {
                font-size: 96px;
                color: white;
                margin: 0;
                padding: 20px;
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
                margin: 10px 0;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
                font-family: 'Segoe UI', 'Arial', sans-serif;
            }
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Texto motivacional
        motivational_text = QLabel("Comienza tu viaje de\naprendizaje del español\ncon inteligencia artificial")
        motivational_text.setStyleSheet("""
            QLabel {
                font-size: 20px;
                color: white;
                text-align: center;
                line-height: 1.6;
                margin: 15px 20px;
                text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
                font-weight: 300;
            }
        """)
        motivational_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        motivational_text.setWordWrap(True)
        layout.addWidget(motivational_text)

        # Espaciador inferior
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        return panel

    def create_form_panel(self):
        """Crear panel de formulario izquierdo mejorado"""
        panel = ResponsiveFrame()
        panel.setStyleSheet("""
            ResponsiveFrame {
                background-color: #f8fafc;
                border: none;
            }
        """)

        # Scroll area para el formulario
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")

        scroll_widget = QWidget()
        scroll_area.setWidget(scroll_widget)

        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(0, 0, 0, 0)
        panel_layout.addWidget(scroll_area)

        main_layout = QVBoxLayout(scroll_widget)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Espaciador superior
        main_layout.addSpacerItem(QSpacerItem(20, 30, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # Contenedor del formulario
        form_container = QFrame()
        form_container.setFixedWidth(520)
        form_container.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 20px;
                padding: 40px;
                border: 1px solid #e2e8f0;
                box-shadow: 0 10px 25px rgba(0,0,0,0.1);
            }
        """)

        form_layout = QVBoxLayout(form_container)
        form_layout.setSpacing(20)

        # Título del formulario
        form_title = QLabel("Crear Cuenta")
        form_title.setStyleSheet(f"""
            QLabel {{
                font-size: 36px;
                font-weight: bold;
                color: {self.settings.COLORS['text_primary']};
                text-align: center;
                margin-bottom: 15px;
                font-family: 'Segoe UI', 'Arial', sans-serif;
            }}
        """)
        form_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        form_layout.addWidget(form_title)

        # Función helper para campos
        def create_field_group(label_text, placeholder, is_password=False, is_combo=False):
            group = QWidget()
            group_layout = QVBoxLayout(group)
            group_layout.setContentsMargins(0, 0, 0, 0)
            group_layout.setSpacing(6)

            label = QLabel(label_text)
            label.setStyleSheet(f"""
                QLabel {{
                    font-size: 14px;
                    font-weight: 600;
                    color: {self.settings.COLORS['text_primary']};
                    margin-bottom: 3px;
                }}
            """)
            group_layout.addWidget(label)

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

            field.setFixedHeight(50)
            group_layout.addWidget(field)
            return group, field

        # Crear campos con espaciado optimizado
        email_group, self.email_input = create_field_group("Correo Electrónico", "tu@email.com")
        form_layout.addWidget(email_group)

        # Layout de nombre y apellido en fila
        name_layout = QHBoxLayout()
        name_layout.setSpacing(15)

        nombre_group, self.nombre_input = create_field_group("Nombre", "Tu nombre")
        apellido_group, self.apellido_input = create_field_group("Apellido", "Tu apellido")

        name_layout.addWidget(nombre_group)
        name_layout.addWidget(apellido_group)
        form_layout.addLayout(name_layout)

        password_group, self.password_input = create_field_group("Contraseña", "Mínimo 8 caracteres", is_password=True)
        form_layout.addWidget(password_group)

        confirm_password_group, self.confirm_password_input = create_field_group("Confirmar Contraseña",
                                                                                 "Repetir contraseña", is_password=True)
        form_layout.addWidget(confirm_password_group)

        nivel_group, self.nivel_combo = create_field_group("Nivel Inicial", "", is_combo=True)
        form_layout.addWidget(nivel_group)

        # Espaciado extra
        form_layout.addSpacing(10)

        # Barra de progreso
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)
        self.progress_bar.hide()
        self.progress_bar.setFixedHeight(4)
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: none;
                border-radius: 2px;
                background-color: #e2e8f0;
            }}
            QProgressBar::chunk {{
                background-color: {self.settings.COLORS['green_success']};
                border-radius: 2px;
            }}
        """)
        form_layout.addWidget(self.progress_bar)

        # Botón crear cuenta
        self.register_button = QPushButton("Crear Mi Cuenta")
        self.register_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.settings.COLORS['green_success']};
                color: white;
                border: none;
                border-radius: 12px;
                padding: 16px 20px;
                font-size: 18px;
                font-weight: 600;
                font-family: 'Segoe UI', 'Arial', sans-serif;
            }}
            QPushButton:hover {{
                background-color: #22c55e;
                transform: translateY(-1px);
            }}
            QPushButton:pressed {{
                background-color: #16a34a;
                transform: translateY(0px);
            }}
            QPushButton:disabled {{
                background-color: #94a3b8;
            }}
        """)
        self.register_button.setFixedHeight(60)
        self.register_button.clicked.connect(self.handle_register)
        form_layout.addWidget(self.register_button)

        # Espaciado
        form_layout.addSpacing(10)

        # Botón volver
        back_button = QPushButton("Ya tengo cuenta")
        back_button.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {self.settings.COLORS['green_success']};
                border: 2px solid {self.settings.COLORS['green_success']};
                border-radius: 12px;
                padding: 16px 20px;
                font-size: 18px;
                font-weight: 600;
                font-family: 'Segoe UI', 'Arial', sans-serif;
            }}
            QPushButton:hover {{
                background-color: {self.settings.COLORS['green_success']};
                color: white;
                transform: translateY(-1px);
            }}
            QPushButton:pressed {{
                transform: translateY(0px);
            }}
        """)
        back_button.setFixedHeight(60)
        back_button.clicked.connect(self.switch_to_login.emit)
        form_layout.addWidget(back_button)

        # Centrar el form container
        main_layout.addWidget(form_container, 0, Qt.AlignmentFlag.AlignCenter)

        # Espaciador inferior
        main_layout.addSpacerItem(QSpacerItem(20, 30, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        return panel

    def _get_input_style(self):
        """Estilo para campos de entrada"""
        return f"""
            QLineEdit {{
                border: 2px solid #e2e8f0;
                border-radius: 12px;
                padding: 14px 16px;
                font-size: 16px;
                background-color: #f8fafc;
                color: {self.settings.COLORS['text_primary']};
                font-weight: 400;
                font-family: 'Segoe UI', 'Arial', sans-serif;
            }}
            QLineEdit:focus {{
                border-color: {self.settings.COLORS['green_success']};
                background-color: white;
                box-shadow: 0 0 0 3px rgba(126, 211, 33, 0.1);
            }}
            QLineEdit::placeholder {{
                color: #94a3b8;
                font-style: normal;
            }}
        """

    def _get_combo_style(self):
        """Estilo para ComboBox"""
        return f"""
            QComboBox {{
                border: 2px solid #e2e8f0;
                border-radius: 12px;
                padding: 14px 16px;
                font-size: 16px;
                background-color: #f8fafc;
                color: {self.settings.COLORS['text_primary']};
                font-weight: 400;
                font-family: 'Segoe UI', 'Arial', sans-serif;
            }}
            QComboBox:focus {{
                border-color: {self.settings.COLORS['green_success']};
                background-color: white;
                box-shadow: 0 0 0 3px rgba(126, 211, 33, 0.1);
            }}
            QComboBox::drop-down {{
                border: none;
                background-color: {self.settings.COLORS['green_success']};
                width: 30px;
                border-radius: 8px;
                margin: 4px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border: 2px solid white;
                width: 8px;
                height: 8px;
                border-top: none;
                border-right: none;
                transform: rotate(-45deg);
                margin-top: -6px;
            }}
            QComboBox QAbstractItemView {{
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                background-color: white;
                selection-background-color: {self.settings.COLORS['green_success']};
                padding: 4px;
            }}
        """

    def handle_register(self):
        """Manejar registro con validación completa"""
        email = self.email_input.text().strip()
        nombre = self.nombre_input.text().strip()
        apellido = self.apellido_input.text().strip()
        password = self.password_input.text()
        confirm_password = self.confirm_password_input.text()
        nivel_inicial = self.nivel_combo.currentText()

        # Validaciones paso a paso
        if not email:
            self.show_field_error(self.email_input, "El email es requerido")
            return

        if "@" not in email or "." not in email:
            self.show_field_error(self.email_input, "Formato de email inválido")
            return

        if not nombre:
            self.show_field_error(self.nombre_input, "El nombre es requerido")
            return

        if not apellido:
            self.show_field_error(self.apellido_input, "El apellido es requerido")
            return

        if len(password) < 8:
            self.show_field_error(self.password_input, "La contraseña debe tener al menos 8 caracteres")
            return

        if password != confirm_password:
            self.show_field_error(self.confirm_password_input, "Las contraseñas no coinciden")
            return

        # Deshabilitar UI y mostrar progreso
        self.set_loading_state(True)

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

    def show_field_error(self, field, message):
        """Mostrar error en campo específico"""
        field.setStyleSheet(self._get_input_style().replace("#e2e8f0", "#ff6b6b"))
        field.setFocus()
        QMessageBox.warning(self, "Error de validación", message)
        QTimer.singleShot(3000, lambda: field.setStyleSheet(self._get_input_style()))

    def set_loading_state(self, loading):
        """Configurar estado de carga"""
        self.register_button.setEnabled(not loading)
        for field in [self.email_input, self.nombre_input, self.apellido_input,
                      self.password_input, self.confirm_password_input]:
            field.setEnabled(not loading)

        if loading:
            self.register_button.setText("Creando cuenta...")
            self.progress_bar.show()
        else:
            self.register_button.setText("Crear Mi Cuenta")
            self.progress_bar.hide()

    def on_register_completed(self, success: bool, message: str):
        """Resultado del registro"""
        self.set_loading_state(False)

        if success:
            self.register_button.setText("¡Cuenta creada!")
            self.register_button.setStyleSheet(self.register_button.styleSheet().replace(
                self.settings.COLORS['green_success'], self.settings.COLORS['blue_educational']
            ))
            QMessageBox.information(self, "¡Éxito!", "Cuenta creada exitosamente.\nAhora puedes iniciar sesión.")
            QTimer.singleShot(1000, self.register_success.emit)
        else:
            QMessageBox.warning(self, "Error en el registro", message)


class LoginWindow(QWidget):
    """Ventana principal de login - TAMAÑO COMPLETO IGUAL AL MAIN WINDOW"""
    login_successful = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.settings = Settings()
        self.is_fullscreen_ready = False
        self.setup_ui()
        # CONFIGURAR MISMO TAMAÑO QUE MAIN WINDOW
        self.configure_fullscreen_like_main()

    def configure_fullscreen_like_main(self):
        """Configurar login window del mismo tamaño que main window"""
        print("🔧 Configurando login window a tamaño completo...")

        # Paso 1: Obtener geometría de pantalla
        screen = QApplication.primaryScreen()
        if screen:
            screen_geometry = screen.availableGeometry()
            print(f"📐 Resolución detectada: {screen_geometry.width()}x{screen_geometry.height()}")

            # Establecer tamaño mínimo igual al main window (1200x800)
            self.setMinimumSize(1200, 800)

            # Establecer tamaño inicial EXACTO de la pantalla
            self.resize(screen_geometry.width(), screen_geometry.height())

            # Mover a posición (0,0) para cobertura completa
            self.move(screen_geometry.x(), screen_geometry.y())

        # Paso 2: Configurar propiedades de ventana
        self.setWindowState(Qt.WindowState.WindowNoState)

        # Paso 3: Programar secuencia para tamaño completo
        QTimer.singleShot(50, self.prepare_fullsize)
        QTimer.singleShot(150, self.apply_fullsize)
        QTimer.singleShot(300, self.verify_fullsize)

    def prepare_fullsize(self):
        """Paso 1: Preparar para tamaño completo"""
        print("📋 Preparando login para tamaño completo...")
        self.show()
        self.activateWindow()
        self.raise_()

    def apply_fullsize(self):
        """Paso 2: Aplicar tamaño completo"""
        print("🖥️ Aplicando tamaño completo al login...")
        # Maximizar como el main window
        self.setWindowState(Qt.WindowState.WindowMaximized)
        self.repaint()
        QApplication.processEvents()

    def verify_fullsize(self):
        """Paso 3: Verificar tamaño completo"""
        print("✅ Verificando tamaño completo del login...")

        screen = QApplication.primaryScreen()
        if screen:
            screen_geometry = screen.availableGeometry()
            current_geometry = self.geometry()

            print(f"🎯 Pantalla: {screen_geometry.width()}x{screen_geometry.height()}")
            print(f"🎯 Login Window: {current_geometry.width()}x{current_geometry.height()}")

            # Si no coincide, forzar tamaño correcto
            tolerance = 50
            if (abs(current_geometry.width() - screen_geometry.width()) > tolerance or
                    abs(current_geometry.height() - screen_geometry.height()) > tolerance):
                print("⚠️ Corrigiendo tamaño del login window...")
                self.setGeometry(screen_geometry)

        self.is_fullscreen_ready = True
        self.force_layout_refresh()
        print("🎉 Login window configurado a tamaño completo!")

    def force_layout_refresh(self):
        """Forzar actualización del layout"""
        print("🔄 Refrescando layouts del login...")

        if hasattr(self, 'stack'):
            current_widget = self.stack.currentWidget()
            if current_widget:
                current_widget.adjustSize()
                current_widget.updateGeometry()

        self.adjustSize()
        self.updateGeometry()
        self.update()
        QApplication.processEvents()

    def setup_ui(self):
        """Configurar interfaz principal - SIN CAMBIOS"""
        self.setWindowTitle("AlfaIA - Sistema de Autenticación")

        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Stack para formularios
        self.stack = QStackedWidget()
        self.stack.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

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

        # Aplicar estilos globales mejorados
        self.setStyleSheet("""
            QWidget {
                font-family: 'Segoe UI', 'Arial', sans-serif;
            }
            QMessageBox {
                font-size: 14px;
                min-width: 300px;
            }
            QMessageBox QPushButton {
                min-width: 80px;
                padding: 8px 16px;
            }
            QScrollBar:vertical {
                background-color: #f1f5f9;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background-color: #cbd5e1;
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #94a3b8;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
        """)

    def show_login(self):
        """Mostrar formulario de login"""
        print("🔑 Mostrando formulario de login")
        self.stack.setCurrentWidget(self.login_form)
        # Limpiar campos
        self.login_form.email_input.clear()
        self.login_form.password_input.clear()
        self.login_form.email_input.setFocus()

    def show_register(self):
        """Mostrar formulario de registro"""
        print("📝 Mostrando formulario de registro")
        self.stack.setCurrentWidget(self.register_form)
        # Limpiar campos
        for field in [self.register_form.email_input, self.register_form.nombre_input,
                      self.register_form.apellido_input, self.register_form.password_input,
                      self.register_form.confirm_password_input]:
            field.clear()
        self.register_form.email_input.setFocus()

    def on_login_success(self):
        """Manejar login exitoso"""
        print("✅ Login exitoso!")
        self.login_successful.emit()

    def resizeEvent(self, event):
        """Manejar redimensionamiento de ventana mejorado"""
        super().resizeEvent(event)

        # Solo procesar si fullscreen está listo
        if hasattr(self, 'is_fullscreen_ready') and self.is_fullscreen_ready:
            # Asegurar que el contenido se ajuste correctamente
            if hasattr(self, 'stack'):
                QTimer.singleShot(50, self.stack.adjustSize)

    def showEvent(self, event):
        """Manejar evento de mostrar ventana"""
        super().showEvent(event)
        print("👁️  Ventana mostrada")

    def keyPressEvent(self, event):
        """Manejar teclas especiales mejorado"""
        if event.key() == Qt.Key.Key_Escape:
            reply = QMessageBox.question(
                self,
                "Salir de AlfaIA",
                "¿Estás seguro de que quieres salir?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                print("👋 Usuario confirma salida")
                self.close()
        elif event.key() == Qt.Key.Key_F11:
            # Toggle fullscreen con F11
            print("🔄 Toggle fullscreen con F11")
            if self.isMaximized():
                self.showNormal()
            else:
                self.showMaximized()
        elif event.key() == Qt.Key.Key_F5:
            # Refresh layout con F5 (para debugging)
            print("🔄 Refrescando layout con F5")
            self.force_layout_refresh()
        else:
            super().keyPressEvent(event)

    def closeEvent(self, event):
        """Manejar cierre de ventana con cleanup"""
        print("🧹 Limpiando recursos antes de cerrar...")

        # Cleanup workers
        if hasattr(self.login_form, 'auth_worker') and self.login_form.auth_worker:
            if self.login_form.auth_worker.isRunning():
                self.login_form.auth_worker.terminate()
                self.login_form.auth_worker.wait(1000)  # Wait max 1 second

        if hasattr(self.register_form, 'auth_worker') and self.register_form.auth_worker:
            if self.register_form.auth_worker.isRunning():
                self.register_form.auth_worker.terminate()
                self.register_form.auth_worker.wait(1000)

        print("✅ Cleanup completado")
        event.accept()


# =============================================================================
# CÓDIGO DE PRUEBA Y DEBUGGING
# =============================================================================
if __name__ == "__main__":
    print("=" * 60)
    print("🚀 INICIANDO ALFAIA LOGIN WINDOW")
    print("=" * 60)

    app = QApplication(sys.argv)

    # Configurar aplicación
    app.setApplicationName("AlfaIA")
    app.setOrganizationName("AlfaIA")

    # Información de debugging
    screen = app.primaryScreen()
    if screen:
        geometry = screen.availableGeometry()
        print(f"🖥️  Resolución: {geometry.width()}x{geometry.height()}")
        print(f"📐 DPI: {screen.logicalDotsPerInch()}")

    # Crear y mostrar ventana
    print("🏗️  Creando ventana de login...")
    window = LoginWindow()

    print("👁️  Mostrando ventana...")
    window.show()  # El fullscreen se maneja automáticamente

    # Configurar cierre limpio
    app.aboutToQuit.connect(lambda: print("🏁 Cerrando aplicación de login"))

    print("🔄 Iniciando loop de eventos...")
    exit_code = app.exec()
    print(f"🏁 Aplicación terminada con código: {exit_code}")

    sys.exit(exit_code)
# =============================================================================
# AlfaIA/ui/windows/main_window.py - Ventana Principal Corregida y Completa
# =============================================================================

import sys
from pathlib import Path
from datetime import datetime
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QFrame, QStackedWidget, QTreeWidget,
    QTreeWidgetItem, QScrollArea, QSizePolicy, QSpacerItem,
    QMenuBar, QMenu, QToolBar, QStatusBar, QMessageBox,
    QSplitter, QGraphicsDropShadowEffect, QProgressBar
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QSize, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QColor, QPalette, QIcon, QAction

# Agregar path para imports
sys.path.append(str(Path(__file__).parent.parent.parent))

try:
    from config.settings import Settings
    from core.auth.authentication import auth_manager
    from core.database.models import PerfilUsuario

    print("✅ Imports de MainWindow exitosos")
except ImportError as e:
    print(f"⚠️ Error en imports de MainWindow: {e}")


    class Settings:
        APP_NAME = "AlfaIA"
        COLORS = {
            'blue_educational': '#4A90E2',
            'green_success': '#7ED321',
            'orange_energetic': '#F5A623',
            'purple_creative': '#9013FE',
            'text_primary': '#2C3E50',
            'text_secondary': '#7F8C8D',
            'gray_neutral': '#8E9AAF',
            'blue_light': '#E8F4FD',
            'white_pure': '#FFFFFF'
        }


class UserDataManager:
    """Gestor de datos del usuario para MainWindow"""

    def __init__(self, user):
        self.user = user
        self.profile = None
        print(f"🔧 Inicializando UserDataManager para: {type(user)}")

        # Validar usuario antes de continuar
        if not self._validate_user():
            print("⚠️ Usuario inválido, usando datos por defecto")
            return

        # Cargar perfil de forma segura
        self._safe_load_profile()

    def _validate_user(self):
        """Validar que el objeto usuario tenga los atributos mínimos"""
        if not self.user:
            return False

        required_attrs = ['nombre', 'email']
        for attr in required_attrs:
            if not hasattr(self.user, attr):
                print(f"❌ Usuario falta atributo: {attr}")
                return False

        return True

    def _safe_load_profile(self):
        """Cargar perfil de forma segura"""
        try:
            if hasattr(self.user, 'id') and self.user.id:
                print(f"🔍 Cargando perfil para user_id: {self.user.id}")
                self.profile = PerfilUsuario.find_by_user_id(self.user.id)
                if self.profile:
                    print("✅ Perfil cargado desde BD")
                else:
                    print("⚠️ No se encontró perfil, usando valores por defecto")
        except Exception as e:
            print(f"❌ Error cargando perfil: {e}")
            self.profile = None

    def get_display_name(self):
        """Nombre completo para mostrar"""
        if hasattr(self.user, 'nombre') and hasattr(self.user, 'apellido'):
            return f"{self.user.nombre} {self.user.apellido}"
        return "Usuario"

    def get_first_name(self):
        """Solo el nombre"""
        if hasattr(self.user, 'nombre'):
            return self.user.nombre
        return "Usuario"

    def get_email(self):
        """Email del usuario"""
        if hasattr(self.user, 'email'):
            return self.user.email
        return "demo@alfaia.com"

    def get_level(self):
        """Nivel actual del usuario"""
        if self.profile and hasattr(self.profile, 'nivel_lectura'):
            return f"Nivel {self.profile.nivel_lectura}"
        elif hasattr(self.user, 'nivel_inicial'):
            if hasattr(self.user.nivel_inicial, 'value'):
                return self.user.nivel_inicial.value
            return str(self.user.nivel_inicial)
        return "Principiante"

    def get_daily_goal(self):
        """Meta diaria de ejercicios"""
        if self.profile and hasattr(self.profile, 'objetivo_diario_ejercicios'):
            return self.profile.objetivo_diario_ejercicios
        return 5

    def get_total_points(self):
        """Puntos totales"""
        if self.profile and hasattr(self.profile, 'puntos_totales'):
            return self.profile.puntos_totales
        return 0

    def get_streak(self):
        """Racha de días consecutivos"""
        if self.profile and hasattr(self.profile, 'racha_dias_consecutivos'):
            return self.profile.racha_dias_consecutivos
        return 0

    def get_completed_exercises(self):
        """Ejercicios completados"""
        if self.profile and hasattr(self.profile, 'ejercicios_completados'):
            return self.profile.ejercicios_completados
        return 0

    def get_study_time(self):
        """Tiempo de estudio en minutos"""
        if self.profile and hasattr(self.profile, 'tiempo_total_minutos'):
            return self.profile.tiempo_total_minutos
        return 0


class ModernSidebar(QTreeWidget):
    """Barra lateral moderna con navegación"""
    section_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = Settings()
        self.setup_ui()
        self.populate_items()

    def setup_ui(self):
        """Configurar interfaz de la sidebar"""
        self.setHeaderHidden(True)
        self.setRootIsDecorated(False)
        self.setIndentation(0)
        self.setFixedWidth(280)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Estilo corregido con colores visibles
        self.setStyleSheet(f"""
            QTreeWidget {{
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #f8fafc,
                    stop: 0.5 #f1f5f9,
                    stop: 1 #e2e8f0
                );
                border: none;
                border-right: 1px solid #e2e8f0;
                font-family: 'Segoe UI', 'Arial', sans-serif;
                outline: none;
            }}

            QTreeWidget::item {{
                padding: 16px 20px;
                border: none;
                margin: 6px 12px;
                border-radius: 12px;
                background-color: transparent;
                font-weight: 500;
                font-size: 15px;
                color: {self.settings.COLORS['text_primary']};
                min-height: 20px;
            }}

            QTreeWidget::item:selected {{
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 {self.settings.COLORS['blue_educational']},
                    stop: 1 #5ba3f5
                );
                color: {self.settings.COLORS['white_pure']};
                border: none;
                font-weight: 600;
            }}

            QTreeWidget::item:hover:!selected {{
                background-color: {self.settings.COLORS['blue_educational']}15;
                color: {self.settings.COLORS['blue_educational']};
                border: 1px solid {self.settings.COLORS['blue_educational']}30;
            }}
        """)

    def populate_items(self):
        """Poblar elementos de navegación"""
        sections = [
            ("🏠", "Dashboard", "dashboard", "Resumen general de tu progreso"),
            ("📚", "Ejercicios", "exercises", "Practica gramática y vocabulario"),
            ("🎮", "Juegos", "games", "Aprende jugando y divirtiéndote"),
            ("📊", "Mi Progreso", "progress", "Analiza tu evolución y estadísticas"),
            ("🏆", "Logros", "achievements", "Tus logros y recompensas obtenidas"),
            ("👤", "Mi Perfil", "profile", "Información personal y configuración"),
            ("⚙️", "Configuración", "settings", "Ajustes de la aplicación")
        ]

        for icon, text, key, tooltip in sections:
            item = QTreeWidgetItem(self)
            item.setText(0, f"  {icon}   {text}")
            item.setData(0, Qt.ItemDataRole.UserRole, key)
            item.setToolTip(0, tooltip)

        # Conectar señal
        self.itemClicked.connect(self.on_item_clicked)

        # Seleccionar dashboard por defecto
        if self.topLevelItemCount() > 0:
            self.setCurrentItem(self.topLevelItem(0))

    def on_item_clicked(self, item, column):
        """Manejar clic en elemento"""
        section_key = item.data(0, Qt.ItemDataRole.UserRole)
        if section_key:
            self.section_changed.emit(section_key)


class StatsCard(QFrame):
    """Tarjeta de estadística moderna"""

    def __init__(self, title, value, icon, color, description="", parent=None):
        super().__init__(parent)
        self.settings = Settings()
        self.setup_ui(title, value, icon, color, description)

    def setup_ui(self, title, value, icon, color, description):
        """Configurar interfaz de la tarjeta"""
        self.setFixedHeight(130)

        # Frame con estilo corregido
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {self.settings.COLORS['white_pure']};
                border: 1px solid #e2e8f0;
                border-radius: 16px;
                padding: 0px;
            }}
            QFrame:hover {{
                border: 2px solid {color}40;
                background-color: #fafbfc;
            }}
        """)

        # Sombra
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 20))
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)

        # Layout principal
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(8)

        # Header con icono y valor
        header_layout = QHBoxLayout()

        # Icono
        icon_label = QLabel(icon)
        icon_label.setStyleSheet(f"""
            QLabel {{
                font-size: 28px;
                color: {color};
                background-color: {color}15;
                border-radius: 10px;
                padding: 8px;
                min-width: 44px;
                max-width: 44px;
                min-height: 44px;
                max-height: 44px;
                border: none;
            }}
        """)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(icon_label)

        header_layout.addStretch()

        # Valor
        value_label = QLabel(str(value))
        value_label.setStyleSheet(f"""
            QLabel {{
                font-size: 24px;
                font-weight: bold;
                color: {color};
                background-color: transparent;
                border: none;
            }}
        """)
        value_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)
        header_layout.addWidget(value_label)

        layout.addLayout(header_layout)

        # Título
        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            QLabel {{
                font-size: 14px;
                font-weight: 600;
                color: {self.settings.COLORS['text_primary']};
                background-color: transparent;
                border: none;
            }}
        """)
        layout.addWidget(title_label)

        # Descripción
        if description:
            desc_label = QLabel(description)
            desc_label.setStyleSheet(f"""
                QLabel {{
                    font-size: 11px;
                    color: {self.settings.COLORS['text_secondary']};
                    background-color: transparent;
                    border: none;
                }}
            """)
            desc_label.setWordWrap(True)
            layout.addWidget(desc_label)

        layout.addStretch()


class DashboardWidget(QWidget):
    """Widget del dashboard principal"""

    def __init__(self, user_data, parent=None):
        super().__init__(parent)
        self.settings = Settings()
        self.user_data = user_data
        self.setup_ui()

    def setup_ui(self):
        """Configurar interfaz del dashboard"""
        # Scroll area principal
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("QScrollArea { border: none; background-color: #f8fafc; }")

        # Widget de contenido
        content_widget = QWidget()
        scroll_area.setWidget(content_widget)

        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll_area)

        # Layout del contenido
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(30)
        content_layout.setContentsMargins(40, 30, 40, 30)

        # Header con saludo
        header = self.create_header()
        content_layout.addWidget(header)

        # Panel de estadísticas
        stats_panel = self.create_stats_panel()
        content_layout.addWidget(stats_panel)

        # Panel de actividad reciente
        activity_panel = self.create_activity_panel()
        content_layout.addWidget(activity_panel)

        # Panel de acciones rápidas
        actions_panel = self.create_actions_panel()
        content_layout.addWidget(actions_panel)

        # Espaciador final
        content_layout.addStretch()

    def create_header(self):
        """Crear header con saludo personalizado"""
        header = QFrame()
        header.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 {self.settings.COLORS['blue_educational']},
                    stop: 0.5 #5ba3f5,
                    stop: 1 {self.settings.COLORS['purple_creative']}
                );
                border-radius: 20px;
                padding: 0px;
                border: none;
            }}
        """)

        # Sombra
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 30))
        shadow.setOffset(0, 4)
        header.setGraphicsEffect(shadow)

        layout = QVBoxLayout(header)
        layout.setContentsMargins(30, 25, 30, 25)
        layout.setSpacing(12)

        # Saludo principal
        greeting = QLabel(f"¡Hola, {self.user_data.get_first_name()}! 👋")
        greeting.setStyleSheet("""
            QLabel {
                font-size: 32px;
                font-weight: bold;
                color: white;
                background-color: transparent;
                border: none;
            }
        """)
        layout.addWidget(greeting)

        # Mensaje motivacional
        message = QLabel("¡Continúa tu viaje de aprendizaje con AlfaIA!")
        message.setStyleSheet("""
            QLabel {
                font-size: 16px;
                color: white;
                background-color: transparent;
                border: none;
                font-weight: 300;
            }
        """)
        layout.addWidget(message)

        return header

    def create_stats_panel(self):
        """Crear panel de estadísticas"""
        panel = QFrame()
        panel.setStyleSheet("QFrame { background-color: transparent; border: none; }")

        layout = QVBoxLayout(panel)
        layout.setSpacing(20)

        # Título
        title = QLabel("📊 Tu Progreso")
        title.setStyleSheet(f"""
            QLabel {{
                font-size: 22px;
                font-weight: bold;
                color: {self.settings.COLORS['text_primary']};
                background-color: transparent;
                border: none;
                margin-bottom: 10px;
            }}
        """)
        layout.addWidget(title)

        # Grid de estadísticas
        stats_grid = QGridLayout()
        stats_grid.setSpacing(20)

        # Datos de estadísticas del usuario
        stats_data = [
            ("Nivel Actual", self.user_data.get_level(), "🎓", self.settings.COLORS['blue_educational'],
             "Tu nivel de español"),
            ("Meta Diaria", f"0 / {self.user_data.get_daily_goal()}", "📝", self.settings.COLORS['green_success'],
             "Ejercicios por día"),
            ("Racha", f"{self.user_data.get_streak()} días", "🔥", self.settings.COLORS['orange_energetic'],
             "Días consecutivos"),
            ("Puntos", f"{self.user_data.get_total_points()}", "⭐", "#FFD700", "Puntos acumulados"),
            ("Ejercicios", f"{self.user_data.get_completed_exercises()}", "🏆", self.settings.COLORS['purple_creative'],
             "Completados"),
            ("Tiempo", f"{self.user_data.get_study_time()} min", "⏱️", "#FF6B6B", "Tiempo de estudio")
        ]

        for i, (title, value, icon, color, desc) in enumerate(stats_data):
            card = StatsCard(title, value, icon, color, desc)
            row = i // 3
            col = i % 3
            stats_grid.addWidget(card, row, col)

        layout.addLayout(stats_grid)
        return panel

    def create_activity_panel(self):
        """Crear panel de actividad reciente"""
        panel = QFrame()
        panel.setStyleSheet(f"""
            QFrame {{
                background-color: {self.settings.COLORS['white_pure']};
                border: 1px solid #e2e8f0;
                border-radius: 16px;
                padding: 0px;
            }}
        """)

        # Sombra
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(12)
        shadow.setColor(QColor(0, 0, 0, 15))
        shadow.setOffset(0, 2)
        panel.setGraphicsEffect(shadow)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)

        # Título
        title = QLabel("📈 Actividad Reciente")
        title.setStyleSheet(f"""
            QLabel {{
                font-size: 18px;
                font-weight: bold;
                color: {self.settings.COLORS['text_primary']};
                background-color: transparent;
                border: none;
            }}
        """)
        layout.addWidget(title)

        # Actividades
        activities = [
            ("Hoy", f"¡Bienvenido {self.user_data.get_first_name()}!", "Has iniciado sesión en AlfaIA", "🎉"),
            ("Próximo", "Primer ejercicio", "Completa tu primer ejercicio de gramática", "📚"),
            ("Recomendado", "Explora juegos", "Diviértete mientras aprendes español", "🎮")
        ]

        for time, title_act, desc, icon in activities:
            activity_item = self.create_activity_item(time, title_act, desc, icon)
            layout.addWidget(activity_item)

        return panel

    def create_activity_item(self, time, title, description, icon):
        """Crear item individual de actividad"""
        item = QFrame()
        item.setStyleSheet(f"""
            QFrame {{
                background-color: {self.settings.COLORS['blue_light']};
                border: none;
                border-radius: 12px;
                padding: 0px;
                border-left: 4px solid {self.settings.COLORS['blue_educational']};
            }}
            QFrame:hover {{
                background-color: {self.settings.COLORS['blue_educational']}10;
            }}
        """)

        layout = QHBoxLayout(item)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(16)

        # Icono
        icon_label = QLabel(icon)
        icon_label.setStyleSheet(f"""
            QLabel {{
                font-size: 20px;
                background-color: {self.settings.COLORS['blue_educational']};
                color: white;
                border-radius: 18px;
                padding: 6px;
                min-width: 36px;
                max-width: 36px;
                min-height: 36px;
                max-height: 36px;
                border: none;
            }}
        """)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon_label)

        # Contenido
        content_layout = QVBoxLayout()
        content_layout.setSpacing(4)

        # Header con título y tiempo
        header_layout = QHBoxLayout()

        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            QLabel {{
                font-size: 14px;
                font-weight: 600;
                color: {self.settings.COLORS['text_primary']};
                background-color: transparent;
                border: none;
            }}
        """)
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        time_label = QLabel(time)
        time_label.setStyleSheet(f"""
            QLabel {{
                font-size: 11px;
                color: {self.settings.COLORS['text_secondary']};
                background-color: {self.settings.COLORS['blue_educational']}20;
                padding: 3px 8px;
                border-radius: 6px;
                border: none;
            }}
        """)
        header_layout.addWidget(time_label)

        content_layout.addLayout(header_layout)

        # Descripción
        desc_label = QLabel(description)
        desc_label.setStyleSheet(f"""
            QLabel {{
                font-size: 12px;
                color: {self.settings.COLORS['text_secondary']};
                background-color: transparent;
                border: none;
            }}
        """)
        desc_label.setWordWrap(True)
        content_layout.addWidget(desc_label)

        layout.addLayout(content_layout)
        return item

    def create_actions_panel(self):
        """Crear panel de acciones rápidas"""
        panel = QFrame()
        panel.setStyleSheet(f"""
            QFrame {{
                background-color: {self.settings.COLORS['white_pure']};
                border: 1px solid #e2e8f0;
                border-radius: 16px;
                padding: 0px;
            }}
        """)

        # Sombra
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(12)
        shadow.setColor(QColor(0, 0, 0, 15))
        shadow.setOffset(0, 2)
        panel.setGraphicsEffect(shadow)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(20)

        # Título
        title = QLabel("🚀 Acciones Rápidas")
        title.setStyleSheet(f"""
            QLabel {{
                font-size: 18px;
                font-weight: bold;
                color: {self.settings.COLORS['text_primary']};
                background-color: transparent;
                border: none;
            }}
        """)
        layout.addWidget(title)

        # Grid de botones
        buttons_grid = QGridLayout()
        buttons_grid.setSpacing(16)

        # Acciones disponibles
        actions = [
            ("📝 Comenzar Ejercicio", "Practica gramática", self.settings.COLORS['blue_educational']),
            ("🎮 Jugar Ahora", "Aprende jugando", self.settings.COLORS['purple_creative']),
            ("📊 Ver Progreso", "Analiza tu evolución", self.settings.COLORS['green_success']),
            ("🏆 Mis Logros", "Revisa logros", "#FFD700"),
            ("⚙️ Configuración", "Personaliza", self.settings.COLORS['gray_neutral']),
            ("❓ Ayuda", "Obtén soporte", "#FF6B6B")
        ]

        for i, (text, desc, color) in enumerate(actions):
            button = self.create_action_button(text, desc, color)
            row = i // 2
            col = i % 2
            buttons_grid.addWidget(button, row, col)

        layout.addLayout(buttons_grid)
        return panel

    def create_action_button(self, text, description, color):
        """Crear botón de acción"""
        button = QPushButton()
        button.setFixedHeight(70)
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {color}10;
                color: {color};
                border: 2px solid {color}30;
                border-radius: 12px;
                padding: 12px 16px;
                font-size: 14px;
                font-weight: 600;
                text-align: left;
                font-family: 'Segoe UI', 'Arial', sans-serif;
            }}
            QPushButton:hover {{
                background-color: {color};
                color: white;
                border: 2px solid {color};
            }}
            QPushButton:pressed {{
                background-color: {color}CC;
            }}
        """)

        button.setText(f"{text}\n{description}")
        return button


class PlaceholderWidget(QWidget):
    """Widget placeholder para módulos futuros"""

    def __init__(self, section_name, user_data, parent=None):
        super().__init__(parent)
        self.section_name = section_name
        self.user_data = user_data
        self.settings = Settings()
        self.setup_ui()

    def setup_ui(self):
        """Configurar interfaz del placeholder"""
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(30)

        # Icono grande
        icons = {
            'exercises': '📚',
            'games': '🎮',
            'progress': '📊',
            'achievements': '🏆',
            'profile': '👤',
            'settings': '⚙️'
        }

        icon = QLabel(icons.get(self.section_name, '🔧'))
        icon.setStyleSheet("""
            QLabel {
                font-size: 120px;
                color: #cbd5e1;
                background-color: transparent;
                border: none;
            }
        """)
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon)

        # Título
        titles = {
            'exercises': 'Módulo de Ejercicios',
            'games': 'Módulo de Juegos',
            'progress': 'Análisis de Progreso',
            'achievements': 'Sistema de Logros',
            'profile': 'Perfil de Usuario',
            'settings': 'Configuración'
        }

        title = QLabel(titles.get(self.section_name, 'Módulo en Desarrollo'))
        title.setStyleSheet(f"""
            QLabel {{
                font-size: 28px;
                font-weight: bold;
                color: {self.settings.COLORS['text_primary']};
                background-color: transparent;
                border: none;
            }}
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Descripción
        descriptions = {
            'exercises': 'Aquí podrás practicar gramática, vocabulario y comprensión lectora con ejercicios interactivos.',
            'games': 'Diviértete mientras aprendes con juegos educativos como crucigramas y sopas de letras.',
            'progress': 'Analiza tu evolución, ve gráficas de tu progreso y obtén recomendaciones personalizadas.',
            'achievements': 'Desbloquea logros, ve tu racha de días consecutivos y gana puntos por tus actividades.',
            'profile': 'Configura tu perfil personal, ajusta tu nivel y personaliza tu experiencia de aprendizaje.',
            'settings': 'Ajusta las preferencias de la aplicación, temas visuales y configuraciones de NLP.'
        }

        desc = QLabel(descriptions.get(self.section_name, 'Este módulo estará disponible próximamente.'))
        desc.setStyleSheet(f"""
            QLabel {{
                font-size: 16px;
                color: {self.settings.COLORS['text_secondary']};
                background-color: transparent;
                border: none;
                max-width: 500px;
            }}
        """)
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setWordWrap(True)
        layout.addWidget(desc)

        # Estado
        status = QLabel("🚧 En desarrollo")
        status.setStyleSheet(f"""
            QLabel {{
                font-size: 14px;
                color: {self.settings.COLORS['orange_energetic']};
                background-color: {self.settings.COLORS['orange_energetic']}15;
                border: 2px solid {self.settings.COLORS['orange_energetic']}30;
                border-radius: 20px;
                padding: 8px 16px;
            }}
        """)
        status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(status)


class MainWindow(QMainWindow):
    """Ventana principal de AlfaIA - Corregida y completa"""

    def __init__(self, user_data=None):
        super().__init__()

        print(f"🏗️ Inicializando MainWindow con usuario: {type(user_data)}")

        try:
            self.settings = Settings()
            print("✅ Settings cargado")
        except Exception as e:
            print(f"❌ Error cargando Settings: {e}")
            # Crear settings básico como fallback
            self.settings = self._create_basic_settings()

        try:
            # Crear UserDataManager de forma segura
            if user_data:
                self.user_data_manager = UserDataManager(user_data)
                print(f"✅ UserDataManager creado para: {self.user_data_manager.get_display_name()}")
            else:
                print("⚠️ No se recibió user_data, creando manager demo")
                self.user_data_manager = self._create_demo_manager()
        except Exception as e:
            print(f"❌ Error creando UserDataManager: {e}")
            print("🔄 Creando manager demo como fallback")
            self.user_data_manager = self._create_demo_manager()

        self.current_section = "dashboard"

        try:
            self.setup_ui()
            self.setup_menu_bar()
            self.setup_tool_bar()
            self.setup_status_bar()
            print("✅ MainWindow configurado exitosamente")
        except Exception as e:
            print(f"❌ Error configurando MainWindow: {e}")
            self._setup_error_ui()

    def _create_basic_settings(self):
        """Crear configuración básica como fallback"""

        class BasicSettings:
            APP_NAME = "AlfaIA"
            COLORS = {
                'blue_educational': '#4A90E2',
                'green_success': '#7ED321',
                'orange_energetic': '#F5A623',
                'purple_creative': '#9013FE',
                'text_primary': '#2C3E50',
                'text_secondary': '#7F8C8D',
                'gray_neutral': '#8E9AAF',
                'blue_light': '#E8F4FD',
                'white_pure': '#FFFFFF',
                'background_primary': '#FFFFFF',
                'background_secondary': '#F9FAFB'
            }

        return BasicSettings()

    def _create_demo_manager(self):
        """Crear UserDataManager demo como fallback"""

        class DemoUser:
            def __init__(self):
                self.id = 999
                self.nombre = "Usuario"
                self.apellido = "Demo"
                self.email = "demo@alfaia.com"
                self.nivel_inicial = "Principiante"

        return UserDataManager(DemoUser())

    def _setup_error_ui(self):
        """Configurar UI básica en caso de error"""
        self.setWindowTitle("AlfaIA - Error")
        self.setMinimumSize(800, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        error_label = QLabel("❌ Error cargando la interfaz principal\n\nPor favor, verifica la instalación de AlfaIA")
        error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        error_label.setStyleSheet("font-size: 18px; color: #DC2626; padding: 40px;")

        layout.addWidget(error_label)

    def setup_ui(self):
        """Configurar interfaz principal"""
        self.setWindowTitle(
            f"{self.settings.APP_NAME} - {self.user_data_manager.get_display_name() if self.user_data_manager else 'Usuario'}")
        self.setMinimumSize(1200, 800)

        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layout principal horizontal
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Sidebar de navegación
        self.sidebar = ModernSidebar()
        self.sidebar.section_changed.connect(self.change_section)
        main_layout.addWidget(self.sidebar)

        # Área de contenido principal
        self.content_stack = QStackedWidget()
        self.content_stack.setStyleSheet("QStackedWidget { background-color: #f8fafc; }")
        main_layout.addWidget(self.content_stack)

        # Crear widgets para cada sección
        self.create_content_widgets()

        # Aplicar estilo global
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {self.settings.COLORS['white_pure']};
                color: {self.settings.COLORS['text_primary']};
            }}
        """)

    def create_content_widgets(self):
        """Crear widgets de contenido para cada sección"""
        # Dashboard principal
        if self.user_data_manager:
            dashboard = DashboardWidget(self.user_data_manager)
        else:
            dashboard = PlaceholderWidget("dashboard", None)

        self.content_stack.addWidget(dashboard)

        # Placeholders para módulos futuros
        modules = ['exercises', 'games', 'progress', 'achievements', 'profile', 'settings']
        for module in modules:
            placeholder = PlaceholderWidget(module, self.user_data_manager)
            self.content_stack.addWidget(placeholder)

    def setup_menu_bar(self):
        """Configurar barra de menú"""
        menubar = self.menuBar()
        menubar.setStyleSheet(f"""
            QMenuBar {{
                background-color: {self.settings.COLORS['white_pure']};
                color: {self.settings.COLORS['text_primary']};
                border-bottom: 1px solid #e2e8f0;
                padding: 4px 8px;
                font-size: 14px;
            }}
            QMenuBar::item {{
                background-color: transparent;
                padding: 8px 12px;
                border-radius: 6px;
            }}
            QMenuBar::item:selected {{
                background-color: {self.settings.COLORS['blue_educational']}15;
                color: {self.settings.COLORS['blue_educational']};
            }}
            QMenu {{
                background-color: {self.settings.COLORS['white_pure']};
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 8px;
            }}
            QMenu::item {{
                padding: 8px 16px;
                border-radius: 6px;
            }}
            QMenu::item:selected {{
                background-color: {self.settings.COLORS['blue_educational']};
                color: white;
            }}
        """)

        # Menú Archivo
        file_menu = menubar.addMenu('&Archivo')

        # Acción Cerrar Sesión
        logout_action = QAction('🚪 Cerrar Sesión', self)
        logout_action.setShortcut('Ctrl+Q')
        logout_action.triggered.connect(self.logout)
        file_menu.addAction(logout_action)

        file_menu.addSeparator()

        # Acción Salir
        exit_action = QAction('❌ Salir', self)
        exit_action.setShortcut('Alt+F4')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Menú Ayuda
        help_menu = menubar.addMenu('&Ayuda')

        about_action = QAction('ℹ️ Acerca de AlfaIA', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def setup_tool_bar(self):
        """Configurar barra de herramientas"""
        toolbar = self.addToolBar('Principal')
        toolbar.setMovable(False)
        toolbar.setStyleSheet(f"""
            QToolBar {{
                background-color: {self.settings.COLORS['white_pure']};
                border: none;
                border-bottom: 1px solid #e2e8f0;
                padding: 8px;
                spacing: 8px;
            }}
            QToolButton {{
                background-color: transparent;
                border: none;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 14px;
                color: {self.settings.COLORS['text_primary']};
            }}
            QToolButton:hover {{
                background-color: {self.settings.COLORS['blue_educational']}15;
                color: {self.settings.COLORS['blue_educational']};
            }}
        """)

        # Acciones de la toolbar
        dashboard_action = QAction('🏠 Dashboard', self)
        dashboard_action.triggered.connect(lambda: self.change_section('dashboard'))
        toolbar.addAction(dashboard_action)

        toolbar.addSeparator()

        exercises_action = QAction('📚 Ejercicios', self)
        exercises_action.triggered.connect(lambda: self.change_section('exercises'))
        toolbar.addAction(exercises_action)

        games_action = QAction('🎮 Juegos', self)
        games_action.triggered.connect(lambda: self.change_section('games'))
        toolbar.addAction(games_action)

    def setup_status_bar(self):
        """Configurar barra de estado"""
        status = self.statusBar()
        status.setStyleSheet(f"""
            QStatusBar {{
                background-color: {self.settings.COLORS['white_pure']};
                color: {self.settings.COLORS['text_secondary']};
                border-top: 1px solid #e2e8f0;
                padding: 4px 8px;
                font-size: 12px;
            }}
        """)

        # Información del usuario
        if self.user_data_manager:
            user_info = f"👤 {self.user_data_manager.get_display_name()}"
            goal_info = f"🎯 Meta diaria: 0/{self.user_data_manager.get_daily_goal()}"
        else:
            user_info = "👤 Usuario Demo"
            goal_info = "🎯 Meta diaria: 0/5"

        status.showMessage(f"{user_info}  |  {goal_info}  |  📡 Conectado")

    def change_section(self, section_key):
        """Cambiar sección activa"""
        section_mapping = {
            'dashboard': 0,
            'exercises': 1,
            'games': 2,
            'progress': 3,
            'achievements': 4,
            'profile': 5,
            'settings': 6
        }

        if section_key in section_mapping:
            self.current_section = section_key
            self.content_stack.setCurrentIndex(section_mapping[section_key])
            print(f"🔄 Cambiando a sección: {section_key}")
        else:
            print(f"⚠️ Sección desconocida: {section_key}")

    def logout(self):
        """Cerrar sesión del usuario"""
        reply = QMessageBox.question(
            self,
            "Cerrar Sesión",
            "¿Estás seguro de que quieres cerrar sesión?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            print("🚪 Cerrando sesión...")

            # Logout del auth_manager
            auth_manager.logout()

            # Cerrar ventana principal
            self.close()

            # Mostrar ventana de login nuevamente
            try:
                from ui.windows.login_window import LoginWindow
                login_window = LoginWindow()
                login_window.show()
                print("✅ Ventana de login mostrada")
            except Exception as e:
                print(f"❌ Error mostrando login: {e}")

    def show_about(self):
        """Mostrar información acerca de la aplicación"""
        QMessageBox.about(
            self,
            "Acerca de AlfaIA",
            f"""
            <h2>{self.settings.APP_NAME}</h2>
            <p><b>Versión:</b> 1.0.0</p>
            <p><b>Descripción:</b> Aplicación educativa para aprendizaje de español con inteligencia artificial.</p>
            <p><b>Desarrollado con:</b> PyQt6 y NLP</p>
            <hr>
            <p>© 2024 AlfaIA - Todos los derechos reservados</p>
            """
        )

    def closeEvent(self, event):
        """Manejar cierre de ventana"""
        reply = QMessageBox.question(
            self,
            "Salir de AlfaIA",
            "¿Estás seguro de que quieres salir de la aplicación?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            print("👋 Cerrando AlfaIA...")
            auth_manager.logout()
            event.accept()
        else:
            event.ignore()


# =============================================================================
# TESTING Y DEBUGGING
# =============================================================================
if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    import sys

    print("🧪 Probando MainWindow...")

    app = QApplication(sys.argv)


    # Crear usuario demo para pruebas
    class DemoUser:
        def __init__(self):
            self.id = 1
            self.nombre = "Usuario"
            self.apellido = "Demo"
            self.email = "demo@alfaia.com"
            self.nivel_inicial = "Principiante"


    demo_user = DemoUser()
    window = MainWindow(demo_user)
    window.show()

    print("✅ MainWindow en modo de prueba")
    sys.exit(app.exec())
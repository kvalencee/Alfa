
# AlfaIA/ui/windows/main_window.py - Preparado para Módulos Futuros
# =============================================================================

import sys
from pathlib import Path

# IMPORTS CRÍTICOS DE PyQt6 - ESTOS DEBEN FUNCIONAR
print("🔄 Importando PyQt6...")

# Import básico que siempre debe funcionar
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

print("✅ PyQt6 importado correctamente")

# Agregar path para imports
sys.path.append(str(Path(__file__).parent.parent.parent))

try:
    from config.settings import Settings
    from core.database.connection import DatabaseManager

    print("✅ Imports de configuración exitosos")
except ImportError as e:
    print(f"⚠️ Error importando configuración: {e}")


    # Crear clases fallback
    class Settings:
        APP_NAME = "AlfaIA"
        APP_VERSION = "1.0.0"
        COLORS = {
            'blue_educational': '#4A90E2',
            'green_success': '#7ED321',
            'orange_energetic': '#F5A623',
            'purple_creative': '#9013FE',
            'text_primary': '#2C3E50',
            'text_secondary': '#7F8C8D',
            'gray_neutral': '#8E9AAF',
            'blue_light': '#E8F4FD'
        }


    class DatabaseManager:
        def test_connection(self):
            return False


class UserDataManager:
    """Gestor centralizado de datos de usuario - Preparado para futuros módulos"""

    def __init__(self, user_data=None):
        print("🔧 Inicializando UserDataManager...")

        # Datos básicos por defecto
        self.user_id = None
        self.user_name = "Usuario Demo"
        self.user_email = "demo@alfaia.com"
        self.first_name = "Usuario"
        self.last_name = "Demo"

        # Datos de perfil por defecto
        self.daily_goal = 5
        self.current_level = "Principiante"
        self.total_points = 0
        self.current_streak = 0
        self.exercises_completed = 0
        self.study_time_minutes = 0

        # Preferencias por defecto
        self.preferences = {
            "theme": "light",
            "notifications": True,
            "sounds": True,
            "difficulty_auto_adjust": True
        }

        # Procesar datos de entrada
        self.load_user_data(user_data)

    def load_user_data(self, user_data):
        """Cargar datos de usuario de forma robusta"""
        if not user_data:
            print("⚠️ No se recibieron datos de usuario, usando valores por defecto")
            return

        try:
            print(f"📥 Procesando datos de usuario: {type(user_data)}")

            # Extraer datos básicos de forma segura
            if hasattr(user_data, 'id'):
                self.user_id = user_data.id

            if hasattr(user_data, 'nombre'):
                self.first_name = user_data.nombre
                self.user_name = f"{user_data.nombre}"

                if hasattr(user_data, 'apellido') and user_data.apellido:
                    self.last_name = user_data.apellido
                    self.user_name = f"{user_data.nombre} {user_data.apellido}"

            if hasattr(user_data, 'email'):
                self.user_email = user_data.email

            if hasattr(user_data, 'nivel_inicial'):
                if hasattr(user_data.nivel_inicial, 'value'):
                    self.current_level = user_data.nivel_inicial.value
                else:
                    self.current_level = str(user_data.nivel_inicial)

            print(f"✅ Datos de usuario procesados: {self.user_name}")

            # Intentar cargar perfil desde BD (sin fallar si hay error)
            self.load_profile_safe()

        except Exception as e:
            print(f"⚠️ Error procesando datos de usuario: {e}")
            print("🔄 Usando datos por defecto")

    def load_profile_safe(self):
        """Cargar perfil de usuario de forma segura (no falla nunca)"""
        if not self.user_id:
            print("⚠️ No hay user_id, no se puede cargar perfil desde BD")
            return

        try:
            print(f"🔍 Intentando cargar perfil para user_id: {self.user_id}")

            # Intentar importar y cargar perfil
            try:
                from core.database.models import PerfilUsuario
                profile = PerfilUsuario.find_by_user_id(self.user_id)

                if profile:
                    print("✅ Perfil cargado desde BD")
                    self.daily_goal = profile.objetivo_diario_ejercicios
                    self.total_points = profile.puntos_totales
                    self.current_streak = profile.racha_dias_consecutivos
                    self.exercises_completed = profile.ejercicios_completados
                    self.study_time_minutes = profile.tiempo_total_minutos

                    # Cargar preferencias si existen
                    if hasattr(profile, 'preferencias_json') and profile.preferencias_json:
                        self.preferences.update(profile.preferencias_json)

                else:
                    print("⚠️ No se encontró perfil en BD, usando valores por defecto")

            except ImportError as e:
                print(f"⚠️ No se pueden importar modelos de BD: {e}")
            except Exception as e:
                print(f"⚠️ Error con modelos de BD: {e}")

        except Exception as e:
            print(f"⚠️ Error general cargando perfil: {e}")
            print("🔄 Continuando con valores por defecto")

    def get_display_name(self):
        """Obtener nombre para mostrar"""
        return self.user_name

    def get_greeting_name(self):
        """Obtener nombre para saludo"""
        return self.first_name

    def get_progress_text(self):
        """Obtener texto de progreso diario"""
        return f"🎯 Progreso del día: 0/{self.daily_goal}"

    def get_stats_data(self):
        """Obtener datos de estadísticas para el dashboard"""
        return [
            ("Nivel Actual", self.current_level, "🎓", "#4A90E2", "Tu nivel de español"),
            ("Ejercicios Hoy", f"0 / {self.daily_goal}", "📝", "#7ED321", "Meta diaria"),
            ("Racha Actual", f"{self.current_streak} días", "🔥", "#F5A623", "Días consecutivos"),
            ("Tiempo Total", f"{self.study_time_minutes} min", "⏱️", "#9013FE", "Tiempo de estudio"),
            ("Puntos Totales", f"{self.total_points} pts", "⭐", "#FFD700", "Puntuación acumulada"),
            ("Ejercicios", f"{self.exercises_completed}", "🏆", "#FF6B6B", "Ejercicios completados")
        ]

    def update_daily_progress(self, completed_today=0):
        """Actualizar progreso diario (para futuros módulos)"""
        # Esta función será expandida cuando implementemos los módulos
        return f"🎯 Progreso del día: {completed_today}/{self.daily_goal}"

    def save_progress(self, exercise_data):
        """Guardar progreso de ejercicio (para módulos futuros)"""
        try:
            # Esta función será implementada cuando desarrollemos los módulos de ejercicios
            print(f"💾 Guardando progreso: {exercise_data}")
            return True
        except Exception as e:
            print(f"❌ Error guardando progreso: {e}")
            return False


class ModernSidebarWidget(QTreeWidget):
    """Sidebar moderna con mejor diseño visual"""
    section_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = Settings()
        self.setup_ui()
        self.populate_sidebar()

    def setup_ui(self):
        """Configurar interfaz de la barra lateral moderna"""
        self.setHeaderHidden(True)
        self.setRootIsDecorated(False)
        self.setIndentation(0)
        self.setMinimumWidth(280)
        self.setMaximumWidth(320)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Aplicar estilos modernos similares al login
        self.setStyleSheet(f"""
            QTreeWidget {{
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #f8fafc,
                    stop: 0.1 #f1f5f9,
                    stop: 1 #e2e8f0
                );
                border: none;
                font-size: 16px;
                color: {self.settings.COLORS['text_primary']};
                font-family: 'Segoe UI', 'Arial', sans-serif;
                outline: none;
            }}
            QTreeWidget::item {{
                padding: 18px 24px;
                border: none;
                margin: 4px 12px;
                border-radius: 12px;
                background-color: transparent;
                font-weight: 500;
                color: {self.settings.COLORS['text_primary']};
            }}
            QTreeWidget::item:selected {{
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 {self.settings.COLORS['blue_educational']},
                    stop: 1 #5ba3f5
                );
                color: white;
                border: none;
                font-weight: 600;
            }}
            QTreeWidget::item:hover:!selected {{
                background-color: {self.settings.COLORS['blue_educational']}20;
                color: {self.settings.COLORS['blue_educational']};
                border: 2px solid {self.settings.COLORS['blue_educational']}40;
            }}
        """)

    def populate_sidebar(self):
        """Poblar la barra lateral con opciones de navegación mejoradas"""
        sections = [
            ("🏠", "Dashboard", "dashboard", "Resumen y estado general"),
            ("📚", "Ejercicios", "exercises", "Practica con ejercicios interactivos"),
            ("🎮", "Juegos", "games", "Aprende jugando"),
            ("📊", "Progreso", "progress", "Analiza tu avance"),
            ("🏆", "Logros", "achievements", "Tus logros y recompensas"),
            ("👤", "Perfil", "profile", "Configuración personal"),
            ("⚙️", "Configuración", "settings", "Ajustes de la aplicación")
        ]

        for icon, text, key, description in sections:
            item = QTreeWidgetItem(self)
            item.setText(0, f"  {icon}   {text}")
            item.setData(0, Qt.ItemDataRole.UserRole, key)
            item.setToolTip(0, description)

        # Conectar señal de selección
        self.itemClicked.connect(self.on_item_clicked)

        # Seleccionar dashboard por defecto
        if self.topLevelItemCount() > 0:
            self.setCurrentItem(self.topLevelItem(0))

    def on_item_clicked(self, item, column):
        """Manejar clic en item de la barra lateral"""
        section_key = item.data(0, Qt.ItemDataRole.UserRole)
        if section_key:
            self.section_changed.emit(section_key)


class ModernStatsCard(QFrame):
    """Tarjeta de estadística moderna"""

    def __init__(self, title, value, icon, color, description="", parent=None):
        super().__init__(parent)
        self.settings = Settings()
        self.setup_ui(title, value, icon, color, description)

    def setup_ui(self, title, value, icon, color, description):
        """Configurar interfaz de la tarjeta"""
        self.setFixedHeight(140)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: none;
                border-radius: 16px;
                padding: 20px;
            }}
            QFrame:hover {{
                background-color: #f8fafc;
                border: 1px solid {color}40;
            }}
        """)

        # Efecto de sombra
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 30))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)

        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(20, 16, 20, 16)

        # Header con icono y valor
        header_layout = QHBoxLayout()

        # Icono
        icon_label = QLabel(icon)
        icon_label.setStyleSheet(f"""
            QLabel {{
                font-size: 32px;
                color: {color};
                background-color: {color}15;
                border-radius: 12px;
                padding: 8px;
                max-width: 48px;
                max-height: 48px;
            }}
        """)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(icon_label)

        header_layout.addStretch()

        # Valor
        value_label = QLabel(value)
        value_label.setStyleSheet(f"""
            QLabel {{
                font-size: 28px;
                font-weight: bold;
                color: {color};
                margin: 0;
                background-color: transparent;
            }}
        """)
        value_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)
        header_layout.addWidget(value_label)

        layout.addLayout(header_layout)

        # Título
        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            QLabel {{
                font-size: 16px;
                font-weight: 600;
                color: {self.settings.COLORS['text_primary']};
                margin: 0;
                background-color: transparent;
            }}
        """)
        layout.addWidget(title_label)

        # Descripción
        if description:
            desc_label = QLabel(description)
            desc_label.setStyleSheet(f"""
                QLabel {{
                    font-size: 13px;
                    color: {self.settings.COLORS['text_secondary']};
                    margin: 0;
                    background-color: transparent;
                }}
            """)
            desc_label.setWordWrap(True)
            layout.addWidget(desc_label)

        layout.addStretch()


class ModernDashboardWidget(QWidget):
    """Dashboard principal moderno con datos reales"""

    def __init__(self, user_data_manager, parent=None):
        super().__init__(parent)
        self.settings = Settings()
        self.user_data = user_data_manager
        self.greeting_label = None
        self.stats_cards = []  # Para poder actualizar las estadísticas
        self.setup_ui()

    def setup_ui(self):
        """Configurar interfaz del dashboard moderno"""
        # Scroll area principal
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("""
            QScrollArea { 
                border: none; 
                background-color: #f8fafc; 
            }
            QScrollBar:vertical {
                background-color: #e2e8f0;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background-color: #94a3b8;
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #64748b;
            }
        """)

        # Widget principal del scroll
        main_widget = QWidget()
        scroll_area.setWidget(main_widget)

        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll_area)

        # Layout del contenido
        content_layout = QVBoxLayout(main_widget)
        content_layout.setSpacing(30)
        content_layout.setContentsMargins(40, 40, 40, 40)

        # Header del dashboard
        header_section = self.create_header_section()
        content_layout.addWidget(header_section)

        # Panel de estadísticas
        stats_section = self.create_stats_section()
        content_layout.addWidget(stats_section)

        # Panel de actividad reciente
        activity_section = self.create_activity_section()
        content_layout.addWidget(activity_section)

        # Panel de acciones rápidas
        quick_actions_section = self.create_quick_actions_section()
        content_layout.addWidget(quick_actions_section)

        # Espaciador final
        content_layout.addStretch()

    def create_header_section(self):
        """Crear sección de encabezado personalizada"""
        section = QFrame()
        section.setStyleSheet("""
            QFrame {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #667eea,
                    stop: 0.5 #764ba2,
                    stop: 1 #f093fb
                );
                border-radius: 20px;
                padding: 30px;
            }
        """)

        # Efecto de sombra
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(25)
        shadow.setColor(QColor(0, 0, 0, 40))
        shadow.setOffset(0, 6)
        section.setGraphicsEffect(shadow)

        layout = QVBoxLayout(section)
        layout.setSpacing(15)

        # Saludo personalizado
        greeting_text = f"¡Bienvenido de vuelta, {self.user_data.get_greeting_name()}! 👋"

        self.greeting_label = QLabel(greeting_text)
        self.greeting_label.setStyleSheet("""
            QLabel {
                font-size: 36px;
                font-weight: bold;
                color: white;
                margin: 0;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
                background-color: transparent;
            }
        """)
        layout.addWidget(self.greeting_label)

        # Mensaje motivacional
        motivation = QLabel("Continúa tu viaje de aprendizaje del español con AlfaIA")
        motivation.setStyleSheet("""
            QLabel {
                font-size: 18px;
                color: white;
                margin: 0;
                text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
                font-weight: 300;
                background-color: transparent;
            }
        """)
        layout.addWidget(motivation)

        return section

    def create_stats_section(self):
        """Crear sección de estadísticas con datos reales"""
        section = QFrame()
        section.setStyleSheet("QFrame { background-color: transparent; }")

        layout = QVBoxLayout(section)
        layout.setSpacing(20)

        # Título de sección
        title = QLabel("📊 Tu Progreso")
        title.setStyleSheet(f"""
            QLabel {{
                font-size: 24px;
                font-weight: bold;
                color: {self.settings.COLORS['text_primary']};
                margin-bottom: 10px;
                background-color: transparent;
            }}
        """)
        layout.addWidget(title)

        # Grid de estadísticas con datos reales
        stats_grid = QGridLayout()
        stats_grid.setSpacing(20)
        stats_grid.setContentsMargins(0, 0, 0, 0)

        # Obtener datos reales del usuario
        stats_data = self.user_data.get_stats_data()

        self.stats_cards = []  # Para poder actualizar después
        for i, (title, value, icon, color, desc) in enumerate(stats_data):
            card = ModernStatsCard(title, value, icon, color, desc)
            self.stats_cards.append(card)
            row = i // 3
            col = i % 3
            stats_grid.addWidget(card, row, col)

        layout.addLayout(stats_grid)
        return section

    def create_activity_section(self):
        """Crear sección de actividad reciente"""
        section = QFrame()
        section.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-radius: 16px;
                padding: 24px;
                border: 1px solid {self.settings.COLORS['gray_neutral']}20;
            }}
        """)

        # Efecto de sombra
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 20))
        shadow.setOffset(0, 2)
        section.setGraphicsEffect(shadow)

        layout = QVBoxLayout(section)
        layout.setSpacing(20)

        # Título
        title = QLabel("📈 Actividad Reciente")
        title.setStyleSheet(f"""
            QLabel {{
                font-size: 20px;
                font-weight: bold;
                color: {self.settings.COLORS['text_primary']};
                margin-bottom: 10px;
                background-color: transparent;
            }}
        """)
        layout.addWidget(title)

        # Actividades personalizadas según el usuario
        activities = [
            ("Hoy", f"¡Bienvenido {self.user_data.get_greeting_name()}!", "Iniciaste sesión en AlfaIA", "🎉"),
            ("Próximo", "Completar primer ejercicio", "Prueba un ejercicio de gramática básica", "📚"),
            ("Próximo", "Explorar juegos", "Diviértete mientras aprendes", "🎮")
        ]

        for time, title_act, desc, icon in activities:
            activity_item = self.create_activity_item(time, title_act, desc, icon)
            layout.addWidget(activity_item)

        return section

    def create_activity_item(self, time, title, description, icon):
        """Crear item de actividad individual"""
        item = QFrame()
        item.setStyleSheet(f"""
            QFrame {{
                background-color: {self.settings.COLORS['blue_light']};
                border-radius: 12px;
                padding: 16px;
                border-left: 4px solid {self.settings.COLORS['blue_educational']};
            }}
            QFrame:hover {{
                background-color: {self.settings.COLORS['blue_educational']}10;
            }}
        """)

        layout = QHBoxLayout(item)
        layout.setSpacing(16)

        # Icono
        icon_label = QLabel(icon)
        icon_label.setStyleSheet(f"""
            QLabel {{
                font-size: 24px;
                background-color: {self.settings.COLORS['blue_educational']};
                color: white;
                border-radius: 20px;
                padding: 8px;
                max-width: 40px;
                max-height: 40px;
            }}
        """)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon_label)

        # Contenido
        content_layout = QVBoxLayout()
        content_layout.setSpacing(4)

        # Título y tiempo
        header_layout = QHBoxLayout()

        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            QLabel {{
                font-size: 16px;
                font-weight: 600;
                color: {self.settings.COLORS['text_primary']};
                background-color: transparent;
            }}
        """)
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        time_label = QLabel(time)
        time_label.setStyleSheet(f"""
            QLabel {{
                font-size: 12px;
                color: {self.settings.COLORS['text_secondary']};
                background-color: {self.settings.COLORS['blue_educational']}20;
                padding: 4px 8px;
                border-radius: 8px;
            }}
        """)
        header_layout.addWidget(time_label)

        content_layout.addLayout(header_layout)

        # Descripción
        desc_label = QLabel(description)
        desc_label.setStyleSheet(f"""
            QLabel {{
                font-size: 14px;
                color: {self.settings.COLORS['text_secondary']};
                margin: 0;
                background-color: transparent;
            }}
        """)
        desc_label.setWordWrap(True)
        content_layout.addWidget(desc_label)

        layout.addLayout(content_layout)

        return item

    def create_quick_actions_section(self):
        """Crear sección de acciones rápidas"""
        section = QFrame()
        section.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-radius: 16px;
                padding: 24px;
                border: 1px solid {self.settings.COLORS['gray_neutral']}20;
            }}
        """)

        # Efecto de sombra
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 20))
        shadow.setOffset(0, 2)
        section.setGraphicsEffect(shadow)

        layout = QVBoxLayout(section)
        layout.setSpacing(25)

        # Título
        title = QLabel("🚀 Acciones Rápidas")
        title.setStyleSheet(f"""
            QLabel {{
                font-size: 20px;
                font-weight: bold;
                color: {self.settings.COLORS['text_primary']};
                margin-bottom: 10px;
                background-color: transparent;
            }}
        """)
        layout.addWidget(title)

        # Grid de botones
        buttons_grid = QGridLayout()
        buttons_grid.setSpacing(16)

        # Botones de acción
        actions = [
            ("📝 Comenzar Ejercicio", "Practica gramática y vocabulario", self.settings.COLORS['blue_educational']),
            ("🎮 Jugar Ahora", "Aprende divirtiéndote", self.settings.COLORS['purple_creative']),
            ("📊 Ver Mi Progreso", "Analiza tu evolución", self.settings.COLORS['green_success']),
            ("🏆 Mis Logros", "Revisa tus logros", "#FFD700"),
            ("⚙️ Configuración", "Personaliza tu experiencia", self.settings.COLORS['gray_neutral']),
            ("❓ Ayuda", "Obtén ayuda y soporte", "#FF6B6B")
        ]

        for i, (text, desc, color) in enumerate(actions):
            button = self.create_action_button(text, desc, color)
            row = i // 2
            col = i % 2
            buttons_grid.addWidget(button, row, col)

        layout.addLayout(buttons_grid)

        return section

    def create_action_button(self, text, description, color):
        """Crear botón de acción moderno"""
        button = QPushButton()
        button.setFixedHeight(80)
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {color}10;
                color: {color};
                border: 2px solid {color}30;
                border-radius: 12px;
                padding: 16px 20px;
                font-size: 16px;
                font-weight: 600;
                text-align: left;
                font-family: 'Segoe UI', 'Arial', sans-serif;
            }}
            QPushButton:hover {{
                background-color: {color};
                color: white;
                border: 2px solid {color};
                transform: translateY(-2px);
            }}
            QPushButton:pressed {{
                background-color: {color}CC;
                transform: translateY(0px);
            }}
        """)

        button.setText(f"{text}\n{description}")
        return button

    def update_stats(self):
        """Actualizar estadísticas (para módulos futuros)"""
        # Esta función será expandida cuando implementemos los módulos
        print("🔄 Actualizando estadísticas del dashboard...")

    def refresh_data(self):
        """Refrescar todos los datos del dashboard"""
        # Esta función será útil cuando implementemos los módulos
        try:
            # Recargar datos del usuario
            self.user_data.load_profile_safe()
            # Actualizar estadísticas
            self.update_stats()
            print("✅ Dashboard actualizado")
        except Exception as e:
            print(f"❌ Error actualizando dashboard: {e}")


class PlaceholderWidget(QWidget):
    """Widget placeholder preparado para módulos futuros"""

    def __init__(self, section_name: str, user_data_manager, parent=None):
        super().__init__(parent)
        self.section_name = section_name
        self.user_data = user_data_manager
        self.settings = Settings()
        self.setup_ui()
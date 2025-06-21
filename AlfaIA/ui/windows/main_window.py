# =============================================================================
# AlfaIA/ui/windows/main_window.py - Ventana Principal de la Aplicación
# =============================================================================

import sys
from pathlib import Path
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QMenuBar, QToolBar, QStatusBar, QSplitter,
    QTreeWidget, QTreeWidgetItem, QStackedWidget,
    QLabel, QPushButton, QFrame, QMessageBox,
    QApplication
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QAction, QIcon, QFont, QPalette, QColor

# Agregar path para imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from config.settings import Settings
from core.database.connection import DatabaseManager


class SidebarWidget(QTreeWidget):
    """Widget de barra lateral para navegación"""

    # Señal emitida cuando se selecciona una sección
    section_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = Settings()
        self.setup_ui()
        self.populate_sidebar()

    def setup_ui(self):
        """Configurar interfaz de la barra lateral"""
        self.setHeaderHidden(True)
        self.setRootIsDecorated(False)
        self.setIndentation(20)
        self.setMinimumWidth(250)
        self.setMaximumWidth(300)

        # Aplicar estilos
        self.setStyleSheet(f"""
            QTreeWidget {{
                background-color: {self.settings.COLORS['blue_light']};
                border: none;
                font-size: 14px;
                color: {self.settings.COLORS['text_primary']};
            }}
            QTreeWidget::item {{
                padding: 12px 16px;
                border-bottom: 1px solid {self.settings.COLORS['gray_neutral']}40;
            }}
            QTreeWidget::item:selected {{
                background-color: {self.settings.COLORS['blue_educational']};
                color: white;
                border-radius: 8px;
                margin: 2px;
            }}
            QTreeWidget::item:hover {{
                background-color: {self.settings.COLORS['blue_educational']}30;
                border-radius: 8px;
                margin: 2px;
            }}
        """)

    def populate_sidebar(self):
        """Poblar la barra lateral con opciones de navegación"""
        sections = [
            ("🏠", "Dashboard", "dashboard"),
            ("📚", "Ejercicios", "exercises"),
            ("🎮", "Juegos", "games"),
            ("📊", "Progreso", "progress"),
            ("👤", "Perfil", "profile"),
            ("⚙️", "Configuración", "settings")
        ]

        for icon, text, key in sections:
            item = QTreeWidgetItem(self)
            item.setText(0, f"{icon}  {text}")
            item.setData(0, Qt.ItemDataRole.UserRole, key)

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


class DashboardWidget(QWidget):
    """Widget del dashboard principal"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = Settings()
        self.setup_ui()

    def setup_ui(self):
        """Configurar interfaz del dashboard"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        # Título de bienvenida
        title = QLabel("¡Bienvenido a AlfaIA! 🎓")
        title.setStyleSheet(f"""
            QLabel {{
                font-size: 28px;
                font-weight: bold;
                color: {self.settings.COLORS['blue_educational']};
                margin-bottom: 10px;
            }}
        """)
        layout.addWidget(title)

        # Subtítulo
        subtitle = QLabel("Tu compañero inteligente para aprender español")
        subtitle.setStyleSheet(f"""
            QLabel {{
                font-size: 16px;
                color: {self.settings.COLORS['text_secondary']};
                margin-bottom: 30px;
            }}
        """)
        layout.addWidget(subtitle)

        # Panel de estadísticas rápidas
        stats_frame = self.create_stats_panel()
        layout.addWidget(stats_frame)

        # Panel de acciones rápidas
        actions_frame = self.create_quick_actions()
        layout.addWidget(actions_frame)

        # Espacio flexible
        layout.addStretch()

    def create_stats_panel(self) -> QFrame:
        """Crear panel de estadísticas rápidas"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.Shape.Box)
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 2px solid {self.settings.COLORS['blue_light']};
                border-radius: 12px;
                padding: 20px;
            }}
        """)

        layout = QHBoxLayout(frame)

        # Estadísticas de ejemplo (se conectarán con la BD después)
        stats = [
            ("Nivel Actual", "Principiante", self.settings.COLORS['blue_educational']),
            ("Ejercicios Completados", "0", self.settings.COLORS['green_success']),
            ("Racha Actual", "0 días", self.settings.COLORS['orange_energetic']),
            ("Tiempo Total", "0 min", self.settings.COLORS['purple_creative'])
        ]

        for label, value, color in stats:
            stat_widget = self.create_stat_widget(label, value, color)
            layout.addWidget(stat_widget)

        return frame

    def create_stat_widget(self, label: str, value: str, color: str) -> QWidget:
        """Crear widget individual de estadística"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Valor
        value_label = QLabel(value)
        value_label.setStyleSheet(f"""
            QLabel {{
                font-size: 24px;
                font-weight: bold;
                color: {color};
            }}
        """)
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Etiqueta
        label_widget = QLabel(label)
        label_widget.setStyleSheet(f"""
            QLabel {{
                font-size: 12px;
                color: {self.settings.COLORS['text_secondary']};
            }}
        """)
        label_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(value_label)
        layout.addWidget(label_widget)

        return widget

    def create_quick_actions(self) -> QFrame:
        """Crear panel de acciones rápidas"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.Shape.Box)
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 2px solid {self.settings.COLORS['green_mint']};
                border-radius: 12px;
                padding: 20px;
            }}
        """)

        layout = QVBoxLayout(frame)

        # Título
        title = QLabel("🚀 Acciones Rápidas")
        title.setStyleSheet(f"""
            QLabel {{
                font-size: 18px;
                font-weight: bold;
                color: {self.settings.COLORS['text_primary']};
                margin-bottom: 15px;
            }}
        """)
        layout.addWidget(title)

        # Botones de acción
        buttons_layout = QHBoxLayout()

        actions = [
            ("📝 Comenzar Ejercicio", self.settings.COLORS['blue_educational']),
            ("🎮 Jugar", self.settings.COLORS['purple_creative']),
            ("📊 Ver Progreso", self.settings.COLORS['green_success']),
            ("⚙️ Configurar", self.settings.COLORS['gray_neutral'])
        ]

        for text, color in actions:
            button = QPushButton(text)
            button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 12px 20px;
                    font-size: 14px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {color}CC;
                }}
                QPushButton:pressed {{
                    background-color: {color}AA;
                }}
            """)
            buttons_layout.addWidget(button)

        layout.addLayout(buttons_layout)

        return frame


class PlaceholderWidget(QWidget):
    """Widget placeholder para secciones en desarrollo"""

    def __init__(self, section_name: str, parent=None):
        super().__init__(parent)
        self.section_name = section_name
        self.settings = Settings()
        self.setup_ui()

    def setup_ui(self):
        """Configurar interfaz placeholder"""
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Icono de sección
        icon_map = {
            "exercises": "📚",
            "games": "🎮",
            "progress": "📊",
            "profile": "👤",
            "settings": "⚙️"
        }

        icon = QLabel(icon_map.get(self.section_name, "📄"))
        icon.setStyleSheet("font-size: 64px;")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon)

        # Título
        title = QLabel(f"Sección: {self.section_name.title()}")
        title.setStyleSheet(f"""
            QLabel {{
                font-size: 24px;
                font-weight: bold;
                color: {self.settings.COLORS['blue_educational']};
                margin: 20px;
            }}
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Mensaje
        message = QLabel("Esta sección se desarrollará en fases posteriores")
        message.setStyleSheet(f"""
            QLabel {{
                font-size: 16px;
                color: {self.settings.COLORS['text_secondary']};
            }}
        """)
        message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(message)


class MainWindow(QMainWindow):
    """Ventana principal de AlfaIA"""

    def __init__(self):
        super().__init__()
        self.settings = Settings()
        self.db_manager = DatabaseManager()
        self.setup_ui()
        self.setup_connections()
        self.setup_status_updates()

    def setup_ui(self):
        """Configurar interfaz principal"""
        # Configuración básica de ventana
        self.setWindowTitle(f"{self.settings.APP_NAME} v{self.settings.APP_VERSION}")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)

        # Crear componentes principales
        self.create_menu_bar()
        self.create_toolbar()
        self.create_central_widget()
        self.create_status_bar()

        # Aplicar estilos globales
        self.apply_global_styles()

    def create_menu_bar(self):
        """Crear barra de menú"""
        menubar = self.menuBar()

        # Menú Archivo
        file_menu = menubar.addMenu("&Archivo")

        # Menú Ejercicios
        exercises_menu = menubar.addMenu("&Ejercicios")

        # Menú Juegos
        games_menu = menubar.addMenu("&Juegos")

        # Menú Análisis
        analysis_menu = menubar.addMenu("&Análisis")

        # Menú Ayuda
        help_menu = menubar.addMenu("&Ayuda")
        about_action = help_menu.addAction("Acerca de AlfaIA")
        about_action.triggered.connect(self.show_about_dialog)

    def create_toolbar(self):
        """Crear barra de herramientas"""
        toolbar = self.addToolBar("Principal")
        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)

        # Acciones rápidas
        actions = [
            ("🏠", "Dashboard", self.show_dashboard),
            ("📚", "Ejercicios", lambda: self.switch_section("exercises")),
            ("🎮", "Juegos", lambda: self.switch_section("games")),
            ("📊", "Progreso", lambda: self.switch_section("progress"))
        ]

        for icon, text, callback in actions:
            action = QAction(f"{icon}\n{text}", self)
            action.triggered.connect(callback)
            toolbar.addAction(action)

    def create_central_widget(self):
        """Crear widget central con splitter"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layout principal
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Splitter para dividir sidebar y contenido
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Barra lateral
        self.sidebar = SidebarWidget()
        splitter.addWidget(self.sidebar)

        # Widget de contenido principal (stackable)
        self.content_stack = QStackedWidget()
        splitter.addWidget(self.content_stack)

        # Configurar proporciones del splitter
        splitter.setSizes([250, 1000])
        splitter.setCollapsible(0, False)  # No colapsar sidebar

        main_layout.addWidget(splitter)

        # Crear widgets de contenido
        self.create_content_widgets()

    def create_content_widgets(self):
        """Crear widgets de contenido para cada sección"""
        # Dashboard
        self.dashboard_widget = DashboardWidget()
        self.content_stack.addWidget(self.dashboard_widget)

        # Placeholders para otras secciones
        sections = ["exercises", "games", "progress", "profile", "settings"]
        self.section_widgets = {}

        for section in sections:
            widget = PlaceholderWidget(section)
            self.section_widgets[section] = widget
            self.content_stack.addWidget(widget)

        # Mostrar dashboard por defecto
        self.content_stack.setCurrentWidget(self.dashboard_widget)

    def create_status_bar(self):
        """Crear barra de estado"""
        self.status_bar = self.statusBar()

        # Etiquetas de estado
        self.user_label = QLabel("Usuario: No conectado")
        self.progress_label = QLabel("Progreso del día: 0/5")
        self.db_label = QLabel("BD: Conectando...")

        # Agregar a barra de estado
        self.status_bar.addWidget(self.user_label)
        self.status_bar.addPermanentWidget(self.progress_label)
        self.status_bar.addPermanentWidget(self.db_label)

    def apply_global_styles(self):
        """Aplicar estilos globales a la aplicación"""
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {self.settings.COLORS['white_pure']};
                color: {self.settings.COLORS['text_primary']};
                font-family: 'Segoe UI', 'Inter', 'Roboto', sans-serif;
                font-size: 14px;
            }}
            QMenuBar {{
                background-color: {self.settings.COLORS['blue_light']};
                border-bottom: 1px solid {self.settings.COLORS['gray_neutral']};
                padding: 4px;
            }}
            QToolBar {{
                background-color: {self.settings.COLORS['blue_light']};
                border-bottom: 1px solid {self.settings.COLORS['gray_neutral']};
                spacing: 8px;
                padding: 8px;
            }}
            QStatusBar {{
                background-color: {self.settings.COLORS['blue_light']};
                border-top: 1px solid {self.settings.COLORS['gray_neutral']};
                color: {self.settings.COLORS['text_secondary']};
            }}
        """)

    def setup_connections(self):
        """Configurar conexiones de señales"""
        # Conectar sidebar con cambio de sección
        self.sidebar.section_changed.connect(self.switch_section)

    def setup_status_updates(self):
        """Configurar actualizaciones de estado"""
        # Timer para actualizar estado de BD
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status)
        self.status_timer.start(5000)  # Actualizar cada 5 segundos

        # Actualización inicial
        self.update_status()

    def switch_section(self, section_key: str):
        """Cambiar a una sección específica"""
        if section_key == "dashboard":
            self.content_stack.setCurrentWidget(self.dashboard_widget)
        elif section_key in self.section_widgets:
            self.content_stack.setCurrentWidget(self.section_widgets[section_key])

    def show_dashboard(self):
        """Mostrar dashboard"""
        self.switch_section("dashboard")
        # Actualizar selección en sidebar
        if self.sidebar.topLevelItemCount() > 0:
            self.sidebar.setCurrentItem(self.sidebar.topLevelItem(0))

    def update_status(self):
        """Actualizar información en barra de estado"""
        # Verificar conexión de BD
        if self.db_manager.test_connection():
            self.db_label.setText("BD: ✅ Conectado")
            self.db_label.setStyleSheet(f"color: {self.settings.COLORS['green_success']};")
        else:
            self.db_label.setText("BD: ❌ Desconectado")
            self.db_label.setStyleSheet(f"color: {self.settings.COLORS['red_soft']};")

    def show_about_dialog(self):
        """Mostrar diálogo Acerca de"""
        QMessageBox.about(
            self,
            "Acerca de AlfaIA",
            f"""
            <h2>{self.settings.APP_NAME}</h2>
            <p><b>Versión:</b> {self.settings.APP_VERSION}</p>
            <p><b>Descripción:</b> {self.settings.APP_DESCRIPTION}</p>
            <p>Aplicación educativa para el aprendizaje de español con inteligencia artificial.</p>
            <p><b>Tecnologías:</b> PyQt6, MySQL, spaCy, NLP</p>
            """
        )

    def closeEvent(self, event):
        """Manejar cierre de aplicación"""
        reply = QMessageBox.question(
            self,
            "Salir de AlfaIA",
            "¿Estás seguro de que quieres salir?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Limpiar recursos
            if hasattr(self, 'status_timer'):
                self.status_timer.stop()
            event.accept()
        else:
            event.ignore()


# =============================================================================
# Código de prueba si se ejecuta directamente
# =============================================================================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
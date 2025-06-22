# =============================================================================
# AlfaIA/main.py - Punto de Entrada Corregido y Optimizado
# =============================================================================

import sys
import logging
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QMessageBox, QSplashScreen
from PyQt6.QtCore import QTranslator, QLocale, QTimer, Qt
from PyQt6.QtGui import QIcon, QPixmap, QPalette, QColor

print("🚀 Iniciando AlfaIA...")

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('alfaia.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Agregar path para imports
sys.path.append(str(Path(__file__).parent))

# Importar configuración y componentes principales
try:
    from config.settings import Settings
    from config.database_config import DatabaseConfig
    from core.database.connection import DatabaseManager
    from core.auth.authentication import auth_manager

    print("✅ Configuración importada exitosamente")
except ImportError as e:
    print(f"❌ Error importando configuración: {e}")
    sys.exit(1)


class AlfaIAApplication:
    """Aplicación principal de AlfaIA - Corregida y optimizada"""

    def __init__(self):
        self.app = None
        self.main_window = None
        self.login_window = None
        self.splash = None
        self.db_manager = None
        self.settings = Settings()
        self.logger = logging.getLogger(__name__)

        print("🏗️ AlfaIAApplication inicializada")

    def show_splash_screen(self):
        """Mostrar pantalla de splash mientras carga la aplicación"""
        try:
            # Crear splash screen simple
            splash_pixmap = QPixmap(400, 300)
            splash_pixmap.fill(QColor(self.settings.COLORS['blue_educational']))

            self.splash = QSplashScreen(splash_pixmap)
            self.splash.setStyleSheet(f"""
                QSplashScreen {{
                    color: white;
                    font-size: 18px;
                    font-weight: bold;
                }}
            """)

            self.splash.show()
            self.splash.showMessage("🎓 Iniciando AlfaIA...",
                                    alignment=Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignBottom)

            # Procesar eventos para mostrar el splash
            self.app.processEvents()

        except Exception as e:
            print(f"⚠️ Error creando splash: {e}")

    def hide_splash_screen(self):
        """Ocultar splash screen"""
        if self.splash:
            self.splash.close()
            self.splash = None

    def initialize_app(self) -> bool:
        """Inicializar aplicación PyQt6"""
        try:
            self.app = QApplication(sys.argv)

            # Configurar aplicación
            self.app.setApplicationName(self.settings.APP_NAME)
            self.app.setApplicationVersion(self.settings.APP_VERSION)
            self.app.setOrganizationName("AlfaIA")

            # Mostrar splash
            self.show_splash_screen()

            # Configurar estilo global
            self.setup_global_style()

            self.logger.info("Aplicación PyQt6 inicializada")
            return True

        except Exception as e:
            self.logger.error(f"Error inicializando aplicación: {e}")
            return False

    def setup_global_style(self):
        """Configurar estilo global de la aplicación"""
        global_style = f"""
            /* Estilo global para toda la aplicación */
            QApplication {{
                font-family: 'Segoe UI', 'Arial', sans-serif;
                font-size: 14px;
            }}

            /* Mensajes de diálogo */
            QMessageBox {{
                background-color: white;
                color: {self.settings.COLORS['text_primary']};
                font-size: 14px;
                min-width: 350px;
            }}

            QMessageBox QPushButton {{
                background-color: {self.settings.COLORS['blue_educational']};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 600;
                min-width: 80px;
            }}

            QMessageBox QPushButton:hover {{
                background-color: #3a7bd5;
            }}

            /* Barras de scroll globales */
            QScrollBar:vertical {{
                background-color: #f1f5f9;
                width: 12px;
                border-radius: 6px;
                margin: 0;
            }}

            QScrollBar::handle:vertical {{
                background-color: {self.settings.COLORS['gray_neutral']};
                border-radius: 6px;
                min-height: 20px;
                margin: 2px;
            }}

            QScrollBar::handle:vertical:hover {{
                background-color: {self.settings.COLORS['blue_educational']};
            }}

            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                border: none;
                background: none;
                height: 0px;
            }}

            /* Tooltips */
            QToolTip {{
                background-color: {self.settings.COLORS['text_primary']};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 12px;
            }}
        """

        self.app.setStyleSheet(global_style)

    def initialize_database(self) -> bool:
        """Inicializar base de datos"""
        try:
            if self.splash:
                self.splash.showMessage("🗄️ Conectando a base de datos...",
                                        alignment=Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignBottom)
                self.app.processEvents()

            self.db_manager = DatabaseManager()

            # Probar conexión
            if not self.db_manager.test_connection():
                self.show_database_error(
                    "No se pudo conectar a MySQL.\n\nVerifica que MySQL esté ejecutándose y las credenciales sean correctas.")
                return False

            # Crear esquema
            if not self.db_manager.create_database_schema():
                self.show_database_error("Error creando las tablas de la base de datos.")
                return False

            self.logger.info("Base de datos inicializada")
            return True

        except Exception as e:
            self.logger.error(f"Error inicializando BD: {e}")
            self.show_database_error(f"Error de conexión a base de datos:\n{str(e)}")
            return False

    def show_database_error(self, message: str):
        """Mostrar error de base de datos"""
        self.hide_splash_screen()
        QMessageBox.critical(None, "Error de Base de Datos", message)

    def show_login_window(self):
        """Mostrar ventana de login"""
        try:
            if self.splash:
                self.splash.showMessage("🔑 Cargando sistema de autenticación...",
                                        alignment=Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignBottom)
                self.app.processEvents()

            from ui.windows.login_window import LoginWindow
            self.login_window = LoginWindow()

            # Conectar señal de login exitoso
            self.login_window.login_successful.connect(self.on_login_success)

            # Ocultar splash y mostrar login
            self.hide_splash_screen()
            self.login_window.show()

            self.logger.info("Ventana de login mostrada")
            return True

        except Exception as e:
            self.logger.error(f"Error creando ventana de login: {e}")
            self.hide_splash_screen()
            QMessageBox.critical(None, "Error", f"No se pudo cargar la ventana de login:\n{str(e)}")
            return False

    def on_login_success(self):
        """Manejar login exitoso"""
        print("🎉 Login exitoso - Cargando ventana principal...")

        # Pequeño delay para asegurar que el auth_manager esté actualizado
        QTimer.singleShot(200, self.show_main_window)

    def show_main_window(self):
        """Mostrar ventana principal"""
        try:
            # Obtener usuario del auth_manager
            current_user = auth_manager.get_current_user()

            if not current_user:
                QMessageBox.warning(None, "Error", "No se pudo obtener información del usuario.")
                return

            print(f"👤 Cargando ventana principal para: {current_user.nombre} {current_user.apellido}")

            # Importar y crear ventana principal
            from ui.windows.main_window import MainWindow
            self.main_window = MainWindow(current_user)

            # Mostrar ventana principal
            self.main_window.show()

            # Cerrar y limpiar ventana de login
            if self.login_window:
                self.login_window.close()
                self.login_window = None

            self.logger.info(f"Ventana principal mostrada para usuario: {current_user.email}")
            print("✅ Ventana principal cargada exitosamente")

        except Exception as e:
            self.logger.error(f"Error mostrando ventana principal: {e}")
            QMessageBox.critical(None, "Error", f"No se pudo cargar la ventana principal:\n{str(e)}")
            import traceback
            traceback.print_exc()

    def run(self) -> int:
        """Ejecutar aplicación"""
        try:
            print("\n=== INICIANDO ALFAIA ===")

            # 1. Inicializar PyQt6
            if not self.initialize_app():
                return 1

            # 2. Inicializar base de datos
            if not self.initialize_database():
                return 1

            # 3. Mostrar login
            if not self.show_login_window():
                return 1

            # 4. Ejecutar aplicación
            self.logger.info("AlfaIA iniciado exitosamente")
            print("🎉 AlfaIA listo para usar")

            return self.app.exec()

        except Exception as e:
            self.logger.error(f"Error ejecutando aplicación: {e}")
            self.hide_splash_screen()
            QMessageBox.critical(None, "Error Fatal", f"Error inesperado:\n{str(e)}")
            return 1

    def cleanup(self):
        """Limpiar recursos"""
        try:
            self.hide_splash_screen()

            if self.main_window:
                self.main_window.close()

            if self.login_window:
                self.login_window.close()

            # Logout del auth_manager
            auth_manager.logout()

            self.logger.info("Recursos limpiados")

        except Exception as e:
            self.logger.error(f"Error en cleanup: {e}")


def main():
    """Función principal"""
    print("=" * 50)
    print("🎓 ALFAIA - APLICACIÓN EDUCATIVA")
    print("=" * 50)

    app = AlfaIAApplication()
    exit_code = 0

    try:
        exit_code = app.run()

    except KeyboardInterrupt:
        print("\n⚠️ Aplicación interrumpida por el usuario")
        exit_code = 0

    except Exception as e:
        print(f"❌ Error fatal: {e}")
        exit_code = 1

    finally:
        app.cleanup()
        print(f"\n🏁 AlfaIA terminado con código: {exit_code}")

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
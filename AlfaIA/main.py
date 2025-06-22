# =============================================================================
# AlfaIA/main.py - Punto de Entrada CORREGIDO con Debugging Mejorado
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

# IMPORTS SEGUROS CON DEBUGGING DETALLADO
try:
    from config.settings import Settings

    print("✅ Settings importado exitosamente")
except ImportError as e:
    print(f"❌ Error importando Settings: {e}")
    sys.exit(1)

try:
    from config.database_config import DatabaseConfig

    print("✅ DatabaseConfig importado exitosamente")
except ImportError as e:
    print(f"❌ Error importando DatabaseConfig: {e}")
    sys.exit(1)

try:
    from core.database.connection import DatabaseManager

    print("✅ DatabaseManager importado exitosamente")
except ImportError as e:
    print(f"❌ Error importando DatabaseManager: {e}")
    sys.exit(1)

try:
    from core.auth.authentication import auth_manager

    print("✅ auth_manager importado exitosamente")
except ImportError as e:
    print(f"❌ Error importando auth_manager: {e}")
    sys.exit(1)


class AlfaIAApplication:
    """Aplicación principal de AlfaIA - Corregida con mejor manejo de errores"""

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
            print("✅ Splash screen mostrado")

        except Exception as e:
            print(f"⚠️ Error creando splash: {e}")

    def hide_splash_screen(self):
        """Ocultar splash screen"""
        if self.splash:
            self.splash.close()
            self.splash = None
            print("✅ Splash screen ocultado")

    def initialize_app(self) -> bool:
        """Inicializar aplicación PyQt6"""
        try:
            print("🔧 Inicializando aplicación PyQt6...")

            self.app = QApplication(sys.argv)

            # Configurar aplicación
            self.app.setApplicationName(self.settings.APP_NAME)
            self.app.setApplicationVersion("1.0.0")
            self.app.setOrganizationName("AlfaIA")

            # Mostrar splash
            self.show_splash_screen()

            # Configurar estilo global
            self.setup_global_style()

            self.logger.info("Aplicación PyQt6 inicializada")
            print("✅ Aplicación PyQt6 inicializada correctamente")
            return True

        except Exception as e:
            self.logger.error(f"Error inicializando aplicación: {e}")
            print(f"❌ Error inicializando aplicación: {e}")
            import traceback
            traceback.print_exc()
            return False

    def setup_global_style(self):
        """Configurar estilo global de la aplicación"""
        try:
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
            print("✅ Estilo global aplicado")

        except Exception as e:
            print(f"⚠️ Error aplicando estilo global: {e}")

    def initialize_database(self) -> bool:
        """Inicializar base de datos"""
        try:
            print("🗄️ Inicializando base de datos...")

            if self.splash:
                self.splash.showMessage("🗄️ Conectando a base de datos...",
                                        alignment=Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignBottom)
                self.app.processEvents()

            self.db_manager = DatabaseManager()
            print("✅ DatabaseManager creado")

            # Probar conexión
            print("📡 Probando conexión a BD...")
            if not self.db_manager.test_connection():
                error_msg = ("No se pudo conectar a MySQL.\n\n"
                             "Verifica que:\n"
                             "• MySQL esté ejecutándose\n"
                             "• Las credenciales sean correctas\n"
                             "• El puerto 3306 esté disponible")
                self.show_database_error(error_msg)
                return False

            print("✅ Conexión a BD exitosa")

            # Crear esquema
            print("🏗️ Creando/verificando esquema de BD...")
            if not self.db_manager.create_database_schema():
                self.show_database_error("Error creando las tablas de la base de datos.")
                return False

            print("✅ Esquema de BD verificado")
            self.logger.info("Base de datos inicializada")
            return True

        except Exception as e:
            self.logger.error(f"Error inicializando BD: {e}")
            print(f"❌ Error inicializando BD: {e}")
            import traceback
            traceback.print_exc()
            self.show_database_error(f"Error de conexión a base de datos:\n{str(e)}")
            return False

    def show_database_error(self, message: str):
        """Mostrar error de base de datos"""
        self.hide_splash_screen()
        print(f"💥 Error de BD: {message}")
        QMessageBox.critical(None, "Error de Base de Datos", message)

    def show_login_window(self):
        """Mostrar ventana de login"""
        try:
            print("🔑 Cargando ventana de login...")

            if self.splash:
                self.splash.showMessage("🔑 Cargando sistema de autenticación...",
                                        alignment=Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignBottom)
                self.app.processEvents()

            from ui.windows.login_window import LoginWindow
            print("✅ LoginWindow importado")

            self.login_window = LoginWindow()
            print("✅ LoginWindow creado")

            # Conectar señal de login exitoso
            self.login_window.login_successful.connect(self.on_login_success)
            print("✅ Señal de login conectada")

            # Ocultar splash y mostrar login
            self.hide_splash_screen()
            self.login_window.show()

            self.logger.info("Ventana de login mostrada")
            print("✅ Ventana de login mostrada exitosamente")
            return True

        except Exception as e:
            self.logger.error(f"Error creando ventana de login: {e}")
            print(f"❌ Error creando ventana de login: {e}")
            import traceback
            traceback.print_exc()

            self.hide_splash_screen()
            QMessageBox.critical(None, "Error", f"No se pudo cargar la ventana de login:\n{str(e)}")
            return False

    def on_login_success(self):
        """Manejar login exitoso"""
        print("🎉 ¡Login exitoso detectado!")
        print("⏳ Preparando carga de ventana principal...")

        # Pequeño delay para asegurar que el auth_manager esté actualizado
        QTimer.singleShot(500, self.show_main_window)

    def show_main_window(self):
        """Mostrar ventana principal"""
        try:
            print("🏠 Iniciando carga de ventana principal...")

            # Obtener usuario del auth_manager
            print("👤 Obteniendo usuario actual...")
            current_user = auth_manager.get_current_user()

            if not current_user:
                print("❌ No se pudo obtener usuario del auth_manager")
                QMessageBox.warning(None, "Error", "No se pudo obtener información del usuario.")
                return

            print(f"✅ Usuario obtenido: {current_user.nombre} {current_user.apellido} ({current_user.email})")

            # Importar y crear ventana principal
            print("📦 Importando MainWindow...")
            from ui.windows.main_window import MainWindow
            print("✅ MainWindow importado exitosamente")

            print("🏗️ Creando instancia de MainWindow...")
            self.main_window = MainWindow(current_user)
            print("✅ MainWindow creado exitosamente")

            # Mostrar ventana principal
            print("👁️ Mostrando ventana principal...")
            self.main_window.show()
            print("✅ Ventana principal mostrada")

            # Cerrar y limpiar ventana de login
            if self.login_window:
                print("🧹 Cerrando ventana de login...")
                self.login_window.close()
                self.login_window = None
                print("✅ Ventana de login cerrada")

            self.logger.info(f"Ventana principal mostrada para usuario: {current_user.email}")
            print("🎉 ¡Carga de ventana principal completada exitosamente!")

        except Exception as e:
            self.logger.error(f"Error mostrando ventana principal: {e}")
            print(f"❌ Error crítico mostrando ventana principal: {e}")
            import traceback
            traceback.print_exc()

            # Mostrar error detallado
            error_details = f"Error mostrando ventana principal:\n{str(e)}\n\nRevisa la consola para más detalles."
            QMessageBox.critical(None, "Error Crítico", error_details)

    def run(self) -> int:
        """Ejecutar aplicación"""
        try:
            print("\n" + "=" * 60)
            print("🎓 INICIANDO ALFAIA - APLICACIÓN EDUCATIVA")
            print("=" * 60)

            # 1. Inicializar PyQt6
            print("\n📋 PASO 1: Inicializando PyQt6...")
            if not self.initialize_app():
                print("❌ Falló inicialización de PyQt6")
                return 1
            print("✅ PyQt6 inicializado correctamente")

            # 2. Inicializar base de datos
            print("\n📋 PASO 2: Inicializando base de datos...")
            if not self.initialize_database():
                print("❌ Falló inicialización de base de datos")
                return 1
            print("✅ Base de datos inicializada correctamente")

            # 3. Mostrar login
            print("\n📋 PASO 3: Mostrando ventana de login...")
            if not self.show_login_window():
                print("❌ Falló carga de ventana de login")
                return 1
            print("✅ Ventana de login mostrada correctamente")

            # 4. Ejecutar aplicación
            print("\n📋 PASO 4: Iniciando loop de eventos...")
            self.logger.info("AlfaIA iniciado exitosamente")
            print("🎉 ¡AlfaIA listo para usar!")
            print("💡 Usa las credenciales que creaste o crea una cuenta nueva")
            print("-" * 60)

            return self.app.exec()

        except Exception as e:
            self.logger.error(f"Error ejecutando aplicación: {e}")
            print(f"❌ Error fatal ejecutando aplicación: {e}")
            import traceback
            traceback.print_exc()

            self.hide_splash_screen()
            QMessageBox.critical(None, "Error Fatal", f"Error inesperado:\n{str(e)}")
            return 1

    def cleanup(self):
        """Limpiar recursos"""
        try:
            print("🧹 Iniciando limpieza de recursos...")

            self.hide_splash_screen()

            if self.main_window:
                print("🏠 Cerrando ventana principal...")
                self.main_window.close()

            if self.login_window:
                print("🔑 Cerrando ventana de login...")
                self.login_window.close()

            # Logout del auth_manager
            print("👤 Cerrando sesión...")
            try:
                auth_manager.logout()
            except Exception as e:
                print(f"⚠️ Error en logout: {e}")

            self.logger.info("Recursos limpiados")
            print("✅ Limpieza de recursos completada")

        except Exception as e:
            self.logger.error(f"Error en cleanup: {e}")
            print(f"⚠️ Error en limpieza: {e}")


def show_startup_info():
    """Mostrar información de inicio"""
    print("🔧 Información del sistema:")
    print(f"   Python: {sys.version}")
    print(f"   Plataforma: {sys.platform}")
    print(f"   Directorio: {Path(__file__).parent}")

    try:
        from PyQt6.QtCore import QT_VERSION_STR
        print(f"   PyQt6: {QT_VERSION_STR}")
    except:
        print("   PyQt6: No disponible")


def main():
    """Función principal"""
    print("=" * 50)
    print("🎓 ALFAIA - APLICACIÓN EDUCATIVA")
    print("=" * 50)

    show_startup_info()

    app = AlfaIAApplication()
    exit_code = 0

    try:
        exit_code = app.run()

    except KeyboardInterrupt:
        print("\n⚠️ Aplicación interrumpida por el usuario (Ctrl+C)")
        exit_code = 0

    except Exception as e:
        print(f"\n❌ Error fatal no manejado: {e}")
        import traceback
        traceback.print_exc()
        exit_code = 1

    finally:
        app.cleanup()
        print(f"\n🏁 AlfaIA terminado con código: {exit_code}")
        if exit_code == 0:
            print("✅ Salida limpia")
        else:
            print("❌ Salida con errores - revisa los logs")

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
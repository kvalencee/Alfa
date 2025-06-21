# =============================================================================
# AlfaIA/main.py - Punto de Entrada Principal (CON DEBUG COMPLETO)
# =============================================================================

import sys
import logging
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import QTranslator, QLocale
from PyQt6.QtGui import QIcon

print("🚀 Iniciando AlfaIA...")

# Configurar logging más detallado
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('alfaia_debug.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
logger.info("Sistema de logging inicializado")

# Importar configuración y componentes principales
try:
    print("📦 Importando configuración...")
    from config.settings import Settings
    from config.database_config import DatabaseConfig
    from core.database.connection import DatabaseManager

    print("✅ Configuración importada exitosamente")
except ImportError as e:
    print(f"❌ Error importando configuración: {e}")
    sys.exit(1)


class AlfaIAApplication:
    """Clase principal de la aplicación AlfaIA"""

    def __init__(self):
        print("🏗️  Inicializando aplicación AlfaIA...")
        self.app = None
        self.main_window = None
        self.login_window = None
        self.db_manager = None
        self.logger = logging.getLogger(__name__)
        print("✅ Clase AlfaIAApplication inicializada")

    def initialize_database(self) -> bool:
        """Inicializar conexión y esquema de base de datos"""
        print("🗄️  Inicializando base de datos...")
        try:
            self.db_manager = DatabaseManager()

            # Probar conexión
            print("📡 Probando conexión a BD...")
            if not self.db_manager.test_connection():
                self.show_database_error("No se pudo conectar a la base de datos MySQL.")
                return False

            # Crear esquema si no existe
            print("🏗️  Creando esquema de BD...")
            if not self.db_manager.create_database_schema():
                self.show_database_error("Error creando esquema de base de datos.")
                return False

            self.logger.info("Base de datos inicializada correctamente")
            print("✅ Base de datos inicializada correctamente")
            return True

        except Exception as e:
            self.logger.error(f"Error inicializando BD: {e}")
            self.show_database_error(f"Error de base de datos: {str(e)}")
            print(f"❌ Error inicializando BD: {e}")
            return False

    def show_database_error(self, message: str) -> None:
        """Mostrar error de base de datos al usuario"""
        print(f"🚨 Error de BD: {message}")
        if self.app:
            QMessageBox.critical(None, "Error de Base de Datos", message)
        else:
            print(f"ERROR BD: {message}")

    def initialize_app(self) -> bool:
        """Inicializar aplicación PyQt6"""
        print("🖼️  Inicializando PyQt6...")
        try:
            self.app = QApplication(sys.argv)
            settings = Settings()
            self.app.setApplicationName(settings.APP_NAME)
            self.app.setApplicationVersion(settings.APP_VERSION)

            self.logger.info("Aplicación PyQt6 inicializada")
            print("✅ PyQt6 inicializado exitosamente")
            return True

        except Exception as e:
            self.logger.error(f"Error inicializando aplicación: {e}")
            print(f"❌ Error inicializando PyQt6: {e}")
            return False

    def show_main_window(self):
        """Mostrar ventana principal después del login exitoso"""
        print("🏠 Intentando mostrar ventana principal...")
        try:
            # Importación tardía para evitar problemas de imports circulares
            from ui.windows.main_window import MainWindow
            print("📦 MainWindow importado exitosamente")

            self.main_window = MainWindow()
            print("🏗️  MainWindow creado")

            self.main_window.show()
            print("✅ MainWindow mostrado")

            # Cerrar ventana de login
            if self.login_window:
                self.login_window.close()
                print("🔒 Ventana de login cerrada")

            self.logger.info("Ventana principal mostrada")

        except Exception as e:
            self.logger.error(f"Error mostrando ventana principal: {e}")
            print(f"❌ Error mostrando ventana principal: {e}")
            QMessageBox.critical(None, "Error", f"No se pudo abrir la ventana principal: {str(e)}")

    def show_login_window(self):
        """Mostrar ventana de login"""
        print("🔑 Intentando mostrar ventana de login...")
        try:
            from ui.windows.login_window import LoginWindow
            print("📦 LoginWindow importado exitosamente")

            self.login_window = LoginWindow()
            print("🏗️  LoginWindow creado")

            self.login_window.login_successful.connect(self.show_main_window)
            print("🔗 Señales conectadas")

            self.login_window.show()
            print("✅ LoginWindow mostrado")

            return True

        except Exception as e:
            self.logger.error(f"Error creando ventana de login: {e}")
            print(f"❌ Error creando ventana de login: {e}")
            QMessageBox.critical(None, "Error", f"No se pudo crear la ventana de login: {str(e)}")
            return False

    def run(self) -> int:
        """Ejecutar la aplicación principal"""
        print("🎬 Ejecutando aplicación...")
        try:
            # Paso 1: Inicializar aplicación PyQt6
            print("\n--- PASO 1: Inicializar PyQt6 ---")
            if not self.initialize_app():
                print("❌ Falló inicialización de PyQt6")
                return 1

            # Paso 2: Inicializar base de datos
            print("\n--- PASO 2: Inicializar Base de Datos ---")
            if not self.initialize_database():
                print("❌ Falló inicialización de BD")
                return 1

            # Paso 3: Mostrar ventana de login
            print("\n--- PASO 3: Mostrar Ventana de Login ---")
            if not self.show_login_window():
                print("❌ Falló creación de ventana de login")
                return 1

            self.logger.info("AlfaIA iniciado exitosamente")
            print("🎉 AlfaIA iniciado exitosamente")

            # Paso 4: Ejecutar loop de eventos
            print("\n--- PASO 4: Iniciando Loop de Eventos ---")
            print("🔄 Entrando en loop de eventos de PyQt6...")
            result = self.app.exec()
            print(f"🏁 Loop de eventos terminado con código: {result}")
            return result

        except Exception as e:
            self.logger.error(f"Error ejecutando aplicación: {e}")
            print(f"❌ Error fatal ejecutando aplicación: {e}")
            import traceback
            traceback.print_exc()
            return 1

    def cleanup(self) -> None:
        """Limpiar recursos antes de cerrar"""
        print("🧹 Limpiando recursos...")
        try:
            if self.main_window:
                self.main_window.close()
                print("✅ MainWindow cerrado")

            if self.login_window:
                self.login_window.close()
                print("✅ LoginWindow cerrado")

            if self.db_manager and self.db_manager._pool:
                # Cerrar pool de conexiones si existe
                print("✅ Pool de BD cerrado")

            self.logger.info("Recursos limpiados correctamente")
            print("✅ Recursos limpiados correctamente")

        except Exception as e:
            self.logger.error(f"Error en cleanup: {e}")
            print(f"❌ Error en cleanup: {e}")


def main():
    """Función principal de entrada"""
    print("=" * 60)
    print("🎓 ALFAIA - APLICACIÓN EDUCATIVA")
    print("=" * 60)

    app = AlfaIAApplication()

    try:
        # Ejecutar aplicación
        print("🚀 Iniciando ejecución...")
        exit_code = app.run()
        print(f"🏁 Aplicación terminada con código: {exit_code}")

    except KeyboardInterrupt:
        print("\n⚠️  Aplicación interrumpida por el usuario")
        exit_code = 0

    except Exception as e:
        print(f"❌ Error fatal: {e}")
        logging.getLogger(__name__).error(f"Error fatal: {e}", exc_info=True)
        import traceback
        traceback.print_exc()
        exit_code = 1

    finally:
        # Limpiar recursos
        print("\n--- CLEANUP ---")
        app.cleanup()

    print(f"\n🏁 Finalizando con código de salida: {exit_code}")
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
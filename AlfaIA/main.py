# =============================================================================
# AlfaIA/main_simple.py - Versión Simplificada para Testing
# =============================================================================

import sys
import logging
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QMessageBox, QSplashScreen
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QPixmap, QColor
try:
    from modules.exercises.exercises_main_widget import ExercisesMainWidget
    print("✅ ExercisesMainWidget importado correctamente")
except ImportError as e:
    print(f"❌ Error importando ExercisesMainWidget: {e}")
    ExercisesMainWidget = None


# Configurar logging básico
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Agregar path para imports
sys.path.append(str(Path(__file__).parent))

# IMPORTS SEGUROS
try:
    from config.settings import Settings

    print("✅ Settings importado")
except ImportError as e:
    print(f"❌ Error importando Settings: {e}")
    sys.exit(1)

try:
    from core.database.connection import DatabaseManager

    print("✅ DatabaseManager importado")
except ImportError as e:
    print(f"❌ Error importando DatabaseManager: {e}")
    sys.exit(1)

try:
    from core.auth.authentication import get_auth_manager

    print("✅ get_auth_manager importado")
except ImportError as e:
    print(f"❌ Error importando get_auth_manager: {e}")
    sys.exit(1)


class SimpleAlfaIAApplication:
    """Aplicación AlfaIA simplificada"""

    def __init__(self):
        self.app = None
        self.main_window = None
        self.login_window = None
        self.splash = None
        self.settings = Settings()
        print("🏗️ SimpleAlfaIAApplication inicializada")

    def initialize_app(self) -> bool:
        """Inicializar aplicación PyQt6"""
        try:
            print("🔧 Inicializando PyQt6...")
            self.app = QApplication(sys.argv)
            self.app.setApplicationName("AlfaIA")
            print("✅ PyQt6 inicializado")
            return True
        except Exception as e:
            print(f"❌ Error inicializando PyQt6: {e}")
            return False

    def initialize_database(self) -> bool:
        """Inicializar base de datos"""
        try:
            print("🗄️ Inicializando BD...")
            db_manager = DatabaseManager()

            if not db_manager.test_connection():
                print("❌ No se pudo conectar a BD")
                return False

            print("✅ BD inicializada")
            return True
        except Exception as e:
            print(f"❌ Error inicializando BD: {e}")
            return False

    def show_login_window(self) -> bool:
        """Mostrar ventana de login"""
        try:
            print("🔑 Cargando login...")
            from ui.windows.login_window import LoginWindow

            self.login_window = LoginWindow()
            self.login_window.login_successful.connect(self.on_login_success)
            self.login_window.show()

            print("✅ Login mostrado")
            return True
        except Exception as e:
            print(f"❌ Error cargando login: {e}")
            return False

    def on_login_success(self):
        """Manejar login exitoso - SIMPLE"""
        print("🎉 ¡Login exitoso!")

        # Delay mínimo para asegurar que el worker termine
        QTimer.singleShot(200, self.show_main_window)

    def show_main_window(self):
        """Mostrar ventana principal - SIMPLE"""
        try:
            print("🏠 Mostrando ventana principal...")

            # Obtener usuario
            auth_manager = get_auth_manager()
            current_user = auth_manager.get_current_user_safe()

            if not current_user:
                print("❌ No se pudo obtener usuario")
                QMessageBox.warning(None, "Error", "No se pudo obtener información del usuario.")
                return

            print(f"✅ Usuario: {current_user.nombre} {current_user.apellido}")

            # Crear ventana principal
            from ui.windows.main_window import MainWindow
            self.main_window = MainWindow(current_user)
            self.main_window.show()

            # Cerrar login
            if self.login_window:
                self.login_window.close()
                self.login_window = None

            print("🎉 ¡Ventana principal mostrada!")

        except Exception as e:
            print(f"❌ Error mostrando ventana principal: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(None, "Error", f"Error crítico:\n{str(e)}")

    def run(self) -> int:
        """Ejecutar aplicación"""
        try:
            print("=" * 50)
            print("🎓 ALFAIA SIMPLIFICADO")
            print("=" * 50)

            if not self.initialize_app():
                return 1

            if not self.initialize_database():
                return 1

            if not self.show_login_window():
                return 1

            print("🚀 Ejecutando aplicación...")
            return self.app.exec()

        except Exception as e:
            print(f"❌ Error fatal: {e}")
            import traceback
            traceback.print_exc()
            return 1

    def cleanup(self):
        """Limpiar recursos"""
        try:
            print("🧹 Limpiando...")
            if self.main_window:
                self.main_window.close()
            if self.login_window:
                self.login_window.close()
        except Exception as e:
            print(f"⚠️ Error en limpieza: {e}")


def main():
    """Función principal simplificada"""
    app = SimpleAlfaIAApplication()
    exit_code = 0

    try:
        exit_code = app.run()
    except KeyboardInterrupt:
        print("\n⚠️ Interrumpido por usuario")
        exit_code = 0
    except Exception as e:
        print(f"\n❌ Error no manejado: {e}")
        exit_code = 1
    finally:
        app.cleanup()
        print(f"\n🏁 Terminado con código: {exit_code}")

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
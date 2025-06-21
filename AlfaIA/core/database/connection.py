# =============================================================================
# AlfaIA/core/database/connection.py - Gestor de Conexión a MySQL
# =============================================================================

import mysql.connector
from mysql.connector import pooling, Error
from typing import Optional, Dict, Any, List
import logging
from pathlib import Path
import sys

# Agregar directorio padre al path para imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from config.database_config import DatabaseConfig


class DatabaseManager:
    """Gestor de conexiones a la base de datos MySQL"""

    _instance = None
    _pool = None

    def __new__(cls):
        """Singleton pattern para el gestor de BD"""
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """Inicializar el gestor de base de datos"""
        if not hasattr(self, 'initialized'):
            self.logger = logging.getLogger(__name__)
            self.config = DatabaseConfig()
            self.initialized = True

    def create_connection_pool(self) -> bool:
        """Crear pool de conexiones a MySQL"""
        try:
            pool_config = self.config.get_connection_dict()
            pool_config.update(self.config.POOL_CONFIG)

            self._pool = pooling.MySQLConnectionPool(**pool_config)
            self.logger.info("Pool de conexiones creado exitosamente")
            return True

        except Error as e:
            self.logger.error(f"Error creando pool de conexiones: {e}")
            return False

    def get_connection(self):
        """Obtener conexión del pool"""
        try:
            if self._pool is None:
                if not self.create_connection_pool():
                    return None

            connection = self._pool.get_connection()
            return connection

        except Error as e:
            self.logger.error(f"Error obteniendo conexión: {e}")
            return None

    def test_connection(self) -> bool:
        """Probar la conexión a la base de datos"""
        try:
            connection = self.get_connection()
            if connection is None:
                return False

            cursor = connection.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()

            cursor.close()
            connection.close()

            return result is not None

        except Error as e:
            self.logger.error(f"Error probando conexión: {e}")
            return False

    def execute_query(self, query: str, params: tuple = None) -> Optional[List[tuple]]:
        """Ejecutar query SELECT y retornar resultados"""
        try:
            connection = self.get_connection()
            if connection is None:
                return None

            cursor = connection.cursor()
            cursor.execute(query, params or ())
            results = cursor.fetchall()

            cursor.close()
            connection.close()

            return results

        except Error as e:
            self.logger.error(f"Error ejecutando query: {e}")
            return None

    def execute_non_query(self, query: str, params: tuple = None) -> bool:
        """Ejecutar query INSERT/UPDATE/DELETE"""
        try:
            connection = self.get_connection()
            if connection is None:
                return False

            cursor = connection.cursor()
            cursor.execute(query, params or ())
            connection.commit()

            cursor.close()
            connection.close()

            return True

        except Error as e:
            self.logger.error(f"Error ejecutando non-query: {e}")
            return False

    def create_database_schema(self) -> bool:
        """Crear esquema completo de la base de datos"""
        try:
            # SQL para crear todas las tablas según especificaciones
            tables_sql = {
                "usuarios": """
                            CREATE TABLE IF NOT EXISTS usuarios
                            (
                                id                 INT PRIMARY KEY AUTO_INCREMENT,
                                email              VARCHAR(255) UNIQUE NOT NULL,
                                password_hash      VARCHAR(255)        NOT NULL,
                                nombre             VARCHAR(100)        NOT NULL,
                                apellido           VARCHAR(100)        NOT NULL,
                                fecha_nacimiento   DATE,
                                nivel_inicial      ENUM ('Principiante', 'Intermedio', 'Avanzado') DEFAULT 'Principiante',
                                rol                ENUM ('Estudiante', 'Tutor', 'Administrador')   DEFAULT 'Estudiante',
                                activo             BOOLEAN                                         DEFAULT TRUE,
                                fecha_registro     TIMESTAMP                                       DEFAULT CURRENT_TIMESTAMP,
                                configuracion_json JSON,
                                INDEX idx_email (email),
                                INDEX idx_activo (activo)
                            ) ENGINE = InnoDB
                              CHARSET = utf8mb4
                              COLLATE = utf8mb4_unicode_ci;
                            """,

                "perfiles_usuario": """
                                    CREATE TABLE IF NOT EXISTS perfiles_usuario
                                    (
                                        id                         INT PRIMARY KEY AUTO_INCREMENT,
                                        user_id                    INT NOT NULL,
                                        nivel_lectura              INT                                                 DEFAULT 1 CHECK (nivel_lectura BETWEEN 1 AND 10),
                                        nivel_gramatica            INT                                                 DEFAULT 1 CHECK (nivel_gramatica BETWEEN 1 AND 10),
                                        nivel_vocabulario          INT                                                 DEFAULT 1 CHECK (nivel_vocabulario BETWEEN 1 AND 10),
                                        puntos_totales             INT                                                 DEFAULT 0,
                                        experiencia_total          INT                                                 DEFAULT 0,
                                        racha_dias_consecutivos    INT                                                 DEFAULT 0,
                                        tiempo_total_minutos       INT                                                 DEFAULT 0,
                                        ejercicios_completados     INT                                                 DEFAULT 0,
                                        objetivo_diario_ejercicios INT                                                 DEFAULT 5,
                                        estilo_aprendizaje         ENUM ('Visual', 'Auditivo', 'Kinestésico', 'Mixto') DEFAULT 'Mixto',
                                        preferencias_json          JSON,
                                        estadisticas_json          JSON,
                                        FOREIGN KEY (user_id) REFERENCES usuarios (id) ON DELETE CASCADE,
                                        INDEX idx_user_id (user_id)
                                    ) ENGINE = InnoDB
                                      CHARSET = utf8mb4
                                      COLLATE = utf8mb4_unicode_ci;
                                    """,

                "categorias": """
                              CREATE TABLE IF NOT EXISTS categorias
                              (
                                  id             INT PRIMARY KEY AUTO_INCREMENT,
                                  nombre         VARCHAR(100) NOT NULL,
                                  descripcion    TEXT,
                                  icono          VARCHAR(100),
                                  color_hex      VARCHAR(7) DEFAULT '#4A90E2',
                                  nivel_minimo   INT        DEFAULT 1 CHECK (nivel_minimo BETWEEN 1 AND 10),
                                  nivel_maximo   INT        DEFAULT 10 CHECK (nivel_maximo BETWEEN 1 AND 10),
                                  activa         BOOLEAN    DEFAULT TRUE,
                                  metadatos_json JSON,
                                  INDEX idx_activa (activa),
                                  INDEX idx_nivel (nivel_minimo, nivel_maximo)
                              ) ENGINE = InnoDB
                                CHARSET = utf8mb4
                                COLLATE = utf8mb4_unicode_ci;
                              """,

                "ejercicios": """
                              CREATE TABLE IF NOT EXISTS ejercicios
                              (
                                  id                        INT PRIMARY KEY AUTO_INCREMENT,
                                  tipo                      ENUM ('Completar_Palabra', 'Encontrar_Error', 'Clasificar_Palabra', 'Comprension', 'Ordenar_Frase') NOT NULL,
                                  titulo                    VARCHAR(255)                                                                                        NOT NULL,
                                  instrucciones             TEXT                                                                                                NOT NULL,
                                  contenido_json            JSON                                                                                                NOT NULL,
                                  respuestas_correctas_json JSON                                                                                                NOT NULL,
                                  explicaciones_json        JSON,
                                  categoria_id              INT,
                                  nivel_dificultad          INT     DEFAULT 1 CHECK (nivel_dificultad BETWEEN 1 AND 10),
                                  puntos_maximos            INT     DEFAULT 10,
                                  tiempo_limite_segundos    INT     DEFAULT 300,
                                  pistas_json               JSON,
                                  activo                    BOOLEAN DEFAULT TRUE,
                                  FOREIGN KEY (categoria_id) REFERENCES categorias (id) ON DELETE SET NULL,
                                  INDEX idx_tipo (tipo),
                                  INDEX idx_nivel (nivel_dificultad),
                                  INDEX idx_activo (activo)
                              ) ENGINE = InnoDB
                                CHARSET = utf8mb4
                                COLLATE = utf8mb4_unicode_ci;
                              """,

                "resultados_ejercicios": """
                                         CREATE TABLE IF NOT EXISTS resultados_ejercicios
                                         (
                                             id                      INT PRIMARY KEY AUTO_INCREMENT,
                                             user_id                 INT  NOT NULL,
                                             ejercicio_id            INT  NOT NULL,
                                             respuestas_usuario_json JSON NOT NULL,
                                             puntos_obtenidos        INT           DEFAULT 0,
                                             precision_porcentaje    DECIMAL(5, 2) DEFAULT 0.00,
                                             tiempo_segundos         INT           DEFAULT 0,
                                             completado              BOOLEAN       DEFAULT FALSE,
                                             fecha_intento           TIMESTAMP     DEFAULT CURRENT_TIMESTAMP,
                                             analisis_nlp_json       JSON,
                                             FOREIGN KEY (user_id) REFERENCES usuarios (id) ON DELETE CASCADE,
                                             FOREIGN KEY (ejercicio_id) REFERENCES ejercicios (id) ON DELETE CASCADE,
                                             INDEX idx_user_ejercicio (user_id, ejercicio_id),
                                             INDEX idx_fecha (fecha_intento)
                                         ) ENGINE = InnoDB
                                           CHARSET = utf8mb4
                                           COLLATE = utf8mb4_unicode_ci;
                                         """
            }

            # Crear tablas
            for table_name, sql in tables_sql.items():
                if self.execute_non_query(sql):
                    self.logger.info(f"Tabla {table_name} creada/verificada exitosamente")
                else:
                    self.logger.error(f"Error creando tabla {table_name}")
                    return False

            # Insertar datos iniciales si es necesario
            self._insert_initial_data()

            return True

        except Exception as e:
            self.logger.error(f"Error creando esquema de BD: {e}")
            return False

    def _insert_initial_data(self) -> None:
        """Insertar datos iniciales en la base de datos"""
        # Categorías iniciales
        categorias_iniciales = [
            ("Gramática Básica", "Ejercicios de gramática fundamental", "grammar", "#4A90E2", 1, 5),
            ("Vocabulario", "Ampliación de vocabulario", "vocabulary", "#7ED321", 1, 10),
            ("Comprensión Lectora", "Ejercicios de lectura y comprensión", "reading", "#F5A623", 3, 10),
            ("Ortografía", "Reglas de ortografía y acentuación", "spelling", "#9013FE", 1, 8)
        ]

        for categoria in categorias_iniciales:
            query = """
                    INSERT IGNORE INTO categorias (nombre, descripcion, icono, color_hex, nivel_minimo, nivel_maximo)
                    VALUES (%s, %s, %s, %s, %s, %s) \
                    """
            self.execute_non_query(query, categoria)


# =============================================================================
# AlfaIA/main.py - Punto de Entrada Principal
# =============================================================================

import sys
import logging
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import QTranslator, QLocale
from PyQt6.QtGui import QIcon

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('alfaia.log'),
        logging.StreamHandler()
    ]
)

# Importar configuración y componentes
from config import settings, db_config
from core.database.connection import DatabaseManager
from ui.windows.main_window import MainWindow


class AlfaIAApplication:
    """Clase principal de la aplicación AlfaIA"""

    def __init__(self):
        self.app = None
        self.main_window = None
        self.db_manager = None
        self.logger = logging.getLogger(__name__)

    def initialize_database(self) -> bool:
        """Inicializar conexión y esquema de base de datos"""
        try:
            self.db_manager = DatabaseManager()

            # Probar conexión
            if not self.db_manager.test_connection():
                self.show_database_error("No se pudo conectar a la base de datos MySQL.")
                return False

            # Crear esquema si no existe
            if not self.db_manager.create_database_schema():
                self.show_database_error("Error creando esquema de base de datos.")
                return False

            self.logger.info("Base de datos inicializada correctamente")
            return True

        except Exception as e:
            self.logger.error(f"Error inicializando BD: {e}")
            self.show_database_error(f"Error de base de datos: {str(e)}")
            return False

    def show_database_error(self, message: str) -> None:
        """Mostrar error de base de datos al usuario"""
        if self.app:
            QMessageBox.critical(None, "Error de Base de Datos", message)
        else:
            print(f"ERROR BD: {message}")

    def initialize_app(self) -> bool:
        """Inicializar aplicación PyQt6"""
        try:
            self.app = QApplication(sys.argv)
            self.app.setApplicationName(settings.APP_NAME)
            self.app.setApplicationVersion(settings.APP_VERSION)

            # Configurar icono de la aplicación
            # icon_path = settings.RESOURCES_DIR / "icon.png"
            # if icon_path.exists():
            #     self.app.setWindowIcon(QIcon(str(icon_path)))

            self.logger.info("Aplicación PyQt6 inicializada")
            return True

        except Exception as e:
            self.logger.error(f"Error inicializando aplicación: {e}")
            return False

    def show_main_window(self):
        """Mostrar ventana principal después del login exitoso"""
        try:
            from ui.windows.main_window import MainWindow
            self.main_window = MainWindow()
            self.main_window.show()

            # Cerrar ventana de login
            if hasattr(self, 'login_window'):
                self.login_window.close()

        except Exception as e:
            self.logger.error(f"Error mostrando ventana principal: {e}")

    def run(self) -> int:
        """Ejecutar la aplicación principal"""
        try:
            # Inicializar aplicación
            if not self.initialize_app():
                return 1

            # Inicializar base de datos
            if not self.initialize_database():
                return 1

            # Mostrar ventana de login primero
            from ui.windows.login_window import LoginWindow
            self.login_window = LoginWindow()
            self.login_window.login_successful.connect(self.show_main_window)
            self.login_window.show()

            self.logger.info("AlfaIA iniciado exitosamente")

            # Ejecutar loop de eventos
            return self.app.exec()

        except Exception as e:
            self.logger.error(f"Error ejecutando aplicación: {e}")
            return 1

    def cleanup(self) -> None:
        """Limpiar recursos antes de cerrar"""
        try:
            if self.main_window:
                self.main_window.close()

            if self.db_manager and self.db_manager._pool:
                # Cerrar pool de conexiones si existe
                pass

            self.logger.info("Recursos limpiados correctamente")

        except Exception as e:
            self.logger.error(f"Error en cleanup: {e}")


def main():
    """Función principal de entrada"""
    app = AlfaIAApplication()

    try:
        # Ejecutar aplicación
        exit_code = app.run()

    except KeyboardInterrupt:
        print("\n⚠️  Aplicación interrumpida por el usuario")
        exit_code = 0

    except Exception as e:
        print(f"❌ Error fatal: {e}")
        exit_code = 1

    finally:
        # Limpiar recursos
        app.cleanup()

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
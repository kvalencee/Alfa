# =============================================================================
# AlfaIA/core/database/connection.py - Gestor de Conexión a MySQL (CORREGIDO)
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

    def ensure_database_exists(self) -> bool:
        """Asegurar que la base de datos existe"""
        try:
            return self.config.create_database_if_not_exists()
        except Exception as e:
            self.logger.error(f"Error asegurando que existe la BD: {e}")
            return False

    def create_connection_pool(self) -> bool:
        """Crear pool de conexiones a MySQL"""
        try:
            if not self.ensure_database_exists():
                self.logger.error("No se pudo crear o verificar la base de datos")
                return False

            pool_config = self.config.get_connection_dict()
            safe_pool_config = {
                "pool_name": "alfaia_pool",
                "pool_size": 10,
                "pool_reset_session": True
            }

            pool_config.update(safe_pool_config)

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

            for table_name, sql in tables_sql.items():
                if self.execute_non_query(sql):
                    self.logger.info(f"Tabla {table_name} creada/verificada exitosamente")
                    print(f"✅ Tabla {table_name} creada/verificada")
                else:
                    self.logger.error(f"Error creando tabla {table_name}")
                    print(f"❌ Error creando tabla {table_name}")
                    return False

            self._insert_initial_data()
            return True

        except Exception as e:
            self.logger.error(f"Error creando esquema de BD: {e}")
            print(f"❌ Error creando esquema: {e}")
            return False

    def _insert_initial_data(self) -> None:
        """Insertar datos iniciales en la base de datos"""
        categorias_iniciales = [
            ("Gramática Básica", "Ejercicios de gramática fundamental", "grammar", "#4A90E2", 1, 5),
            ("Vocabulario", "Ampliación de vocabulario", "vocabulary", "#7ED321", 1, 10),
            ("Comprensión Lectora", "Ejercicios de lectura y comprensión", "reading", "#F5A623", 3, 10),
            ("Ortografía", "Reglas de ortografía y acentuación", "spelling", "#9013FE", 1, 8)
        ]

        for categoria in categorias_iniciales:
            query = """
                    INSERT IGNORE INTO categorias (nombre, descripcion, icono, color_hex, nivel_minimo, nivel_maximo)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """
            if self.execute_non_query(query, categoria):
                print(f"✅ Categoría '{categoria[0]}' insertada/verificada")


if __name__ == "__main__":
    print("🔧 Configurando base de datos AlfaIA...")

    db_manager = DatabaseManager()

    print("📡 Probando conexión...")
    if db_manager.test_connection():
        print("✅ Conexión exitosa")
    else:
        print("❌ Error de conexión")

    print("🏗️  Creando esquema...")
    if db_manager.create_database_schema():
        print("✅ Esquema creado exitosamente")
    else:
        print("❌ Error creando esquema")
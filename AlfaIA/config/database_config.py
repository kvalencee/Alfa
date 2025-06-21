# =============================================================================
# AlfaIA/config/database_config.py - Configuración de Base de Datos (CORREGIDA)
# =============================================================================

import os
from typing import Dict, Any


class DatabaseConfig:
    """Configuración de la base de datos MySQL"""

    # Configuración de conexión
    HOST = os.getenv("DB_HOST", "localhost")
    PORT = int(os.getenv("DB_PORT", "3306"))
    DATABASE = os.getenv("DB_NAME", "alfaia_db")
    USER = os.getenv("DB_USER", "root")
    PASSWORD = os.getenv("DB_PASSWORD", "tired2019")

    # Configuración de conexión corregida (sin parámetros incompatibles)
    CONNECTION_CONFIG = {
        "host": HOST,
        "port": PORT,
        "database": DATABASE,
        "user": USER,
        "password": PASSWORD,
        "charset": "utf8mb4",
        "collation": "utf8mb4_unicode_ci",
        "autocommit": True,
        "time_zone": "+00:00",
        "sql_mode": "STRICT_TRANS_TABLES,NO_ZERO_DATE,NO_ZERO_IN_DATE,ERROR_FOR_DIVISION_BY_ZERO",
        "connection_timeout": 60,
    }

    # Pool de conexiones
    POOL_CONFIG = {
        "pool_name": "alfaia_pool",
        "pool_size": 10,
        "pool_reset_session": True,
    }

    # Configuración de tablas
    TABLES_CONFIG = {
        "usuarios": {
            "engine": "InnoDB",
            "charset": "utf8mb4",
            "collation": "utf8mb4_unicode_ci"
        },
        "perfiles_usuario": {
            "engine": "InnoDB",
            "charset": "utf8mb4",
            "collation": "utf8mb4_unicode_ci"
        },
        "ejercicios": {
            "engine": "InnoDB",
            "charset": "utf8mb4",
            "collation": "utf8mb4_unicode_ci"
        },
        "resultados_ejercicios": {
            "engine": "InnoDB",
            "charset": "utf8mb4",
            "collation": "utf8mb4_unicode_ci"
        }
    }

    @classmethod
    def get_connection_string(cls) -> str:
        """Retorna string de conexión para MySQL"""
        return f"mysql+pymysql://{cls.USER}:{cls.PASSWORD}@{cls.HOST}:{cls.PORT}/{cls.DATABASE}"

    @classmethod
    def get_connection_dict(cls) -> Dict[str, Any]:
        """Retorna diccionario de configuración de conexión"""
        return cls.CONNECTION_CONFIG.copy()

    @classmethod
    def create_database_if_not_exists(cls) -> bool:
        """Crear la base de datos si no existe"""
        import mysql.connector
        from mysql.connector import Error

        try:
            connection_config = cls.CONNECTION_CONFIG.copy()
            connection_config.pop('database', None)

            connection = mysql.connector.connect(**connection_config)
            cursor = connection.cursor()

            cursor.execute(
                f"CREATE DATABASE IF NOT EXISTS {cls.DATABASE} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            print(f"✅ Base de datos '{cls.DATABASE}' creada o verificada exitosamente")

            cursor.close()
            connection.close()
            return True

        except Error as e:
            print(f"❌ Error creando base de datos: {e}")
            return False
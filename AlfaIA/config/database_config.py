# =============================================================================
# AlfaIA/config/database_config.py - Configuración de Base de Datos
# =============================================================================

import os
from pathlib import Path
from typing import Dict, List, Any, Tuple
from datetime import datetime

print("🔧 Cargando configuración de base de datos...")


class DatabaseConfig:
    """Configuración de base de datos para AlfaIA"""

    # =============================================================================
    # CONFIGURACIÓN PRINCIPAL DE BASE DE DATOS
    # =============================================================================

    DATABASE = {
        # Configuración de conexión
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': int(os.getenv('DB_PORT', 3306)),
        'database': os.getenv('DB_NAME', 'alfaia_db'),
        'user': os.getenv('DB_USER', 'alfaia_user'),
        'password': os.getenv('DB_PASSWORD', 'alfaia_password'),

        # Configuración de charset
        'charset': 'utf8mb4',
        'collation': 'utf8mb4_unicode_ci',

        # Configuración de conexión
        'autocommit': False,
        'time_zone': '+00:00',
        'sql_mode': 'STRICT_TRANS_TABLES,NO_ZERO_DATE,NO_ZERO_IN_DATE,ERROR_FOR_DIVISION_BY_ZERO',

        # Pool de conexiones
        'pool_size': 10,
        'pool_reset_session': True,
        'pool_name': 'alfaia_pool'
    }

    # =============================================================================
    # CONFIGURACIÓN DE TABLAS
    # =============================================================================

    # Scripts SQL para crear las tablas
    TABLE_SCHEMAS = {
        'usuarios': """
                    CREATE TABLE IF NOT EXISTS usuarios
                    (
                        id                 INT AUTO_INCREMENT PRIMARY KEY,
                        email              VARCHAR(255) UNIQUE NOT NULL,
                        password_hash      VARCHAR(255)        NOT NULL,
                        nombre             VARCHAR(100)        NOT NULL,
                        apellido           VARCHAR(100)        NOT NULL,
                        fecha_nacimiento   DATE,
                        nivel_inicial      ENUM ('principiante', 'basico', 'intermedio', 'avanzado') DEFAULT 'principiante',
                        rol                ENUM ('estudiante', 'profesor', 'administrador')          DEFAULT 'estudiante',
                        activo             BOOLEAN                                                   DEFAULT TRUE,
                        fecha_registro     TIMESTAMP                                                 DEFAULT CURRENT_TIMESTAMP,
                        ultima_conexion    TIMESTAMP           NULL,
                        configuracion_json TEXT,
                        INDEX idx_email (email),
                        INDEX idx_activo (activo),
                        INDEX idx_fecha_registro (fecha_registro)
                    ) ENGINE = InnoDB
                      DEFAULT CHARSET = utf8mb4
                      COLLATE = utf8mb4_unicode_ci;
                    """,

        'perfiles_usuario': """
                            CREATE TABLE IF NOT EXISTS perfiles_usuario
                            (
                                id                         INT AUTO_INCREMENT PRIMARY KEY,
                                user_id                    INT NOT NULL,
                                nivel_lectura              INT                                                 DEFAULT 1,
                                nivel_gramatica            INT                                                 DEFAULT 1,
                                nivel_vocabulario          INT                                                 DEFAULT 1,
                                puntos_totales             INT                                                 DEFAULT 0,
                                experiencia_total          INT                                                 DEFAULT 0,
                                racha_dias_consecutivos    INT                                                 DEFAULT 0,
                                tiempo_total_minutos       INT                                                 DEFAULT 0,
                                ejercicios_completados     INT                                                 DEFAULT 0,
                                objetivo_diario_ejercicios INT                                                 DEFAULT 5,
                                estilo_aprendizaje         ENUM ('visual', 'auditivo', 'kinestesico', 'mixto') DEFAULT 'mixto',
                                preferencias_json          TEXT,
                                estadisticas_json          TEXT,
                                fecha_creacion             TIMESTAMP                                           DEFAULT CURRENT_TIMESTAMP,
                                fecha_actualizacion        TIMESTAMP                                           DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                                FOREIGN KEY (user_id) REFERENCES usuarios (id) ON DELETE CASCADE,
                                UNIQUE KEY unique_user_profile (user_id),
                                INDEX idx_user_id (user_id),
                                INDEX idx_puntos (puntos_totales),
                                INDEX idx_nivel_lectura (nivel_lectura)
                            ) ENGINE = InnoDB
                              DEFAULT CHARSET = utf8mb4
                              COLLATE = utf8mb4_unicode_ci;
                            """,

        'ejercicios': """
                      CREATE TABLE IF NOT EXISTS ejercicios
                      (
                          id                  INT AUTO_INCREMENT PRIMARY KEY,
                          titulo              VARCHAR(255)                   NOT NULL,
                          descripcion         TEXT,
                          tipo_ejercicio      ENUM ('comprension_lectora', 'gramatica', 'vocabulario', 'ortografia',
                              'sinonimos_antonimos', 'ordenar_palabras', 'completar_oraciones',
                              'identificar_errores', 'analisis_morfologico') NOT NULL,
                          dificultad          ENUM ('principiante', 'basico', 'intermedio', 'avanzado', 'experto') DEFAULT 'intermedio',
                          nivel_educativo     ENUM ('primaria_inicial', 'primaria_media', 'primaria_superior',
                              'secundaria', 'universitario', 'profesional')                                        DEFAULT 'secundaria',
                          contenido_json      TEXT                           NOT NULL,
                          texto_fuente        TEXT,
                          puntos_maximos      INT                                                                  DEFAULT 0,
                          tiempo_estimado     INT                                                                  DEFAULT 0, -- en segundos
                          activo              BOOLEAN                                                              DEFAULT TRUE,
                          creado_por          INT,
                          fecha_creacion      TIMESTAMP                                                            DEFAULT CURRENT_TIMESTAMP,
                          fecha_actualizacion TIMESTAMP                                                            DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                          FOREIGN KEY (creado_por) REFERENCES usuarios (id) ON DELETE SET NULL,
                          INDEX idx_tipo (tipo_ejercicio),
                          INDEX idx_dificultad (dificultad),
                          INDEX idx_nivel_educativo (nivel_educativo),
                          INDEX idx_activo (activo)
                      ) ENGINE = InnoDB
                        DEFAULT CHARSET = utf8mb4
                        COLLATE = utf8mb4_unicode_ci;
                      """,

        'resultados_ejercicios': """
                                 CREATE TABLE IF NOT EXISTS resultados_ejercicios
                                 (
                                     id                   INT AUTO_INCREMENT PRIMARY KEY,
                                     user_id              INT         NOT NULL,
                                     ejercicio_id         INT,
                                     tipo_ejercicio       VARCHAR(50) NOT NULL,
                                     dificultad           VARCHAR(20) NOT NULL,
                                     puntuacion           DECIMAL(5, 2) DEFAULT 0.00,
                                     puntos_maximos       DECIMAL(5, 2) DEFAULT 0.00,
                                     porcentaje_acierto   DECIMAL(5, 2) DEFAULT 0.00,
                                     tiempo_empleado      INT           DEFAULT 0, -- en segundos
                                     respuestas_correctas INT           DEFAULT 0,
                                     total_preguntas      INT           DEFAULT 0,
                                     intentos             INT           DEFAULT 1,
                                     pistas_usadas        INT           DEFAULT 0,
                                     fecha_completado     TIMESTAMP     DEFAULT CURRENT_TIMESTAMP,
                                     datos_json           TEXT,                    -- Respuestas detalladas y análisis
                                     FOREIGN KEY (user_id) REFERENCES usuarios (id) ON DELETE CASCADE,
                                     FOREIGN KEY (ejercicio_id) REFERENCES ejercicios (id) ON DELETE SET NULL,
                                     INDEX idx_user_id (user_id),
                                     INDEX idx_ejercicio_id (ejercicio_id),
                                     INDEX idx_tipo_ejercicio (tipo_ejercicio),
                                     INDEX idx_fecha_completado (fecha_completado),
                                     INDEX idx_puntuacion (puntuacion)
                                 ) ENGINE = InnoDB
                                   DEFAULT CHARSET = utf8mb4
                                   COLLATE = utf8mb4_unicode_ci;
                                 """,

        'sesiones_usuario': """
                            CREATE TABLE IF NOT EXISTS sesiones_usuario
                            (
                                id               INT AUTO_INCREMENT PRIMARY KEY,
                                user_id          INT                 NOT NULL,
                                token_sesion     VARCHAR(255) UNIQUE NOT NULL,
                                fecha_inicio     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                fecha_expiracion TIMESTAMP           NOT NULL,
                                ip_address       VARCHAR(45),
                                user_agent       TEXT,
                                activa           BOOLEAN   DEFAULT TRUE,
                                FOREIGN KEY (user_id) REFERENCES usuarios (id) ON DELETE CASCADE,
                                INDEX idx_user_id (user_id),
                                INDEX idx_token (token_sesion),
                                INDEX idx_activa (activa),
                                INDEX idx_expiracion (fecha_expiracion)
                            ) ENGINE = InnoDB
                              DEFAULT CHARSET = utf8mb4
                              COLLATE = utf8mb4_unicode_ci;
                            """,

        'logros': """
                  CREATE TABLE IF NOT EXISTS logros
                  (
                      id                INT AUTO_INCREMENT PRIMARY KEY,
                      nombre            VARCHAR(100)                                                 NOT NULL,
                      descripcion       TEXT                                                         NOT NULL,
                      icono             VARCHAR(50) DEFAULT '🏆',
                      tipo_logro        ENUM ('ejercicios', 'puntos', 'racha', 'tiempo', 'especial') NOT NULL,
                      criterio_json     TEXT                                                         NOT NULL, -- Criterios para obtener el logro
                      puntos_recompensa INT         DEFAULT 0,
                      activo            BOOLEAN     DEFAULT TRUE,
                      fecha_creacion    TIMESTAMP   DEFAULT CURRENT_TIMESTAMP,
                      INDEX idx_tipo (tipo_logro),
                      INDEX idx_activo (activo)
                  ) ENGINE = InnoDB
                    DEFAULT CHARSET = utf8mb4
                    COLLATE = utf8mb4_unicode_ci;
                  """,

        'logros_usuario': """
                          CREATE TABLE IF NOT EXISTS logros_usuario
                          (
                              id                INT AUTO_INCREMENT PRIMARY KEY,
                              user_id           INT NOT NULL,
                              logro_id          INT NOT NULL,
                              fecha_obtenido    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                              datos_adicionales TEXT, -- Información específica del logro
                              FOREIGN KEY (user_id) REFERENCES usuarios (id) ON DELETE CASCADE,
                              FOREIGN KEY (logro_id) REFERENCES logros (id) ON DELETE CASCADE,
                              UNIQUE KEY unique_user_logro (user_id, logro_id),
                              INDEX idx_user_id (user_id),
                              INDEX idx_logro_id (logro_id),
                              INDEX idx_fecha (fecha_obtenido)
                          ) ENGINE = InnoDB
                            DEFAULT CHARSET = utf8mb4
                            COLLATE = utf8mb4_unicode_ci;
                          """,

        'configuracion_sistema': """
                                 CREATE TABLE IF NOT EXISTS configuracion_sistema
                                 (
                                     id                  INT AUTO_INCREMENT PRIMARY KEY,
                                     clave               VARCHAR(100) UNIQUE NOT NULL,
                                     valor               TEXT,
                                     descripcion         TEXT,
                                     tipo_dato           ENUM ('string', 'int', 'float', 'boolean', 'json') DEFAULT 'string',
                                     categoria           VARCHAR(50)                                        DEFAULT 'general',
                                     fecha_actualizacion TIMESTAMP                                          DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                                     INDEX idx_clave (clave),
                                     INDEX idx_categoria (categoria)
                                 ) ENGINE = InnoDB
                                   DEFAULT CHARSET = utf8mb4
                                   COLLATE = utf8mb4_unicode_ci;
                                 """
    }

    # =============================================================================
    # DATOS INICIALES
    # =============================================================================

    INITIAL_DATA = {
        'usuarios': [
            {
                'email': 'admin@alfaia.com',
                'password_hash': '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBdXzgVryZgfHi',  # admin123
                'nombre': 'Administrador',
                'apellido': 'Sistema',
                'fecha_nacimiento': '1990-01-01',
                'nivel_inicial': 'avanzado',
                'rol': 'administrador'
            },
            {
                'email': 'test@alfaia.com',
                'password_hash': '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPjiCnlqa',  # test123
                'nombre': 'Usuario',
                'apellido': 'Prueba',
                'fecha_nacimiento': '2000-06-15',
                'nivel_inicial': 'principiante',
                'rol': 'estudiante'
            }
        ],

        'logros': [
            {
                'nombre': 'Primer Paso',
                'descripcion': 'Completa tu primer ejercicio',
                'icono': '🎯',
                'tipo_logro': 'ejercicios',
                'criterio_json': '{"ejercicios_completados": 1}',
                'puntos_recompensa': 50
            },
            {
                'nombre': 'Estudioso',
                'descripcion': 'Completa 10 ejercicios',
                'icono': '📚',
                'tipo_logro': 'ejercicios',
                'criterio_json': '{"ejercicios_completados": 10}',
                'puntos_recompensa': 200
            },
            {
                'nombre': 'Experto',
                'descripcion': 'Completa 50 ejercicios',
                'icono': '🏆',
                'tipo_logro': 'ejercicios',
                'criterio_json': '{"ejercicios_completados": 50}',
                'puntos_recompensa': 500
            },
            {
                'nombre': 'Constancia',
                'descripcion': 'Mantén una racha de 7 días',
                'icono': '🔥',
                'tipo_logro': 'racha',
                'criterio_json': '{"racha_dias": 7}',
                'puntos_recompensa': 300
            },
            {
                'nombre': 'Millonario',
                'descripcion': 'Acumula 1000 puntos',
                'icono': '💰',
                'tipo_logro': 'puntos',
                'criterio_json': '{"puntos_totales": 1000}',
                'puntos_recompensa': 100
            }
        ],

        'configuracion_sistema': [
            {
                'clave': 'version_app',
                'valor': '1.0.0',
                'descripcion': 'Versión actual de la aplicación',
                'tipo_dato': 'string',
                'categoria': 'sistema'
            },
            {
                'clave': 'puntos_por_ejercicio_basico',
                'valor': '10',
                'descripcion': 'Puntos base por ejercicio básico',
                'tipo_dato': 'int',
                'categoria': 'gamificacion'
            },
            {
                'clave': 'tiempo_sesion_minutos',
                'valor': '120',
                'descripcion': 'Tiempo de duración de sesión en minutos',
                'tipo_dato': 'int',
                'categoria': 'seguridad'
            },
            {
                'clave': 'ejercicios_diarios_default',
                'valor': '5',
                'descripcion': 'Objetivo diario por defecto de ejercicios',
                'tipo_dato': 'int',
                'categoria': 'educacion'
            },
            {
                'clave': 'nivel_dificultad_auto',
                'valor': 'true',
                'descripcion': 'Ajuste automático de dificultad habilitado',
                'tipo_dato': 'boolean',
                'categoria': 'educacion'
            }
        ]
    }

    # =============================================================================
    # CONFIGURACIÓN DE ÍNDICES Y OPTIMIZACIÓN
    # =============================================================================

    OPTIMIZATION_QUERIES = [
        "SET GLOBAL innodb_buffer_pool_size = 268435456;",  # 256MB
        "SET GLOBAL query_cache_size = 67108864;",  # 64MB
        "SET GLOBAL tmp_table_size = 67108864;",  # 64MB
        "SET GLOBAL max_heap_table_size = 67108864;",  # 64MB
    ]

    # Configuración de respaldos
    BACKUP_CONFIG = {
        'auto_backup': True,
        'backup_interval_hours': 24,
        'backup_retention_days': 30,
        'backup_path': './backups/',
        'compress_backups': True
    }


# =============================================================================
# FUNCIONES DE UTILIDAD
# =============================================================================

def get_database_config() -> Dict[str, Any]:
    """Obtener configuración de base de datos"""
    return DatabaseConfig.DATABASE


def get_table_schemas() -> Dict[str, str]:
    """Obtener esquemas de todas las tablas"""
    return DatabaseConfig.TABLE_SCHEMAS


def get_initial_data() -> Dict[str, List[Dict]]:
    """Obtener datos iniciales para las tablas"""
    return DatabaseConfig.INITIAL_DATA


# =============================================================================
# VERIFICACIÓN DE CONFIGURACIÓN
# =============================================================================

def validate_config() -> Tuple[bool, List[str]]:
    """
    Validar configuración de base de datos

    Returns:
        Tuple[bool, List[str]]: (es_válida, lista_de_errores)
    """
    errors = []
    config = DatabaseConfig.DATABASE

    # Validar campos requeridos
    required_fields = ['host', 'port', 'database', 'user', 'password']
    for field in required_fields:
        if not config.get(field):
            errors.append(f"Campo requerido faltante: {field}")

    # Validar tipos de datos
    if not isinstance(config.get('port'), int):
        errors.append("El puerto debe ser un número entero")

    if config.get('port', 0) < 1 or config.get('port', 0) > 65535:
        errors.append("El puerto debe estar entre 1 y 65535")

    # Validar pool size
    pool_size = config.get('pool_size', 10)
    if not isinstance(pool_size, int) or pool_size < 1 or pool_size > 100:
        errors.append("El tamaño del pool debe ser entre 1 y 100")

    return len(errors) == 0, errors


if __name__ == "__main__":
    print("🧪 Verificando configuración de base de datos...")

    # Validar configuración
    is_valid, errors = validate_config()

    if is_valid:
        print("✅ Configuración de base de datos válida")

        config = get_database_config()
        print(f"📊 Configuración cargada:")
        print(f"  Host: {config['host']}:{config['port']}")
        print(f"  Base de datos: {config['database']}")
        print(f"  Usuario: {config['user']}")
        print(f"  Pool size: {config['pool_size']}")
        print(f"  Charset: {config['charset']}")

        print(f"\n📋 Tablas definidas:")
        tables = get_table_schemas()
        for table_name in tables.keys():
            print(f"  • {table_name}")

        print(f"\n📦 Datos iniciales:")
        initial_data = get_initial_data()
        for table_name, data in initial_data.items():
            print(f"  • {table_name}: {len(data)} registros")

    else:
        print("❌ Configuración de base de datos inválida:")
        for error in errors:
            print(f"  • {error}")

    print("\n✅ Verificación completada")
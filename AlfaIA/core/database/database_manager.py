# =============================================================================
# AlfaIA/core/database/database_manager.py - Gestor Completo de Base de Datos
# =============================================================================

import mysql.connector
from mysql.connector import Error, pooling
import json
import logging
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass
from enum import Enum
import sys
from pathlib import Path
from datetime import datetime, timedelta
import threading
import time

# Agregar el directorio raíz al path para imports
sys.path.append(str(Path(__file__).parent.parent.parent))

# Imports de configuración y modelos
try:
    from config.settings import Settings
    from core.database.models import Usuario, PerfilUsuario, RolUsuario, NivelUsuario, EstiloAprendizaje

    MODELS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Algunos módulos no disponibles: {e}")
    MODELS_AVAILABLE = False


    # Definir configuración básica si no está disponible
    class Settings:
        DATABASE = {
            'host': 'localhost',
            'port': 3306,
            'database': 'alfaia_db',
            'user': 'alfaia_user',
            'password': 'alfaia_password'
        }

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print("🔧 Inicializando gestor de base de datos...")


# =============================================================================
# ENUMS Y DATACLASSES
# =============================================================================

class ConnectionStatus(Enum):
    """Estados de conexión de la base de datos"""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"
    RECONNECTING = "reconnecting"


class TransactionStatus(Enum):
    """Estados de transacciones"""
    PENDING = "pending"
    COMMITTED = "committed"
    ROLLED_BACK = "rolled_back"
    ERROR = "error"


@dataclass
class DatabaseStats:
    """Estadísticas de la base de datos"""
    total_connections: int
    active_connections: int
    total_queries: int
    successful_queries: int
    failed_queries: int
    average_query_time: float
    uptime: float
    last_backup: Optional[datetime]


@dataclass
class QueryResult:
    """Resultado de una consulta"""
    success: bool
    data: Any
    affected_rows: int
    execution_time: float
    error_message: Optional[str] = None


@dataclass
class BackupInfo:
    """Información de respaldo"""
    filename: str
    timestamp: datetime
    size_bytes: int
    tables_included: List[str]
    success: bool
    error_message: Optional[str] = None


# =============================================================================
# CLASE PRINCIPAL DEL GESTOR DE BASE DE DATOS
# =============================================================================

class DatabaseManager:
    """
    Gestor completo de base de datos para AlfaIA
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        """Implementar patrón Singleton thread-safe"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(DatabaseManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """Inicializar gestor de base de datos"""
        if hasattr(self, 'initialized'):
            return

        self.logger = logger
        self.settings = Settings()

        # Configuración de conexión con fallback
        if hasattr(self.settings, 'DATABASE'):
            self.db_config = self.settings.DATABASE
        else:
            # Importar configuración de base de datos
            try:
                from config.database_config import DatabaseConfig
                self.db_config = DatabaseConfig.DATABASE
                print("✅ Configuración de BD cargada desde database_config.py")
            except ImportError:
                # Configuración por defecto como último recurso
                self.db_config = {
                    'host': 'localhost',
                    'port': 3306,
                    'database': 'alfaia_db',
                    'user': 'alfaia_user',
                    'password': 'alfaia_password'
                }
                print("⚠️ Usando configuración de BD por defecto")
        self.connection_pool = None
        self.status = ConnectionStatus.DISCONNECTED

        # Estadísticas
        self.stats = DatabaseStats(
            total_connections=0,
            active_connections=0,
            total_queries=0,
            successful_queries=0,
            failed_queries=0,
            average_query_time=0.0,
            uptime=0.0,
            last_backup=None
        )

        # Control de transacciones
        self.active_transactions = {}
        self.transaction_lock = threading.Lock()

        # Inicialización
        self.start_time = datetime.now()
        self.initialized = True

        print("✅ DatabaseManager inicializado")

    def initialize_connection_pool(self, pool_size: int = 10) -> bool:
        """
        Inicializar pool de conexiones

        Args:
            pool_size: Tamaño del pool de conexiones

        Returns:
            bool: True si se inicializó correctamente
        """
        try:
            print(f"🔗 Inicializando pool de conexiones (tamaño: {pool_size})...")

            pool_config = {
                'pool_name': 'alfaia_pool',
                'pool_size': pool_size,
                'pool_reset_session': True,
                'host': self.db_config['host'],
                'port': self.db_config['port'],
                'database': self.db_config['database'],
                'user': self.db_config['user'],
                'password': self.db_config['password'],
                'charset': 'utf8mb4',
                'collation': 'utf8mb4_unicode_ci',
                'autocommit': False,
                'time_zone': '+00:00'
            }

            self.connection_pool = pooling.MySQLConnectionPool(**pool_config)
            self.status = ConnectionStatus.CONNECTED

            print("✅ Pool de conexiones inicializado exitosamente")
            return True

        except Error as e:
            error_msg = f"Error inicializando pool de conexiones: {e}"
            self.logger.error(error_msg)
            print(f"❌ {error_msg}")
            self.status = ConnectionStatus.ERROR
            return False

    def get_connection(self) -> Optional[mysql.connector.MySQLConnection]:
        """
        Obtener conexión del pool

        Returns:
            MySQLConnection o None si hay error
        """
        try:
            if self.connection_pool is None:
                if not self.initialize_connection_pool():
                    return None

            connection = self.connection_pool.get_connection()
            self.stats.total_connections += 1
            self.stats.active_connections += 1

            return connection

        except Error as e:
            self.logger.error(f"Error obteniendo conexión: {e}")
            return None

    def release_connection(self, connection: mysql.connector.MySQLConnection):
        """
        Liberar conexión de vuelta al pool

        Args:
            connection: Conexión a liberar
        """
        try:
            if connection and connection.is_connected():
                connection.close()
                self.stats.active_connections = max(0, self.stats.active_connections - 1)
        except Error as e:
            self.logger.error(f"Error liberando conexión: {e}")

    def test_connection(self) -> bool:
        """
        Probar conexión a la base de datos

        Returns:
            bool: True si la conexión es exitosa
        """
        try:
            print("🔍 Probando conexión a la base de datos...")

            connection = self.get_connection()
            if connection is None:
                return False

            cursor = connection.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()

            cursor.close()
            self.release_connection(connection)

            if result and result[0] == 1:
                print("✅ Conexión a la base de datos exitosa")
                return True
            else:
                print("❌ Respuesta inesperada de la base de datos")
                return False

        except Error as e:
            error_msg = f"Error probando conexión: {e}"
            self.logger.error(error_msg)
            print(f"❌ {error_msg}")
            return False

    def execute_query(self, query: str, params: Optional[Tuple] = None,
                      fetch_results: bool = True) -> QueryResult:
        """
        Ejecutar consulta SQL

        Args:
            query: Consulta SQL
            params: Parámetros de la consulta
            fetch_results: Si obtener resultados

        Returns:
            QueryResult: Resultado de la consulta
        """
        start_time = time.time()
        connection = None
        cursor = None

        try:
            self.stats.total_queries += 1

            connection = self.get_connection()
            if connection is None:
                raise Exception("No se pudo obtener conexión a la base de datos")

            cursor = connection.cursor(dictionary=True)

            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            # Obtener resultados si es necesario
            data = None
            if fetch_results:
                if query.strip().upper().startswith('SELECT'):
                    data = cursor.fetchall()
                else:
                    data = cursor.fetchone()

            affected_rows = cursor.rowcount
            connection.commit()

            execution_time = time.time() - start_time

            # Actualizar estadísticas
            self.stats.successful_queries += 1
            self._update_average_query_time(execution_time)

            return QueryResult(
                success=True,
                data=data,
                affected_rows=affected_rows,
                execution_time=execution_time
            )

        except Error as e:
            if connection:
                connection.rollback()

            execution_time = time.time() - start_time
            error_msg = f"Error ejecutando consulta: {e}"

            self.logger.error(error_msg)
            self.stats.failed_queries += 1

            return QueryResult(
                success=False,
                data=None,
                affected_rows=0,
                execution_time=execution_time,
                error_message=error_msg
            )

        finally:
            if cursor:
                cursor.close()
            if connection:
                self.release_connection(connection)

    def execute_transaction(self, queries: List[Tuple[str, Optional[Tuple]]]) -> QueryResult:
        """
        Ejecutar múltiples consultas en una transacción

        Args:
            queries: Lista de tuplas (consulta, parámetros)

        Returns:
            QueryResult: Resultado de la transacción
        """
        start_time = time.time()
        connection = None
        cursor = None
        transaction_id = f"txn_{int(time.time() * 1000)}"

        try:
            print(f"🔄 Iniciando transacción {transaction_id}...")

            connection = self.get_connection()
            if connection is None:
                raise Exception("No se pudo obtener conexión para transacción")

            cursor = connection.cursor(dictionary=True)
            connection.start_transaction()

            # Registrar transacción activa
            with self.transaction_lock:
                self.active_transactions[transaction_id] = {
                    'status': TransactionStatus.PENDING,
                    'start_time': datetime.now(),
                    'queries_count': len(queries)
                }

            total_affected_rows = 0
            results = []

            # Ejecutar cada consulta
            for i, (query, params) in enumerate(queries):
                print(f"📝 Ejecutando consulta {i + 1}/{len(queries)}...")

                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)

                total_affected_rows += cursor.rowcount

                # Obtener resultados si es SELECT
                if query.strip().upper().startswith('SELECT'):
                    results.extend(cursor.fetchall())

            # Confirmar transacción
            connection.commit()
            execution_time = time.time() - start_time

            # Actualizar estado de transacción
            with self.transaction_lock:
                self.active_transactions[transaction_id]['status'] = TransactionStatus.COMMITTED

            print(f"✅ Transacción {transaction_id} completada exitosamente")

            return QueryResult(
                success=True,
                data=results,
                affected_rows=total_affected_rows,
                execution_time=execution_time
            )

        except Error as e:
            if connection:
                connection.rollback()

            execution_time = time.time() - start_time
            error_msg = f"Error en transacción: {e}"

            # Actualizar estado de transacción
            with self.transaction_lock:
                if transaction_id in self.active_transactions:
                    self.active_transactions[transaction_id]['status'] = TransactionStatus.ROLLED_BACK

            self.logger.error(error_msg)
            print(f"❌ Transacción {transaction_id} falló: {error_msg}")

            return QueryResult(
                success=False,
                data=None,
                affected_rows=0,
                execution_time=execution_time,
                error_message=error_msg
            )

        finally:
            if cursor:
                cursor.close()
            if connection:
                self.release_connection(connection)

            # Limpiar transacción activa
            with self.transaction_lock:
                if transaction_id in self.active_transactions:
                    del self.active_transactions[transaction_id]

    # =============================================================================
    # OPERACIONES CRUD PARA USUARIOS
    # =============================================================================

    def create_user(self, email: str, password_hash: str, nombre: str,
                    apellido: str, fecha_nacimiento: str,
                    nivel_inicial: str = "principiante",
                    rol: str = "estudiante") -> QueryResult:
        """Crear nuevo usuario"""
        query = """
                INSERT INTO usuarios (email, password_hash, nombre, apellido, fecha_nacimiento,
                                      nivel_inicial, rol, activo, fecha_registro)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) \
                """

        params = (
            email, password_hash, nombre, apellido, fecha_nacimiento,
            nivel_inicial, rol, True, datetime.now()
        )

        return self.execute_query(query, params, fetch_results=False)

    def get_user_by_email(self, email: str) -> QueryResult:
        """Obtener usuario por email"""
        query = "SELECT * FROM usuarios WHERE email = %s AND activo = TRUE"
        return self.execute_query(query, (email,))

    def get_user_by_id(self, user_id: int) -> QueryResult:
        """Obtener usuario por ID"""
        query = "SELECT * FROM usuarios WHERE id = %s AND activo = TRUE"
        return self.execute_query(query, (user_id,))

    def update_user(self, user_id: int, updates: Dict[str, Any]) -> QueryResult:
        """Actualizar datos de usuario"""
        if not updates:
            return QueryResult(False, None, 0, 0.0, "No hay datos para actualizar")

        # Construir consulta dinámicamente
        set_clauses = []
        params = []

        for field, value in updates.items():
            set_clauses.append(f"{field} = %s")
            params.append(value)

        params.append(user_id)

        query = f"UPDATE usuarios SET {', '.join(set_clauses)} WHERE id = %s"
        return self.execute_query(query, tuple(params), fetch_results=False)

    def delete_user(self, user_id: int, soft_delete: bool = True) -> QueryResult:
        """Eliminar usuario (soft delete por defecto)"""
        if soft_delete:
            query = "UPDATE usuarios SET activo = FALSE WHERE id = %s"
        else:
            query = "DELETE FROM usuarios WHERE id = %s"

        return self.execute_query(query, (user_id,), fetch_results=False)

    # =============================================================================
    # OPERACIONES CRUD PARA PERFILES DE USUARIO
    # =============================================================================

    def create_user_profile(self, user_id: int, **profile_data) -> QueryResult:
        """Crear perfil de usuario"""
        default_profile = {
            'user_id': user_id,
            'nivel_lectura': 1,
            'nivel_gramatica': 1,
            'nivel_vocabulario': 1,
            'puntos_totales': 0,
            'experiencia_total': 0,
            'racha_dias_consecutivos': 0,
            'tiempo_total_minutos': 0,
            'ejercicios_completados': 0,
            'objetivo_diario_ejercicios': 5,
            'estilo_aprendizaje': 'mixto',
            'preferencias_json': '{}',
            'estadisticas_json': '{}'
        }

        # Actualizar con datos proporcionados
        default_profile.update(profile_data)

        fields = ', '.join(default_profile.keys())
        placeholders = ', '.join(['%s'] * len(default_profile))
        values = tuple(default_profile.values())

        query = f"INSERT INTO perfiles_usuario ({fields}) VALUES ({placeholders})"
        return self.execute_query(query, values, fetch_results=False)

    def get_user_profile(self, user_id: int) -> QueryResult:
        """Obtener perfil de usuario"""
        query = "SELECT * FROM perfiles_usuario WHERE user_id = %s"
        return self.execute_query(query, (user_id,))

    def update_user_profile(self, user_id: int, updates: Dict[str, Any]) -> QueryResult:
        """Actualizar perfil de usuario"""
        if not updates:
            return QueryResult(False, None, 0, 0.0, "No hay datos para actualizar")

        set_clauses = []
        params = []

        for field, value in updates.items():
            set_clauses.append(f"{field} = %s")
            params.append(value)

        params.append(user_id)

        query = f"UPDATE perfiles_usuario SET {', '.join(set_clauses)} WHERE user_id = %s"
        return self.execute_query(query, tuple(params), fetch_results=False)

    # =============================================================================
    # OPERACIONES DE EJERCICIOS Y RESULTADOS
    # =============================================================================

    def save_exercise_result(self, user_id: int, exercise_data: Dict[str, Any]) -> QueryResult:
        """Guardar resultado de ejercicio"""
        query = """
                INSERT INTO resultados_ejercicios
                (user_id, tipo_ejercicio, dificultad, puntuacion, tiempo_empleado,
                 respuestas_correctas, total_preguntas, fecha_completado, datos_json)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) \
                """

        params = (
            user_id,
            exercise_data.get('tipo_ejercicio', 'general'),
            exercise_data.get('dificultad', 'intermedio'),
            exercise_data.get('puntuacion', 0),
            exercise_data.get('tiempo_empleado', 0),
            exercise_data.get('respuestas_correctas', 0),
            exercise_data.get('total_preguntas', 0),
            datetime.now(),
            json.dumps(exercise_data, ensure_ascii=False)
        )

        return self.execute_query(query, params, fetch_results=False)

    def get_user_exercise_history(self, user_id: int, limit: int = 50) -> QueryResult:
        """Obtener historial de ejercicios del usuario"""
        query = """
                SELECT * \
                FROM resultados_ejercicios
                WHERE user_id = %s
                ORDER BY fecha_completado DESC
                LIMIT %s \
                """
        return self.execute_query(query, (user_id, limit))

    def get_user_statistics(self, user_id: int) -> QueryResult:
        """Obtener estadísticas del usuario"""
        query = """
                SELECT COUNT(*)                  as total_ejercicios, \
                       AVG(puntuacion)           as puntuacion_promedio, \
                       SUM(tiempo_empleado)      as tiempo_total, \
                       SUM(respuestas_correctas) as respuestas_correctas_total, \
                       SUM(total_preguntas)      as preguntas_total, \
                       MAX(fecha_completado)     as ultimo_ejercicio
                FROM resultados_ejercicios
                WHERE user_id = %s \
                """
        return self.execute_query(query, (user_id,))

    # =============================================================================
    # UTILIDADES Y MANTENIMIENTO
    # =============================================================================

    def get_database_stats(self) -> DatabaseStats:
        """Obtener estadísticas actuales de la base de datos"""
        self.stats.uptime = (datetime.now() - self.start_time).total_seconds()
        return self.stats

    def _update_average_query_time(self, execution_time: float):
        """Actualizar tiempo promedio de consultas"""
        if self.stats.successful_queries > 1:
            current_avg = self.stats.average_query_time
            new_avg = ((current_avg * (
                        self.stats.successful_queries - 1)) + execution_time) / self.stats.successful_queries
            self.stats.average_query_time = new_avg
        else:
            self.stats.average_query_time = execution_time

    def create_backup(self, backup_path: Optional[str] = None) -> BackupInfo:
        """Crear respaldo de la base de datos"""
        import subprocess
        import os

        try:
            timestamp = datetime.now()
            if backup_path is None:
                backup_filename = f"alfaia_backup_{timestamp.strftime('%Y%m%d_%H%M%S')}.sql"
                backup_path = f"./backups/{backup_filename}"
            else:
                backup_filename = os.path.basename(backup_path)

            # Crear directorio de respaldos si no existe
            os.makedirs(os.path.dirname(backup_path), exist_ok=True)

            # Ejecutar mysqldump
            cmd = [
                'mysqldump',
                f'--host={self.db_config["host"]}',
                f'--port={self.db_config["port"]}',
                f'--user={self.db_config["user"]}',
                f'--password={self.db_config["password"]}',
                '--routines',
                '--triggers',
                self.db_config['database']
            ]

            with open(backup_path, 'w') as backup_file:
                result = subprocess.run(cmd, stdout=backup_file, stderr=subprocess.PIPE, text=True)

            if result.returncode == 0:
                file_size = os.path.getsize(backup_path)
                self.stats.last_backup = timestamp

                return BackupInfo(
                    filename=backup_filename,
                    timestamp=timestamp,
                    size_bytes=file_size,
                    tables_included=self._get_table_names(),
                    success=True
                )
            else:
                return BackupInfo(
                    filename=backup_filename,
                    timestamp=timestamp,
                    size_bytes=0,
                    tables_included=[],
                    success=False,
                    error_message=result.stderr
                )

        except Exception as e:
            return BackupInfo(
                filename="",
                timestamp=timestamp,
                size_bytes=0,
                tables_included=[],
                success=False,
                error_message=str(e)
            )

    def _get_table_names(self) -> List[str]:
        """Obtener nombres de todas las tablas"""
        result = self.execute_query("SHOW TABLES")
        if result.success and result.data:
            return [list(row.values())[0] for row in result.data]
        return []

    def optimize_database(self) -> QueryResult:
        """Optimizar base de datos"""
        tables = self._get_table_names()
        if not tables:
            return QueryResult(False, None, 0, 0.0, "No se pudieron obtener las tablas")

        optimize_queries = [(f"OPTIMIZE TABLE {table}", None) for table in tables]
        return self.execute_transaction(optimize_queries)

    def close_all_connections(self):
        """Cerrar todas las conexiones"""
        try:
            if self.connection_pool:
                # Cerrar el pool de conexiones
                self.connection_pool = None

            self.status = ConnectionStatus.DISCONNECTED
            print("🔒 Todas las conexiones cerradas")

        except Exception as e:
            self.logger.error(f"Error cerrando conexiones: {e}")


# =============================================================================
# FUNCIONES DE UTILIDAD
# =============================================================================

def get_database_manager() -> DatabaseManager:
    """Obtener instancia única del gestor de base de datos"""
    return DatabaseManager()


def quick_query(query: str, params: Optional[Tuple] = None) -> Dict[str, Any]:
    """
    Ejecutar consulta rápida

    Args:
        query: Consulta SQL
        params: Parámetros opcionales

    Returns:
        Dict con resultado simplificado
    """
    db_manager = get_database_manager()
    result = db_manager.execute_query(query, params)

    return {
        'success': result.success,
        'data': result.data,
        'affected_rows': result.affected_rows,
        'execution_time': result.execution_time,
        'error': result.error_message
    }


def check_database_health() -> Dict[str, Any]:
    """
    Verificar salud de la base de datos

    Returns:
        Dict con estado de la base de datos
    """
    db_manager = get_database_manager()

    # Probar conexión
    connection_ok = db_manager.test_connection()

    # Obtener estadísticas
    stats = db_manager.get_database_stats()

    return {
        'connection_status': connection_ok,
        'total_queries': stats.total_queries,
        'success_rate': (stats.successful_queries / max(stats.total_queries, 1)) * 100,
        'average_query_time': stats.average_query_time,
        'uptime_seconds': stats.uptime,
        'active_connections': stats.active_connections
    }


# =============================================================================
# CÓDIGO DE PRUEBA
# =============================================================================

if __name__ == "__main__":
    print("🧪 Probando gestor de base de datos...")

    # Crear gestor
    db_manager = DatabaseManager()

    print("\n🔍 PRUEBAS DE CONEXIÓN:")
    print("=" * 50)

    # Probar conexión
    connection_test = db_manager.test_connection()
    print(f"Conexión: {'✅ Exitosa' if connection_test else '❌ Falló'}")

    if connection_test:
        # Prueba de consulta simple
        print(f"\n📝 PRUEBA DE CONSULTA SIMPLE:")
        result = db_manager.execute_query("SELECT NOW() as current_time")

        if result.success:
            print(f"✅ Consulta exitosa")
            print(f"⏱️ Tiempo: {result.execution_time:.3f}s")
            print(f"📊 Datos: {result.data}")
        else:
            print(f"❌ Error: {result.error_message}")

        # Prueba de estadísticas
        print(f"\n📊 ESTADÍSTICAS DE BASE DE DATOS:")
        stats = db_manager.get_database_stats()
        print(f"Total consultas: {stats.total_queries}")
        print(f"Consultas exitosas: {stats.successful_queries}")
        print(f"Consultas fallidas: {stats.failed_queries}")
        print(f"Tiempo promedio: {stats.average_query_time:.3f}s")
        print(f"Uptime: {stats.uptime:.1f}s")
        print(f"Conexiones activas: {stats.active_connections}")

        # Prueba de función de utilidad
        print(f"\n⚡ PRUEBA DE CONSULTA RÁPIDA:")
        quick_result = quick_query("SELECT DATABASE() as db_name")
        print(f"Resultado rápido: {quick_result}")

        # Prueba de salud de BD
        print(f"\n🏥 ESTADO DE SALUD DE LA BASE DE DATOS:")
        health = check_database_health()
        print(f"Estado de conexión: {'✅ OK' if health['connection_status'] else '❌ Error'}")
        print(f"Tasa de éxito: {health['success_rate']:.1f}%")
        print(f"Tiempo promedio de consulta: {health['average_query_time']:.3f}s")
        print(f"Uptime: {health['uptime_seconds']:.1f}s")

    else:
        print("❌ No se puede conectar a la base de datos")
        print("💡 Verifica la configuración en config/settings.py")
        print("💡 Asegúrate de que MySQL esté ejecutándose")
        print("💡 Verifica que la base de datos 'alfaia_db' exista")

    print(f"\n✅ Pruebas del gestor de base de datos completadas!")

    # Limpiar recursos
    db_manager.close_all_connections()
    print("🧹 Recursos liberados")
# =============================================================================
# AlfaIA/core/database/models.py - Modelos Completos y Funcionales
# =============================================================================

import json
import hashlib
from datetime import datetime, date
from typing import Optional, Dict, Any, List
from enum import Enum


class NivelUsuario(Enum):
    """Niveles de usuario disponibles"""
    PRINCIPIANTE = "Principiante"
    INTERMEDIO = "Intermedio"
    AVANZADO = "Avanzado"


class RolUsuario(Enum):
    """Roles de usuario en el sistema"""
    ESTUDIANTE = "Estudiante"
    TUTOR = "Tutor"
    ADMINISTRADOR = "Administrador"


class EstiloAprendizaje(Enum):
    """Estilos de aprendizaje"""
    VISUAL = "Visual"
    AUDITIVO = "Auditivo"
    KINESTESICO = "Kinestésico"
    MIXTO = "Mixto"


class Usuario:
    """Modelo de Usuario"""

    def __init__(self, id: int = None, email: str = None, password_hash: str = None,
                 nombre: str = None, apellido: str = None, fecha_nacimiento: date = None,
                 nivel_inicial: NivelUsuario = NivelUsuario.PRINCIPIANTE,
                 rol: RolUsuario = RolUsuario.ESTUDIANTE, activo: bool = True,
                 fecha_registro: datetime = None, configuracion_json: Dict = None):
        self.id = id
        self.email = email
        self.password_hash = password_hash
        self.nombre = nombre
        self.apellido = apellido
        self.fecha_nacimiento = fecha_nacimiento
        self.nivel_inicial = nivel_inicial
        self.rol = rol
        self.activo = activo
        self.fecha_registro = fecha_registro or datetime.now()
        self.configuracion_json = configuracion_json or {}

    @staticmethod
    def hash_password(password: str) -> str:
        """Crear hash de contraseña usando SHA-256 (simplificado)"""
        return hashlib.sha256(password.encode('utf-8')).hexdigest()

    def verify_password(self, password: str) -> bool:
        """Verificar contraseña contra el hash"""
        if not self.password_hash:
            return False
        return self.password_hash == Usuario.hash_password(password)

    def save(self) -> bool:
        """Guardar usuario en la base de datos"""
        try:
            from core.database.connection import DatabaseManager
            db_manager = DatabaseManager()

            if self.id is None:
                # Insertar nuevo usuario
                query = """
                        INSERT INTO usuarios (email, password_hash, nombre, apellido, fecha_nacimiento,
                                              nivel_inicial, rol, activo, configuracion_json)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) \
                        """
                params = (
                    self.email, self.password_hash, self.nombre, self.apellido,
                    self.fecha_nacimiento, self.nivel_inicial.value, self.rol.value,
                    self.activo, json.dumps(self.configuracion_json)
                )

                connection = db_manager.get_connection()
                if connection:
                    cursor = connection.cursor()
                    cursor.execute(query, params)
                    self.id = cursor.lastrowid
                    connection.commit()
                    cursor.close()
                    connection.close()
                    return True
            else:
                # Actualizar usuario existente
                query = """
                        UPDATE usuarios \
                        SET email=%s, \
                            password_hash=%s, \
                            nombre=%s, \
                            apellido=%s, \
                            fecha_nacimiento=%s, \
                            nivel_inicial=%s, \
                            rol=%s, \
                            activo=%s, \
                            configuracion_json=%s
                        WHERE id = %s \
                        """
                params = (
                    self.email, self.password_hash, self.nombre, self.apellido,
                    self.fecha_nacimiento, self.nivel_inicial.value, self.rol.value,
                    self.activo, json.dumps(self.configuracion_json), self.id
                )
                return db_manager.execute_non_query(query, params)

        except Exception as e:
            print(f"Error guardando usuario: {e}")
            return False
        return False

    @classmethod
    def find_by_email(cls, email: str) -> Optional['Usuario']:
        """Buscar usuario por email"""
        try:
            from core.database.connection import DatabaseManager
            db_manager = DatabaseManager()
            query = "SELECT * FROM usuarios WHERE email = %s AND activo = TRUE"
            results = db_manager.execute_query(query, (email,))

            if results and len(results) > 0:
                row = results[0]
                return cls._from_row(row)
            return None

        except Exception as e:
            print(f"Error buscando usuario por email: {e}")
            return None

    @classmethod
    def find_by_id(cls, user_id: int) -> Optional['Usuario']:
        """Buscar usuario por ID"""
        try:
            from core.database.connection import DatabaseManager
            db_manager = DatabaseManager()
            query = "SELECT * FROM usuarios WHERE id = %s"
            results = db_manager.execute_query(query, (user_id,))

            if results and len(results) > 0:
                row = results[0]
                return cls._from_row(row)
            return None

        except Exception as e:
            print(f"Error buscando usuario por ID: {e}")
            return None

    @classmethod
    def _from_row(cls, row: tuple) -> 'Usuario':
        """Crear instancia de Usuario desde fila de BD"""
        try:
            configuracion = json.loads(row[10]) if row[10] else {}
        except (json.JSONDecodeError, TypeError):
            configuracion = {}

        return cls(
            id=row[0],
            email=row[1],
            password_hash=row[2],
            nombre=row[3],
            apellido=row[4],
            fecha_nacimiento=row[5],
            nivel_inicial=NivelUsuario(row[6]),
            rol=RolUsuario(row[7]),
            activo=row[8],
            fecha_registro=row[9],
            configuracion_json=configuracion
        )


class PerfilUsuario:
    """Modelo de Perfil de Usuario"""

    def __init__(self, id: int = None, user_id: int = None, nivel_lectura: int = 1,
                 nivel_gramatica: int = 1, nivel_vocabulario: int = 1, puntos_totales: int = 0,
                 experiencia_total: int = 0, racha_dias_consecutivos: int = 0,
                 tiempo_total_minutos: int = 0, ejercicios_completados: int = 0,
                 objetivo_diario_ejercicios: int = 5,
                 estilo_aprendizaje: EstiloAprendizaje = EstiloAprendizaje.MIXTO,
                 preferencias_json: Dict = None, estadisticas_json: Dict = None):
        self.id = id
        self.user_id = user_id
        self.nivel_lectura = nivel_lectura
        self.nivel_gramatica = nivel_gramatica
        self.nivel_vocabulario = nivel_vocabulario
        self.puntos_totales = puntos_totales
        self.experiencia_total = experiencia_total
        self.racha_dias_consecutivos = racha_dias_consecutivos
        self.tiempo_total_minutos = tiempo_total_minutos
        self.ejercicios_completados = ejercicios_completados
        self.objetivo_diario_ejercicios = objetivo_diario_ejercicios
        self.estilo_aprendizaje = estilo_aprendizaje
        self.preferencias_json = preferencias_json or {}
        self.estadisticas_json = estadisticas_json or {}

    def save(self) -> bool:
        """Guardar perfil en la base de datos"""
        try:
            from core.database.connection import DatabaseManager
            db_manager = DatabaseManager()

            if self.id is None:
                # Insertar nuevo perfil
                query = """
                        INSERT INTO perfiles_usuario (user_id, nivel_lectura, nivel_gramatica, nivel_vocabulario,
                                                      puntos_totales, experiencia_total, racha_dias_consecutivos,
                                                      tiempo_total_minutos, ejercicios_completados, \
                                                      objetivo_diario_ejercicios,
                                                      estilo_aprendizaje, preferencias_json, estadisticas_json)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) \
                        """
                params = (
                    self.user_id, self.nivel_lectura, self.nivel_gramatica, self.nivel_vocabulario,
                    self.puntos_totales, self.experiencia_total, self.racha_dias_consecutivos,
                    self.tiempo_total_minutos, self.ejercicios_completados, self.objetivo_diario_ejercicios,
                    self.estilo_aprendizaje.value, json.dumps(self.preferencias_json),
                    json.dumps(self.estadisticas_json)
                )

                connection = db_manager.get_connection()
                if connection:
                    cursor = connection.cursor()
                    cursor.execute(query, params)
                    self.id = cursor.lastrowid
                    connection.commit()
                    cursor.close()
                    connection.close()
                    return True
            else:
                # Actualizar perfil existente
                query = """
                        UPDATE perfiles_usuario \
                        SET nivel_lectura=%s, \
                            nivel_gramatica=%s, \
                            nivel_vocabulario=%s, \
                            puntos_totales=%s, \
                            experiencia_total=%s, \
                            racha_dias_consecutivos=%s, \
                            tiempo_total_minutos=%s, \
                            ejercicios_completados=%s, \
                            objetivo_diario_ejercicios=%s, \
                            estilo_aprendizaje=%s, \
                            preferencias_json=%s, \
                            estadisticas_json=%s
                        WHERE id = %s \
                        """
                params = (
                    self.nivel_lectura, self.nivel_gramatica, self.nivel_vocabulario,
                    self.puntos_totales, self.experiencia_total, self.racha_dias_consecutivos,
                    self.tiempo_total_minutos, self.ejercicios_completados, self.objetivo_diario_ejercicios,
                    self.estilo_aprendizaje.value, json.dumps(self.preferencias_json),
                    json.dumps(self.estadisticas_json), self.id
                )
                return db_manager.execute_non_query(query, params)

        except Exception as e:
            print(f"Error guardando perfil: {e}")
            return False
        return False

    @classmethod
    def find_by_user_id(cls, user_id: int) -> Optional['PerfilUsuario']:
        """Buscar perfil por ID de usuario"""
        try:
            from core.database.connection import DatabaseManager
            db_manager = DatabaseManager()
            query = "SELECT * FROM perfiles_usuario WHERE user_id = %s"
            results = db_manager.execute_query(query, (user_id,))

            if results and len(results) > 0:
                row = results[0]
                return cls._from_row(row)
            return None

        except Exception as e:
            print(f"Error buscando perfil por user_id: {e}")
            return None

    @classmethod
    def _from_row(cls, row: tuple) -> 'PerfilUsuario':
        """Crear instancia de PerfilUsuario desde fila de BD"""
        try:
            preferencias = json.loads(row[11]) if row[11] else {}
            estadisticas = json.loads(row[12]) if row[12] else {}
        except (json.JSONDecodeError, TypeError):
            preferencias = {}
            estadisticas = {}

        return cls(
            id=row[0],
            user_id=row[1],
            nivel_lectura=row[2],
            nivel_gramatica=row[3],
            nivel_vocabulario=row[4],
            puntos_totales=row[5],
            experiencia_total=row[6],
            racha_dias_consecutivos=row[7],
            tiempo_total_minutos=row[8],
            ejercicios_completados=row[9],
            objetivo_diario_ejercicios=row[10],
            estilo_aprendizaje=EstiloAprendizaje.MIXTO,  # Simplificado por ahora
            preferencias_json=preferencias,
            estadisticas_json=estadisticas
        )


if __name__ == "__main__":
    print("🧪 Probando modelos de AlfaIA...")

    # Crear usuario de prueba
    try:
        user = Usuario(
            email="test@alfaia.com",
            password_hash=Usuario.hash_password("test123"),
            nombre="Usuario",
            apellido="Prueba",
            fecha_nacimiento=date(1990, 1, 1),
            nivel_inicial=NivelUsuario.PRINCIPIANTE,
            rol=RolUsuario.ESTUDIANTE
        )

        if user.save():
            print(f"✅ Usuario creado: {user.email} (ID: {user.id})")

            # Crear perfil asociado
            perfil = PerfilUsuario(
                user_id=user.id,
                preferencias_json={
                    "tema": "light",
                    "notificaciones": True,
                    "sonidos": True
                }
            )
            if perfil.save():
                print("✅ Perfil creado exitosamente")
        else:
            print("❌ Error creando usuario de prueba")
    except Exception as e:
        print(f"❌ Error en pruebas: {e}")

    print("🏁 Pruebas de modelos completadas")
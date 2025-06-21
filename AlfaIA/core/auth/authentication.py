# =============================================================================
# AlfaIA/core/auth/authentication.py - Sistema de Autenticación
# =============================================================================

import re
from datetime import datetime, timedelta
from typing import Optional, Tuple
import secrets
import sys
from pathlib import Path

# Agregar path para imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from core.database.models import Usuario, PerfilUsuario, NivelUsuario, RolUsuario


class AuthenticationError(Exception):
    """Excepción personalizada para errores de autenticación"""
    pass


class ValidationError(Exception):
    """Excepción personalizada para errores de validación"""
    pass


class AuthenticationManager:
    """Gestor de autenticación y sesiones de usuario"""

    def __init__(self):
        self.current_user: Optional[Usuario] = None
        self.session_token: Optional[str] = None
        self.session_expires: Optional[datetime] = None

    def register_user(self, email: str, password: str, nombre: str, apellido: str,
                      fecha_nacimiento: str = None, nivel_inicial: str = "Principiante") -> Tuple[bool, str]:
        """
        Registrar nuevo usuario en el sistema

        Args:
            email: Correo electrónico del usuario
            password: Contraseña en texto plano
            nombre: Nombre del usuario
            apellido: Apellido del usuario
            fecha_nacimiento: Fecha de nacimiento (YYYY-MM-DD)
            nivel_inicial: Nivel inicial del usuario

        Returns:
            Tuple[bool, str]: (éxito, mensaje)
        """
        try:
            # Validar datos de entrada
            self._validate_registration_data(email, password, nombre, apellido)

            # Verificar que el email no esté registrado
            existing_user = Usuario.find_by_email(email)
            if existing_user:
                return False, "El correo electrónico ya está registrado"

            # Crear nuevo usuario
            user = Usuario(
                email=email.lower().strip(),
                password_hash=Usuario.hash_password(password),
                nombre=nombre.strip(),
                apellido=apellido.strip(),
                nivel_inicial=NivelUsuario(nivel_inicial),
                rol=RolUsuario.ESTUDIANTE,
                activo=True
            )

            # Procesar fecha de nacimiento si se proporciona
            if fecha_nacimiento:
                try:
                    from datetime import datetime
                    user.fecha_nacimiento = datetime.strptime(fecha_nacimiento, "%Y-%m-%d").date()
                except ValueError:
                    return False, "Formato de fecha inválido. Use YYYY-MM-DD"

            # Guardar usuario
            if not user.save():
                return False, "Error al guardar el usuario en la base de datos"

            # Crear perfil de usuario por defecto
            perfil = PerfilUsuario(
                user_id=user.id,
                nivel_lectura=1,
                nivel_gramatica=1,
                nivel_vocabulario=1,
                objetivo_diario_ejercicios=5,
                preferencias_json={
                    "tema": "light",
                    "notificaciones": True,
                    "sonidos": True
                },
                estadisticas_json={}
            )

            if not perfil.save():
                return False, "Error al crear el perfil de usuario"

            return True, "Usuario registrado exitosamente"

        except ValidationError as e:
            return False, str(e)
        except Exception as e:
            return False, f"Error inesperado: {str(e)}"

    def login(self, email: str, password: str) -> Tuple[bool, str]:
        """
        Iniciar sesión de usuario

        Args:
            email: Correo electrónico
            password: Contraseña

        Returns:
            Tuple[bool, str]: (éxito, mensaje)
        """
        try:
            # Validar entrada básica
            if not email or not password:
                return False, "Email y contraseña son requeridos"

            # Buscar usuario por email
            user = Usuario.find_by_email(email.lower().strip())
            if not user:
                return False, "Credenciales inválidas"

            # Verificar que el usuario esté activo
            if not user.activo:
                return False, "Cuenta desactivada. Contacte al administrador"

            # Verificar contraseña
            if not user.verify_password(password):
                return False, "Credenciales inválidas"

            # Crear sesión
            self._create_session(user)

            return True, "Inicio de sesión exitoso"

        except Exception as e:
            return False, f"Error en el inicio de sesión: {str(e)}"

    def logout(self) -> bool:
        """
        Cerrar sesión actual

        Returns:
            bool: Éxito del logout
        """
        try:
            self.current_user = None
            self.session_token = None
            self.session_expires = None
            return True
        except Exception:
            return False

    def is_logged_in(self) -> bool:
        """
        Verificar si hay una sesión activa válida

        Returns:
            bool: True si hay sesión activa
        """
        if not self.current_user or not self.session_expires:
            return False

        # Verificar que la sesión no haya expirado
        return datetime.now() < self.session_expires

    def get_current_user(self) -> Optional[Usuario]:
        """
        Obtener usuario actual autenticado

        Returns:
            Usuario actual o None si no hay sesión
        """
        if self.is_logged_in():
            return self.current_user
        return None

    def get_user_profile(self) -> Optional[PerfilUsuario]:
        """
        Obtener perfil del usuario actual

        Returns:
            PerfilUsuario o None si no hay sesión
        """
        if not self.is_logged_in():
            return None

        return PerfilUsuario.find_by_user_id(self.current_user.id)

    def change_password(self, current_password: str, new_password: str) -> Tuple[bool, str]:
        """
        Cambiar contraseña del usuario actual

        Args:
            current_password: Contraseña actual
            new_password: Nueva contraseña

        Returns:
            Tuple[bool, str]: (éxito, mensaje)
        """
        try:
            if not self.is_logged_in():
                return False, "No hay sesión activa"

            # Verificar contraseña actual
            if not self.current_user.verify_password(current_password):
                return False, "Contraseña actual incorrecta"

            # Validar nueva contraseña
            if not self._validate_password(new_password):
                return False, "La nueva contraseña no cumple con los requisitos de seguridad"

            # Actualizar contraseña
            self.current_user.password_hash = Usuario.hash_password(new_password)
            if self.current_user.save():
                return True, "Contraseña actualizada exitosamente"
            else:
                return False, "Error al actualizar la contraseña"

        except Exception as e:
            return False, f"Error al cambiar contraseña: {str(e)}"

    def update_user_profile(self, **kwargs) -> Tuple[bool, str]:
        """
        Actualizar perfil del usuario actual

        Args:
            **kwargs: Campos a actualizar

        Returns:
            Tuple[bool, str]: (éxito, mensaje)
        """
        try:
            if not self.is_logged_in():
                return False, "No hay sesión activa"

            # Obtener perfil actual
            perfil = self.get_user_profile()
            if not perfil:
                return False, "No se encontró el perfil de usuario"

            # Actualizar campos permitidos
            allowed_fields = [
                'objetivo_diario_ejercicios', 'estilo_aprendizaje',
                'preferencias_json', 'nivel_lectura', 'nivel_gramatica', 'nivel_vocabulario'
            ]

            updated = False
            for field, value in kwargs.items():
                if field in allowed_fields and hasattr(perfil, field):
                    setattr(perfil, field, value)
                    updated = True

            if updated and perfil.save():
                return True, "Perfil actualizado exitosamente"
            else:
                return False, "No se realizaron cambios o error al guardar"

        except Exception as e:
            return False, f"Error al actualizar perfil: {str(e)}"

    def _create_session(self, user: Usuario) -> None:
        """
        Crear sesión para el usuario

        Args:
            user: Usuario para crear sesión
        """
        self.current_user = user
        self.session_token = secrets.token_urlsafe(32)
        # Sesión válida por 8 horas
        self.session_expires = datetime.now() + timedelta(hours=8)

    def _validate_registration_data(self, email: str, password: str,
                                    nombre: str, apellido: str) -> None:
        """
        Validar datos de registro

        Args:
            email: Email a validar
            password: Contraseña a validar
            nombre: Nombre a validar
            apellido: Apellido a validar

        Raises:
            ValidationError: Si algún dato es inválido
        """
        # Validar email
        if not self._validate_email(email):
            raise ValidationError("Formato de email inválido")

        # Validar contraseña
        if not self._validate_password(password):
            raise ValidationError(
                "La contraseña debe tener al menos 8 caracteres, "
                "incluir mayúsculas, minúsculas y números"
            )

        # Validar nombre y apellido
        if not nombre or len(nombre.strip()) < 2:
            raise ValidationError("El nombre debe tener al menos 2 caracteres")

        if not apellido or len(apellido.strip()) < 2:
            raise ValidationError("El apellido debe tener al menos 2 caracteres")

        # Validar caracteres especiales en nombre y apellido
        if not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$", nombre.strip()):
            raise ValidationError("El nombre contiene caracteres inválidos")

        if not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$", apellido.strip()):
            raise ValidationError("El apellido contiene caracteres inválidos")

    def _validate_email(self, email: str) -> bool:
        """
        Validar formato de email

        Args:
            email: Email a validar

        Returns:
            bool: True si el email es válido
        """
        if not email:
            return False

        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}
        return re.match(pattern, email.strip()) is not None

    def _validate_password(self, password: str) -> bool:
        """
        Validar fortaleza de contraseña

        Args:
            password: Contraseña a validar

        Returns:
            bool: True si la contraseña es válida
        """
        if not password or len(password) < 8:
            return False

        # Verificar que tenga al menos una mayúscula, una minúscula y un número
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)

        return has_upper and has_lower and has_digit

    def extend_session(self) -> bool:
        """
        Extender sesión actual por 8 horas más

        Returns:
            bool: True si se extendió la sesión
        """
        if self.is_logged_in():
            self.session_expires = datetime.now() + timedelta(hours=8)
            return True
        return False

    def get_session_info(self) -> dict:
        """
        Obtener información de la sesión actual

        Returns:
            dict: Información de la sesión
        """
        if not self.is_logged_in():
            return {"logged_in": False}

        time_remaining = self.session_expires - datetime.now()

        return {
            "logged_in": True,
            "user_id": self.current_user.id,
            "user_name": f"{self.current_user.nombre} {self.current_user.apellido}",
            "user_email": self.current_user.email,
            "user_role": self.current_user.rol.value,
            "session_expires": self.session_expires.isoformat(),
            "time_remaining_minutes": int(time_remaining.total_seconds() / 60)
        }


# =============================================================================
# CLASE SINGLETON PARA GESTIÓN GLOBAL
# =============================================================================

class AuthManager:
    """Gestor singleton de autenticación global"""

    _instance = None
    _auth_manager = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AuthManager, cls).__new__(cls)
            cls._auth_manager = AuthenticationManager()
        return cls._instance

    def __getattr__(self, name):
        """Delegar atributos al AuthenticationManager"""
        return getattr(self._auth_manager, name)


# Instancia global del gestor de autenticación
auth_manager = AuthManager()


# =============================================================================
# FUNCIONES DE UTILIDAD
# =============================================================================

def require_login(func):
    """
    Decorador para funciones que requieren autenticación

    Args:
        func: Función a decorar

    Returns:
        Función decorada
    """

    def wrapper(*args, **kwargs):
        if not auth_manager.is_logged_in():
            raise AuthenticationError("Se requiere autenticación")
        return func(*args, **kwargs)

    return wrapper


def get_current_user() -> Optional[Usuario]:
    """
    Función de conveniencia para obtener usuario actual

    Returns:
        Usuario actual o None
    """
    return auth_manager.get_current_user()


def get_user_profile() -> Optional[PerfilUsuario]:
    """
    Función de conveniencia para obtener perfil de usuario actual

    Returns:
        PerfilUsuario actual o None
    """
    return auth_manager.get_user_profile()


# =============================================================================
# CÓDIGO DE PRUEBA
# =============================================================================

if __name__ == "__main__":
    # Ejemplo de uso del sistema de autenticación
    auth = AuthenticationManager()

    # Registro de usuario de prueba
    success, message = auth.register_user(
        email="test@example.com",
        password="TestPassword123",
        nombre="Usuario",
        apellido="Prueba",
        fecha_nacimiento="1990-01-01"
    )
    print(f"Registro: {success} - {message}")

    # Inicio de sesión
    success, message = auth.login("test@example.com", "TestPassword123")
    print(f"Login: {success} - {message}")

    # Información de sesión
    if auth.is_logged_in():
        session_info = auth.get_session_info()
        print(f"Sesión activa: {session_info}")

        # Obtener perfil
        profile = auth.get_user_profile()
        if profile:
            print(f"Perfil: Nivel lectura {profile.nivel_lectura}")

    # Cerrar sesión
    auth.logout()
    print(f"Sesión cerrada. ¿Activa?: {auth.is_logged_in()}")
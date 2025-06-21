# =============================================================================
# AlfaIA/core/auth/authentication.py - Sistema de Autenticación Simplificado
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


class ValidationError(Exception):
    """Excepción personalizada para errores de validación"""
    pass


class AuthenticationManager:
    """Gestor de autenticación simplificado"""

    def __init__(self):
        self.current_user: Optional[Usuario] = None
        self.session_token: Optional[str] = None
        self.session_expires: Optional[datetime] = None

    def register_user(self, email: str, password: str, nombre: str, apellido: str,
                      fecha_nacimiento: str = None, nivel_inicial: str = "Principiante") -> Tuple[bool, str]:
        """Registrar nuevo usuario"""
        try:
            # Validaciones básicas
            if not email or not password or not nombre or not apellido:
                return False, "Todos los campos son requeridos"

            if len(password) < 8:
                return False, "La contraseña debe tener al menos 8 caracteres"

            if not self._validate_email(email):
                return False, "Formato de email inválido"

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
                    pass  # Ignorar si el formato es inválido

            # Guardar usuario
            if not user.save():
                return False, "Error al guardar el usuario"

            # Crear perfil por defecto
            perfil = PerfilUsuario(
                user_id=user.id,
                preferencias_json={
                    "tema": "light",
                    "notificaciones": True,
                    "sonidos": True
                }
            )
            perfil.save()

            return True, "Usuario registrado exitosamente"

        except Exception as e:
            return False, f"Error inesperado: {str(e)}"

    def login(self, email: str, password: str) -> Tuple[bool, str]:
        """Iniciar sesión"""
        try:
            if not email or not password:
                return False, "Email y contraseña son requeridos"

            # Buscar usuario
            user = Usuario.find_by_email(email.lower().strip())
            if not user:
                return False, "Credenciales inválidas"

            if not user.activo:
                return False, "Cuenta desactivada"

            # Verificar contraseña
            if not user.verify_password(password):
                return False, "Credenciales inválidas"

            # Crear sesión
            self.current_user = user
            self.session_token = secrets.token_urlsafe(32)
            self.session_expires = datetime.now() + timedelta(hours=8)

            return True, "Inicio de sesión exitoso"

        except Exception as e:
            return False, f"Error en el inicio de sesión: {str(e)}"

    def logout(self) -> bool:
        """Cerrar sesión"""
        self.current_user = None
        self.session_token = None
        self.session_expires = None
        return True

    def is_logged_in(self) -> bool:
        """Verificar si hay sesión activa"""
        if not self.current_user or not self.session_expires:
            return False
        return datetime.now() < self.session_expires

    def get_current_user(self) -> Optional[Usuario]:
        """Obtener usuario actual"""
        if self.is_logged_in():
            return self.current_user
        return None

    def get_user_profile(self) -> Optional[PerfilUsuario]:
        """Obtener perfil del usuario actual"""
        if not self.is_logged_in():
            return None
        return PerfilUsuario.find_by_user_id(self.current_user.id)

    def _validate_email(self, email: str) -> bool:
        """Validar formato de email"""
        if not email:
            return False
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email.strip()) is not None

    def get_session_info(self) -> dict:
        """Obtener información de la sesión"""
        if not self.is_logged_in():
            return {"logged_in": False}

        return {
            "logged_in": True,
            "user_id": self.current_user.id,
            "user_name": f"{self.current_user.nombre} {self.current_user.apellido}",
            "user_email": self.current_user.email,
            "user_role": self.current_user.rol.value
        }


# Instancia global
auth_manager = AuthenticationManager()

if __name__ == "__main__":
    # Prueba del sistema de autenticación
    auth = AuthenticationManager()

    # Registrar usuario de prueba
    success, message = auth.register_user(
        email="demo@alfaia.com",
        password="Demo123456",
        nombre="Demo",
        apellido="User"
    )
    print(f"Registro: {success} - {message}")

    # Hacer login
    success, message = auth.login("demo@alfaia.com", "Demo123456")
    print(f"Login: {success} - {message}")

    if auth.is_logged_in():
        print(f"Usuario logueado: {auth.get_current_user().nombre}")

    auth.logout()
    print(f"Sesión cerrada: {not auth.is_logged_in()}")
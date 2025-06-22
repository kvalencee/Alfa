# =============================================================================
# AlfaIA/core/auth/authentication.py - Authentication Manager SIN DEADLOCK
# =============================================================================

import re
from datetime import datetime, timedelta
from typing import Optional, Tuple
import secrets
import sys
from pathlib import Path
import threading

# Agregar path para imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from core.database.models import Usuario, PerfilUsuario, NivelUsuario, RolUsuario


class ValidationError(Exception):
    """Excepción personalizada para errores de validación"""
    pass


class AuthenticationManager:
    """Gestor de autenticación con Singleton REAL y sin deadlock"""

    _instance = None
    _lock = threading.RLock()  # Recursive lock para evitar deadlock
    _initialized = False

    def __new__(cls):
        """Implementación de Singleton thread-safe"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(AuthenticationManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """Inicializar solo una vez"""
        if not self.__class__._initialized:
            with self._lock:
                if not self.__class__._initialized:
                    self.current_user: Optional[Usuario] = None
                    self.session_token: Optional[str] = None
                    self.session_expires: Optional[datetime] = None
                    self.is_authenticated: bool = False
                    self.__class__._initialized = True
                    print("🔐 AuthenticationManager inicializado (Singleton)")

    def register_user(self, email: str, password: str, nombre: str, apellido: str,
                      fecha_nacimiento: str = None, nivel_inicial: str = "Principiante") -> Tuple[bool, str]:
        """Registrar nuevo usuario"""
        with self._lock:
            try:
                print(f"📝 Intentando registrar usuario: {email}")

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

                print(f"✅ Usuario registrado exitosamente: {email}")
                return True, "Usuario registrado exitosamente"

            except Exception as e:
                print(f"❌ Error en registro: {e}")
                return False, f"Error inesperado: {str(e)}"

    def login(self, email: str, password: str) -> Tuple[bool, str]:
        """Iniciar sesión - THREAD SAFE"""
        with self._lock:
            try:
                print(f"🔑 [THREAD-SAFE] Intentando login para: {email}")

                if not email or not password:
                    return False, "Email y contraseña son requeridos"

                # Buscar usuario
                user = Usuario.find_by_email(email.lower().strip())
                if not user:
                    print(f"❌ Usuario no encontrado: {email}")
                    return False, "Credenciales inválidas"

                if not user.activo:
                    print(f"❌ Cuenta desactivada: {email}")
                    return False, "Cuenta desactivada"

                # Verificar contraseña
                if not user.verify_password(password):
                    print(f"❌ Contraseña incorrecta para: {email}")
                    return False, "Credenciales inválidas"

                # CREAR SESIÓN DE FORMA ATÓMICA
                self.current_user = user
                self.session_token = secrets.token_urlsafe(32)
                self.session_expires = datetime.now() + timedelta(hours=8)
                self.is_authenticated = True

                print(f"✅ [THREAD-SAFE] Login exitoso para: {user.email}")
                print(f"👤 Usuario actual establecido: {user.nombre} {user.apellido} (ID: {user.id})")
                print(f"🔗 Token de sesión creado: {self.session_token[:10]}...")
                print(f"⏰ Sesión expira: {self.session_expires}")
                print(f"🔒 Estado autenticado: {self.is_authenticated}")

                return True, "Inicio de sesión exitoso"

            except Exception as e:
                print(f"❌ Error en login: {e}")
                import traceback
                traceback.print_exc()
                return False, f"Error en el inicio de sesión: {str(e)}"

    def logout(self) -> bool:
        """Cerrar sesión - THREAD SAFE"""
        with self._lock:
            try:
                print(
                    f"🚪 Cerrando sesión para: {self.current_user.email if self.current_user else 'usuario desconocido'}")

                self.current_user = None
                self.session_token = None
                self.session_expires = None
                self.is_authenticated = False

                print("✅ Sesión cerrada exitosamente")
                return True
            except Exception as e:
                print(f"❌ Error cerrando sesión: {e}")
                return False

    def is_logged_in(self) -> bool:
        """Verificar si hay sesión activa - SIN LOCK PARA EVITAR DEADLOCK"""
        try:
            if not self.is_authenticated:
                return False

            if not self.current_user or not self.session_expires:
                return False

            is_valid = datetime.now() < self.session_expires

            if not is_valid:
                print("⏰ Sesión expirada, limpiando...")
                # No usar self.logout() aquí para evitar deadlock
                self.current_user = None
                self.session_token = None
                self.session_expires = None
                self.is_authenticated = False

            return is_valid
        except Exception as e:
            print(f"❌ Error verificando sesión: {e}")
            return False

    def get_current_user(self) -> Optional[Usuario]:
        """Obtener usuario actual - SIN LOCK PARA EVITAR DEADLOCK"""
        try:
            if self.is_logged_in() and self.current_user:
                print(f"👤 Retornando usuario actual: {self.current_user.email}")
                return self.current_user
            else:
                print("❌ No hay usuario logueado o sesión inválida")
                return None
        except Exception as e:
            print(f"❌ Error obteniendo usuario actual: {e}")
            return None

    def get_current_user_safe(self) -> Optional[Usuario]:
        """Obtener usuario actual de forma ultra segura (sin validaciones)"""
        try:
            return self.current_user
        except Exception as e:
            print(f"❌ Error obteniendo usuario safe: {e}")
            return None

    def get_user_profile(self) -> Optional[PerfilUsuario]:
        """Obtener perfil del usuario actual"""
        try:
            if not self.is_logged_in():
                return None
            return PerfilUsuario.find_by_user_id(self.current_user.id)
        except Exception as e:
            print(f"❌ Error obteniendo perfil: {e}")
            return None

    def _validate_email(self, email: str) -> bool:
        """Validar formato de email"""
        if not email:
            return False
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email.strip()) is not None

    def get_session_info(self) -> dict:
        """Obtener información de la sesión - SIN LOCK"""
        try:
            if not self.is_logged_in():
                return {"logged_in": False}

            return {
                "logged_in": True,
                "user_id": self.current_user.id,
                "user_name": f"{self.current_user.nombre} {self.current_user.apellido}",
                "user_email": self.current_user.email,
                "user_role": self.current_user.rol.value if hasattr(self.current_user.rol, 'value') else str(
                    self.current_user.rol),
                "session_expires": self.session_expires.isoformat() if self.session_expires else None
            }
        except Exception as e:
            print(f"❌ Error obteniendo info de sesión: {e}")
            return {"logged_in": False}

    def debug_status(self):
        """Método para debugging - CON LOCK"""
        with self._lock:
            print("\n" + "=" * 50)
            print("🔍 DEBUG - Estado del AuthenticationManager:")
            print(f"   Singleton ID: {id(self)}")
            print(f"   is_authenticated: {self.is_authenticated}")
            print(f"   current_user: {self.current_user.email if self.current_user else 'None'}")
            print(f"   session_token: {self.session_token[:10] + '...' if self.session_token else 'None'}")
            print(f"   session_expires: {self.session_expires}")
            print("=" * 50 + "\n")

    def debug_status_no_lock(self):
        """Método para debugging - SIN LOCK (para usar en workers)"""
        print("\n" + "=" * 50)
        print("🔍 DEBUG - Estado del AuthenticationManager (NO LOCK):")
        print(f"   Singleton ID: {id(self)}")
        print(f"   is_authenticated: {self.is_authenticated}")
        print(f"   current_user: {self.current_user.email if self.current_user else 'None'}")
        print(f"   session_token: {self.session_token[:10] + '...' if self.session_token else 'None'}")
        print(f"   session_expires: {self.session_expires}")
        print("=" * 50 + "\n")


# Crear la instancia global del singleton
auth_manager = AuthenticationManager()


# Función para obtener el auth_manager (garantiza singleton)
def get_auth_manager():
    """Obtener la instancia única del AuthenticationManager"""
    return AuthenticationManager()


if __name__ == "__main__":
    # Prueba del sistema de autenticación
    print("🧪 Probando sistema de autenticación sin deadlock...")

    auth = AuthenticationManager()

    # Hacer login
    success, message = auth.login("test@alfaia.com", "test123")
    print(f"Login: {success} - {message}")

    if success:
        # Probar get_current_user sin deadlock
        user = auth.get_current_user()
        print(f"Usuario obtenido: {user.email if user else 'None'}")

        # Probar get_current_user_safe
        user_safe = auth.get_current_user_safe()
        print(f"Usuario safe: {user_safe.email if user_safe else 'None'}")

    print("✅ Prueba sin deadlock completada")
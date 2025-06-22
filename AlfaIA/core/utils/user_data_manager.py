# =============================================================================
# AlfaIA/core/utils/user_data_manager.py - CON CONEXIÓN BD SEGURA
# =============================================================================

import sys
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List

print("🔧 Inicializando user_data_manager con BD...")

# Imports seguros de BD con fallback
try:
    sys.path.append(str(Path(__file__).parent.parent.parent))
    from core.database.models import PerfilUsuario

    print("✅ Modelos de BD importados correctamente")
    BD_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Error importando modelos de BD: {e}")
    print("🔄 Funcionando sin BD por ahora")
    BD_AVAILABLE = False


    # Clase fallback para cuando no hay BD
    class PerfilUsuario:
        @classmethod
        def find_by_user_id(cls, user_id):
            return None


class UserDataManager:
    """
    Gestor de datos de usuario CON conexión a BD segura
    """

    def __init__(self, user):
        """Inicializar con usuario y cargar de BD de forma segura"""
        print(f"📊 Creando UserDataManager para: {type(user).__name__}")

        self.user = user
        self.profile = None
        self.bd_available = BD_AVAILABLE

        # Datos por defecto
        self._default_data = {
            'nombre': 'Usuario',
            'apellido': 'Demo',
            'email': 'demo@alfaia.com',
            'nivel': 'Principiante',
            'puntos': 0,
            'racha': 0,
            'ejercicios': 0,
            'tiempo': 0,
            'meta_diaria': 5
        }

        # Cargar perfil de BD si está disponible
        self._load_profile_safe()

        print(f"✅ UserDataManager inicializado (BD: {'✅' if self.bd_available else '❌'})")

    def _load_profile_safe(self):
        """Cargar perfil de BD de forma segura"""
        if not self.bd_available:
            print("⚠️ BD no disponible, usando datos por defecto")
            return

        try:
            if hasattr(self.user, 'id') and self.user.id:
                print(f"🔍 Cargando perfil desde BD para user_id: {self.user.id}")
                self.profile = PerfilUsuario.find_by_user_id(self.user.id)

                if self.profile:
                    print("✅ Perfil cargado desde BD exitosamente")
                    self._update_defaults_from_profile()
                else:
                    print("⚠️ No se encontró perfil en BD, usando defaults")
            else:
                print("⚠️ Usuario sin ID válido")
        except Exception as e:
            print(f"❌ Error cargando perfil de BD: {e}")
            self.profile = None

    def _update_defaults_from_profile(self):
        """Actualizar datos por defecto con los del perfil de BD"""
        if not self.profile:
            return

        try:
            # Actualizar con datos reales de BD
            if hasattr(self.profile, 'puntos_totales'):
                self._default_data['puntos'] = self.profile.puntos_totales

            if hasattr(self.profile, 'racha_dias_consecutivos'):
                self._default_data['racha'] = self.profile.racha_dias_consecutivos

            if hasattr(self.profile, 'ejercicios_completados'):
                self._default_data['ejercicios'] = self.profile.ejercicios_completados

            if hasattr(self.profile, 'tiempo_total_minutos'):
                self._default_data['tiempo'] = self.profile.tiempo_total_minutos

            if hasattr(self.profile, 'objetivo_diario_ejercicios'):
                self._default_data['meta_diaria'] = self.profile.objetivo_diario_ejercicios

            print("✅ Datos actualizados desde perfil de BD")
        except Exception as e:
            print(f"❌ Error actualizando datos desde perfil: {e}")

    def refresh_from_database(self):
        """Refrescar datos desde BD"""
        if self.bd_available:
            print("🔄 Refrescando datos desde BD...")
            self._load_profile_safe()
        else:
            print("⚠️ BD no disponible para refresh")

    def _safe_get_attr(self, attr_name: str, default_value: Any = None):
        """Obtener atributo de usuario de forma ultra segura"""
        try:
            if self.user and hasattr(self.user, attr_name):
                value = getattr(self.user, attr_name, default_value)
                return value if value is not None else default_value
            return default_value
        except Exception:
            return default_value

    # =============================================================================
    # MÉTODOS BÁSICOS - ULTRA SEGUROS
    # =============================================================================

    def get_display_name(self) -> str:
        """Nombre completo para mostrar"""
        try:
            nombre = self._safe_get_attr('nombre', 'Usuario')
            apellido = self._safe_get_attr('apellido', '')

            if apellido:
                return f"{nombre} {apellido}"
            return nombre
        except Exception:
            return "Usuario Demo"

    def get_first_name(self) -> str:
        """Solo el primer nombre"""
        try:
            return self._safe_get_attr('nombre', 'Usuario')
        except Exception:
            return "Usuario"

    def get_email(self) -> str:
        """Email del usuario"""
        try:
            return self._safe_get_attr('email', 'demo@alfaia.com')
        except Exception:
            return "demo@alfaia.com"

    def get_level(self) -> str:
        """Nivel actual del usuario"""
        try:
            # Intentar desde nivel_inicial del usuario
            nivel_inicial = self._safe_get_attr('nivel_inicial', None)

            if nivel_inicial:
                # Si es un enum, obtener el valor
                if hasattr(nivel_inicial, 'value'):
                    return nivel_inicial.value
                # Si es string directo
                if isinstance(nivel_inicial, str):
                    return nivel_inicial

            return "Principiante"
        except Exception:
            return "Principiante"

    def get_total_points(self) -> int:
        """Puntos totales acumulados"""
        # Primero intentar desde BD, luego fallback
        if self.profile and hasattr(self.profile, 'puntos_totales'):
            return self.profile.puntos_totales
        return self._default_data['puntos']

    def get_streak(self) -> int:
        """Racha de días consecutivos"""
        if self.profile and hasattr(self.profile, 'racha_dias_consecutivos'):
            return self.profile.racha_dias_consecutivos
        return self._default_data['racha']

    def get_completed_exercises(self) -> int:
        """Ejercicios completados"""
        if self.profile and hasattr(self.profile, 'ejercicios_completados'):
            return self.profile.ejercicios_completados
        return self._default_data['ejercicios']

    def get_study_time(self) -> int:
        """Tiempo de estudio en minutos"""
        if self.profile and hasattr(self.profile, 'tiempo_total_minutos'):
            return self.profile.tiempo_total_minutos
        return self._default_data['tiempo']

    def get_daily_goal(self) -> int:
        """Meta diaria de ejercicios"""
        if self.profile and hasattr(self.profile, 'objetivo_diario_ejercicios'):
            return self.profile.objetivo_diario_ejercicios
        return self._default_data['meta_diaria']

    def get_study_time_formatted(self) -> str:
        """Tiempo de estudio formateado"""
        minutes = self.get_study_time()
        if minutes < 60:
            return f"{minutes} min"
        hours = minutes // 60
        remaining = minutes % 60
        if remaining > 0:
            return f"{hours}h {remaining}m"
        return f"{hours}h"

    # =============================================================================
    # MÉTODOS PARA EL DASHBOARD
    # =============================================================================

    def get_stats_cards_data(self) -> List[Dict[str, Any]]:
        """Datos para las tarjetas de estadísticas del dashboard"""
        try:
            return [
                {
                    'title': 'Nivel Actual',
                    'value': self.get_level(),
                    'icon': '🎓',
                    'color': '#4A90E2',
                    'description': 'Tu nivel de español'
                },
                {
                    'title': 'Meta Diaria',
                    'value': f"0 / {self.get_daily_goal()}",
                    'icon': '📝',
                    'color': '#7ED321',
                    'description': 'Ejercicios de hoy'
                },
                {
                    'title': 'Racha',
                    'value': f"{self.get_streak()} días",
                    'icon': '🔥',
                    'color': '#F5A623',
                    'description': 'Días consecutivos'
                },
                {
                    'title': 'Puntos',
                    'value': f"{self.get_total_points():,}",
                    'icon': '⭐',
                    'color': '#FFD700',
                    'description': 'Puntos acumulados'
                },
                {
                    'title': 'Ejercicios',
                    'value': f"{self.get_completed_exercises():,}",
                    'icon': '🏆',
                    'color': '#9013FE',
                    'description': 'Completados'
                },
                {
                    'title': 'Tiempo',
                    'value': self.get_study_time_formatted(),
                    'icon': '⏱️',
                    'color': '#FF6B6B',
                    'description': 'Tiempo de estudio'
                }
            ]
        except Exception:
            # Fallback ultra seguro
            return [
                {'title': 'Nivel', 'value': 'Principiante', 'icon': '🎓', 'color': '#4A90E2',
                 'description': 'Nivel actual'},
                {'title': 'Meta', 'value': '0 / 5', 'icon': '📝', 'color': '#7ED321', 'description': 'Ejercicios hoy'},
                {'title': 'Racha', 'value': '0 días', 'icon': '🔥', 'color': '#F5A623', 'description': 'Días seguidos'},
                {'title': 'Puntos', 'value': '0', 'icon': '⭐', 'color': '#FFD700', 'description': 'Puntos totales'},
                {'title': 'Ejercicios', 'value': '0', 'icon': '🏆', 'color': '#9013FE', 'description': 'Completados'},
                {'title': 'Tiempo', 'value': '0 min', 'icon': '⏱️', 'color': '#FF6B6B', 'description': 'Tiempo estudio'}
            ]

    def get_daily_progress(self) -> Dict[str, Any]:
        """Progreso del día actual"""
        try:
            completed_today = 0
            goal = self.get_daily_goal()

            return {
                'completed': completed_today,
                'goal': goal,
                'percentage': 0.0,
                'remaining': goal
            }
        except Exception:
            return {
                'completed': 0,
                'goal': 5,
                'percentage': 0.0,
                'remaining': 5
            }

    def get_achievement_level(self) -> Dict[str, Any]:
        """Nivel de logro basado en puntos"""
        try:
            points = self.get_total_points()

            return {
                'current_level': 'Principiante',
                'current_icon': '🌱',
                'current_description': 'Empezando el viaje',
                'total_points': points,
                'next_level': 'Aprendiz',
                'points_to_next': 100 - points,
                'progress_percentage': min(100, points)
            }
        except Exception:
            return {
                'current_level': 'Principiante',
                'current_icon': '🌱',
                'current_description': 'Empezando',
                'total_points': 0,
                'next_level': 'Aprendiz',
                'points_to_next': 100,
                'progress_percentage': 0
            }

    # =============================================================================
    # MÉTODOS DE ACTUALIZACIÓN DE BD
    # =============================================================================

    def update_progress(self, exercises_completed: int = 0, time_spent: int = 0, points_earned: int = 0) -> bool:
        """
        Actualizar progreso en BD

        Args:
            exercises_completed: Ejercicios completados hoy
            time_spent: Tiempo en minutos
            points_earned: Puntos ganados
        """
        if not self.bd_available or not self.profile:
            print("⚠️ BD no disponible o perfil no cargado")
            # Actualizar al menos los datos locales
            self._default_data['ejercicios'] += exercises_completed
            self._default_data['tiempo'] += time_spent
            self._default_data['puntos'] += points_earned
            return False

        try:
            # Actualizar perfil
            self.profile.ejercicios_completados += exercises_completed
            self.profile.tiempo_total_minutos += time_spent
            self.profile.puntos_totales += points_earned
            self.profile.experiencia_total += points_earned

            # Verificar meta diaria para racha
            if exercises_completed >= self.get_daily_goal():
                self.profile.racha_dias_consecutivos += 1

            # Guardar en BD
            if self.profile.save():
                print(
                    f"✅ Progreso guardado en BD: +{exercises_completed} ejercicios, +{time_spent}min, +{points_earned}pts")
                self._update_defaults_from_profile()  # Actualizar cache local
                return True
            else:
                print("❌ Error guardando en BD")
                return False

        except Exception as e:
            print(f"❌ Error actualizando progreso en BD: {e}")
            return False

    def create_profile_if_missing(self) -> bool:
        """Crear perfil en BD si no existe"""
        if not self.bd_available:
            return False

        try:
            if self.profile:
                return True  # Ya existe

            if not hasattr(self.user, 'id') or not self.user.id:
                print("❌ Usuario sin ID, no se puede crear perfil")
                return False

            # Crear nuevo perfil
            from core.database.models import PerfilUsuario, EstiloAprendizaje

            new_profile = PerfilUsuario(
                user_id=self.user.id,
                nivel_lectura=1,
                nivel_gramatica=1,
                nivel_vocabulario=1,
                puntos_totales=0,
                experiencia_total=0,
                racha_dias_consecutivos=0,
                tiempo_total_minutos=0,
                ejercicios_completados=0,
                objetivo_diario_ejercicios=5,
                estilo_aprendizaje=EstiloAprendizaje.MIXTO,
                preferencias_json={
                    "tema": "light",
                    "notificaciones": True,
                    "sonidos": True,
                    "difficulty_auto_adjust": True
                },
                estadisticas_json={}
            )

            if new_profile.save():
                self.profile = new_profile
                print(f"✅ Perfil creado en BD para user_id: {self.user.id}")
                return True
            else:
                print("❌ Error guardando nuevo perfil")
                return False

        except Exception as e:
            print(f"❌ Error creando perfil: {e}")
            return False

    def update_daily_goal(self, new_goal: int) -> bool:
        """Actualizar meta diaria"""
        if not self.bd_available or not self.profile:
            self._default_data['meta_diaria'] = new_goal
            return False

        try:
            self.profile.objetivo_diario_ejercicios = new_goal
            if self.profile.save():
                self._default_data['meta_diaria'] = new_goal
                print(f"✅ Meta diaria actualizada a {new_goal}")
                return True
            return False
        except Exception as e:
            print(f"❌ Error actualizando meta diaria: {e}")
            return False

    def reset_streak(self) -> bool:
        """Resetear racha (cuando se pierde)"""
        if not self.bd_available or not self.profile:
            self._default_data['racha'] = 0
            return False

        try:
            self.profile.racha_dias_consecutivos = 0
            if self.profile.save():
                self._default_data['racha'] = 0
                print("📉 Racha reseteada")
                return True
            return False
        except Exception as e:
            print(f"❌ Error reseteando racha: {e}")
            return False

    def is_valid(self) -> bool:
        """Verificar si los datos son válidos"""
        try:
            return (
                    self.user is not None and
                    self.get_display_name() != "" and
                    self.get_email() != ""
            )
        except Exception:
            return False

    def get_summary(self) -> Dict[str, Any]:
        """Resumen completo del usuario"""
        try:
            return {
                'user_info': {
                    'name': self.get_display_name(),
                    'email': self.get_email(),
                    'level': self.get_level()
                },
                'progress': {
                    'points': self.get_total_points(),
                    'streak': self.get_streak(),
                    'exercises': self.get_completed_exercises(),
                    'study_time': self.get_study_time(),
                    'daily_goal': self.get_daily_goal()
                },
                'valid': self.is_valid()
            }
        except Exception:
            return {
                'user_info': {
                    'name': 'Usuario Demo',
                    'email': 'demo@alfaia.com',
                    'level': 'Principiante'
                },
                'progress': {
                    'points': 0,
                    'streak': 0,
                    'exercises': 0,
                    'study_time': 0,
                    'daily_goal': 5
                },
                'valid': False
            }

    def __str__(self) -> str:
        """Representación string"""
        try:
            return f"UserDataManager({self.get_display_name()}, {self.get_level()})"
        except Exception:
            return "UserDataManager(Error)"

    def __repr__(self) -> str:
        """Representación técnica"""
        try:
            return f"UserDataManager(valid={self.is_valid()})"
        except Exception:
            return "UserDataManager(error=True)"


# =============================================================================
# FUNCIÓN DE UTILIDAD
# =============================================================================

def create_demo_user_data_manager():
    """Crear UserDataManager demo para testing"""
    try:
        class DemoUser:
            def __init__(self):
                self.id = 999
                self.nombre = "Usuario"
                self.apellido = "Demo"
                self.email = "demo@alfaia.com"
                self.nivel_inicial = "Principiante"

        return UserDataManager(DemoUser())
    except Exception:
        # Ultra fallback
        return UserDataManager(None)


# =============================================================================
# TESTING BÁSICO
# =============================================================================
if __name__ == "__main__":
    print("🧪 Probando UserDataManager...")

    try:
        # Test con usuario demo
        manager = create_demo_user_data_manager()
        print(f"Nombre: {manager.get_display_name()}")
        print(f"Email: {manager.get_email()}")
        print(f"Nivel: {manager.get_level()}")
        print(f"Válido: {manager.is_valid()}")

        # Test de stats
        stats = manager.get_stats_cards_data()
        print(f"Stats generadas: {len(stats)} tarjetas")

        print("✅ UserDataManager funciona correctamente")

    except Exception as e:
        print(f"❌ Error en testing: {e}")
        import traceback

        traceback.print_exc()
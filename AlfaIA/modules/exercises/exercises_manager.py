# =============================================================================
# AlfaIA/modules/exercises/exercises_manager.py - Gestor de Ejercicios Base
# =============================================================================

import json
import random
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from enum import Enum
import sys
from pathlib import Path

# Agregar path para imports
sys.path.append(str(Path(__file__).parent.parent.parent))

try:
    from core.database.connection import DatabaseManager
    from core.database.models import Usuario

    print("✅ Dependencias de base de datos importadas")
except ImportError as e:
    print(f"⚠️ Error importando BD: {e}")
    DatabaseManager = None


class TipoEjercicio(Enum):
    """Tipos de ejercicios disponibles"""
    COMPLETAR_PALABRA = "Completar_Palabra"
    ENCONTRAR_ERROR = "Encontrar_Error"
    CLASIFICAR_PALABRA = "Clasificar_Palabra"
    COMPRENSION = "Comprension"
    ORDENAR_FRASE = "Ordenar_Frase"


class DificultadEjercicio:
    """Niveles de dificultad de ejercicios"""
    FACIL = 1
    INTERMEDIO = 5
    DIFICIL = 10

    @classmethod
    def get_level_name(cls, level: int) -> str:
        """Obtener nombre del nivel"""
        if level <= 3:
            return "Fácil"
        elif level <= 7:
            return "Intermedio"
        else:
            return "Difícil"


class ExercisesManager:
    """Gestor principal de ejercicios"""

    def __init__(self):
        self.db_manager = DatabaseManager() if DatabaseManager else None
        self.nlp_analyzer = None  # Se cargará después
        print("🎯 ExercisesManager inicializado")

    def get_exercises_by_type(self, tipo: TipoEjercicio, limite: int = 10) -> List[Dict[str, Any]]:
        """Obtener ejercicios por tipo"""
        try:
            if not self.db_manager:
                print("⚠️ BD no disponible, retornando ejercicios demo")
                return self._get_demo_exercises(tipo, limite)

            query = """
                    SELECT e.*, c.nombre as categoria_nombre, c.color_hex
                    FROM ejercicios e
                             LEFT JOIN categorias c ON e.categoria_id = c.id
                    WHERE e.tipo = %s \
                      AND e.activo = TRUE
                    ORDER BY e.nivel_dificultad, RAND()
                    LIMIT %s \
                    """

            results = self.db_manager.execute_query(query, (tipo.value, limite))

            if results:
                exercises = []
                for row in results:
                    exercise = self._parse_exercise_row(row)
                    exercises.append(exercise)

                print(f"✅ {len(exercises)} ejercicios de {tipo.value} obtenidos de BD")
                return exercises
            else:
                print(f"⚠️ No se encontraron ejercicios de {tipo.value} en BD")
                return self._get_demo_exercises(tipo, limite)

        except Exception as e:
            print(f"❌ Error obteniendo ejercicios: {e}")
            return self._get_demo_exercises(tipo, limite)

    def get_exercises_by_level(self, nivel: int, limite: int = 10) -> List[Dict[str, Any]]:
        """Obtener ejercicios por nivel de dificultad"""
        try:
            if not self.db_manager:
                return self._get_demo_exercises_by_level(nivel, limite)

            query = """
                    SELECT e.*, c.nombre as categoria_nombre, c.color_hex
                    FROM ejercicios e
                             LEFT JOIN categorias c ON e.categoria_id = c.id
                    WHERE e.nivel_dificultad = %s \
                      AND e.activo = TRUE
                    ORDER BY RAND()
                    LIMIT %s \
                    """

            results = self.db_manager.execute_query(query, (nivel, limite))

            if results:
                exercises = []
                for row in results:
                    exercise = self._parse_exercise_row(row)
                    exercises.append(exercise)

                print(f"✅ {len(exercises)} ejercicios de nivel {nivel} obtenidos")
                return exercises
            else:
                return self._get_demo_exercises_by_level(nivel, limite)

        except Exception as e:
            print(f"❌ Error obteniendo ejercicios por nivel: {e}")
            return self._get_demo_exercises_by_level(nivel, limite)

    def get_random_exercise(self, user_level: int = 1) -> Optional[Dict[str, Any]]:
        """Obtener ejercicio aleatorio según el nivel del usuario"""
        try:
            # Calcular rango de dificultad basado en nivel del usuario
            min_difficulty = max(1, user_level - 1)
            max_difficulty = min(10, user_level + 2)

            if not self.db_manager:
                return self._get_demo_random_exercise(user_level)

            query = """
                    SELECT e.*, c.nombre as categoria_nombre, c.color_hex
                    FROM ejercicios e
                             LEFT JOIN categorias c ON e.categoria_id = c.id
                    WHERE e.nivel_dificultad BETWEEN %s AND %s
                      AND e.activo = TRUE
                    ORDER BY RAND()
                    LIMIT 1 \
                    """

            results = self.db_manager.execute_query(query, (min_difficulty, max_difficulty))

            if results and len(results) > 0:
                exercise = self._parse_exercise_row(results[0])
                print(f"✅ Ejercicio aleatorio obtenido: {exercise['titulo']}")
                return exercise
            else:
                return self._get_demo_random_exercise(user_level)

        except Exception as e:
            print(f"❌ Error obteniendo ejercicio aleatorio: {e}")
            return self._get_demo_random_exercise(user_level)

    def save_exercise_result(self, user_id: int, exercise_id: int,
                             respuestas: Dict[str, Any], puntos: int,
                             precision: float, tiempo: int) -> bool:
        """Guardar resultado de ejercicio"""
        try:
            if not self.db_manager:
                print("⚠️ BD no disponible, resultado no guardado")
                return False

            query = """
                    INSERT INTO resultados_ejercicios
                    (user_id, ejercicio_id, respuestas_usuario_json, puntos_obtenidos,
                     precision_porcentaje, tiempo_segundos, completado, fecha_intento)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s) \
                    """

            params = (
                user_id, exercise_id, json.dumps(respuestas, ensure_ascii=False),
                puntos, precision, tiempo, True, datetime.now()
            )

            success = self.db_manager.execute_non_query(query, params)

            if success:
                print(f"✅ Resultado guardado: {puntos} puntos, {precision}% precisión")
                return True
            else:
                print("❌ Error guardando resultado")
                return False

        except Exception as e:
            print(f"❌ Error guardando resultado: {e}")
            return False

    def get_user_progress(self, user_id: int) -> Dict[str, Any]:
        """Obtener progreso del usuario en ejercicios"""
        try:
            if not self.db_manager:
                return self._get_demo_progress()

            query = """
                    SELECT COUNT(*)                     as total_ejercicios, \
                           AVG(puntos_obtenidos)        as puntos_promedio, \
                           AVG(precision_porcentaje)    as precision_promedio, \
                           SUM(tiempo_segundos)         as tiempo_total, \
                           COUNT(DISTINCT ejercicio_id) as ejercicios_unicos
                    FROM resultados_ejercicios
                    WHERE user_id = %s \
                      AND completado = TRUE \
                    """

            results = self.db_manager.execute_query(query, (user_id,))

            if results and len(results) > 0:
                row = results[0]
                progress = {
                    'total_ejercicios': row[0] or 0,
                    'puntos_promedio': round(row[1] or 0, 2),
                    'precision_promedio': round(row[2] or 0, 2),
                    'tiempo_total_minutos': round((row[3] or 0) / 60, 2),
                    'ejercicios_unicos': row[4] or 0
                }

                print(f"✅ Progreso obtenido para usuario {user_id}")
                return progress
            else:
                return self._get_demo_progress()

        except Exception as e:
            print(f"❌ Error obteniendo progreso: {e}")
            return self._get_demo_progress()

    def _parse_exercise_row(self, row: tuple) -> Dict[str, Any]:
        """Parsear fila de ejercicio de la BD"""
        try:
            contenido = json.loads(row[4]) if row[4] else {}
            respuestas = json.loads(row[5]) if row[5] else {}
            explicaciones = json.loads(row[6]) if row[6] else {}
            pistas = json.loads(row[12]) if row[12] else {}

            return {
                'id': row[0],
                'tipo': row[1],
                'titulo': row[2],
                'instrucciones': row[3],
                'contenido': contenido,
                'respuestas_correctas': respuestas,
                'explicaciones': explicaciones,
                'categoria_id': row[7],
                'nivel_dificultad': row[8],
                'puntos_maximos': row[9],
                'tiempo_limite': row[10],
                'pistas': pistas,
                'activo': row[11],
                'categoria_nombre': row[14] if len(row) > 14 else "General",
                'categoria_color': row[15] if len(row) > 15 else "#4A90E2"
            }
        except Exception as e:
            print(f"❌ Error parseando ejercicio: {e}")
            return self._get_default_exercise()

    def _get_demo_exercises(self, tipo: TipoEjercicio, limite: int) -> List[Dict[str, Any]]:
        """Obtener ejercicios demo cuando no hay BD"""
        demos = {
            TipoEjercicio.COMPLETAR_PALABRA: [
                {
                    'id': 1,
                    'tipo': 'Completar_Palabra',
                    'titulo': 'Completa las palabras',
                    'instrucciones': 'Completa las palabras que faltan en las oraciones',
                    'contenido': {
                        'oraciones': [
                            'El _ato juega en el jardín',
                            'La _asa está muy limpia',
                            'Mi _adre cocina muy bien'
                        ],
                        'opciones': [
                            ['gato', 'pato', 'rato'],
                            ['casa', 'masa', 'tasa'],
                            ['madre', 'padre', 'andre']
                        ]
                    },
                    'respuestas_correctas': [['gato'], ['casa'], ['madre']],
                    'nivel_dificultad': 2,
                    'puntos_maximos': 30,
                    'tiempo_limite': 120,
                    'categoria_nombre': 'Vocabulario',
                    'categoria_color': '#7ED321'
                }
            ],
            TipoEjercicio.ENCONTRAR_ERROR: [
                {
                    'id': 2,
                    'tipo': 'Encontrar_Error',
                    'titulo': 'Encuentra los errores',
                    'instrucciones': 'Identifica y corrige los errores en las siguientes oraciones',
                    'contenido': {
                        'oraciones': [
                            'Los niña juegan en el parque',
                            'Ayer fuí al cine con mis amigos',
                            'El agua esta muy fria'
                        ]
                    },
                    'respuestas_correctas': [
                        {'posicion': 1, 'error': 'niña', 'correccion': 'niñas'},
                        {'posicion': 1, 'error': 'fuí', 'correccion': 'fui'},
                        {'posicion': 2, 'error': 'esta', 'correccion': 'está'},
                        {'posicion': 3, 'error': 'fria', 'correccion': 'fría'}
                    ],
                    'nivel_dificultad': 4,
                    'puntos_maximos': 40,
                    'tiempo_limite': 180,
                    'categoria_nombre': 'Gramática',
                    'categoria_color': '#4A90E2'
                }
            ],
            TipoEjercicio.CLASIFICAR_PALABRA: [
                {
                    'id': 3,
                    'tipo': 'Clasificar_Palabra',
                    'titulo': 'Clasifica las palabras',
                    'instrucciones': 'Arrastra cada palabra a su categoría gramatical correcta',
                    'contenido': {
                        'palabras': ['correr', 'casa', 'bonito', 'rápidamente', 'con', 'y'],
                        'categorias': ['Verbo', 'Sustantivo', 'Adjetivo', 'Adverbio', 'Preposición', 'Conjunción']
                    },
                    'respuestas_correctas': {
                        'correr': 'Verbo',
                        'casa': 'Sustantivo',
                        'bonito': 'Adjetivo',
                        'rápidamente': 'Adverbio',
                        'con': 'Preposición',
                        'y': 'Conjunción'
                    },
                    'nivel_dificultad': 3,
                    'puntos_maximos': 60,
                    'tiempo_limite': 150,
                    'categoria_nombre': 'Gramática',
                    'categoria_color': '#4A90E2'
                }
            ]
        }

        return demos.get(tipo, [self._get_default_exercise()])[:limite]

    def _get_demo_exercises_by_level(self, nivel: int, limite: int) -> List[Dict[str, Any]]:
        """Obtener ejercicios demo por nivel"""
        all_demos = []
        for tipo in TipoEjercicio:
            all_demos.extend(self._get_demo_exercises(tipo, 5))

        # Filtrar por nivel
        filtered = [ex for ex in all_demos if ex['nivel_dificultad'] == nivel]
        return filtered[:limite]

    def _get_demo_random_exercise(self, user_level: int) -> Dict[str, Any]:
        """Obtener ejercicio demo aleatorio"""
        tipos = list(TipoEjercicio)
        tipo_random = random.choice(tipos)
        demos = self._get_demo_exercises(tipo_random, 5)

        if demos:
            return random.choice(demos)
        else:
            return self._get_default_exercise()

    def _get_demo_progress(self) -> Dict[str, Any]:
        """Obtener progreso demo"""
        return {
            'total_ejercicios': 15,
            'puntos_promedio': 75.5,
            'precision_promedio': 82.3,
            'tiempo_total_minutos': 45.2,
            'ejercicios_unicos': 8
        }

    def _get_default_exercise(self) -> Dict[str, Any]:
        """Obtener ejercicio por defecto"""
        return {
            'id': 0,
            'tipo': 'Completar_Palabra',
            'titulo': 'Ejercicio de demostración',
            'instrucciones': 'Este es un ejercicio de ejemplo',
            'contenido': {'ejemplo': True},
            'respuestas_correctas': {},
            'nivel_dificultad': 1,
            'puntos_maximos': 10,
            'tiempo_limite': 60,
            'categoria_nombre': 'Demo',
            'categoria_color': '#4A90E2'
        }


# =============================================================================
# TESTING
# =============================================================================
if __name__ == "__main__":
    print("🧪 Probando ExercisesManager...")

    manager = ExercisesManager()

    # Probar obtener ejercicios por tipo
    ejercicios_completar = manager.get_exercises_by_type(TipoEjercicio.COMPLETAR_PALABRA, 3)
    print(f"Ejercicios de completar palabra: {len(ejercicios_completar)}")

    # Probar ejercicio aleatorio
    ejercicio_random = manager.get_random_exercise(3)
    if ejercicio_random:
        print(f"Ejercicio aleatorio: {ejercicio_random['titulo']}")

    # Probar progreso
    progress = manager.get_user_progress(1)
    print(f"Progreso demo: {progress}")

    print("✅ Pruebas completadas")
# =============================================================================
# AlfaIA/modules/exercises/exercise_generator.py - Generador de Ejercicios Adaptativos
# =============================================================================

import re
import random
import logging
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass
from enum import Enum
import sys
from pathlib import Path
from collections import Counter

# Agregar el directorio raíz al path para imports
sys.path.append(str(Path(__file__).parent.parent.parent))

# Imports de módulos NLP
try:
    from modules.nlp.text_analyzer import TextAnalyzer, DifficultyLevel
    from modules.nlp.grammar_checker import GrammarChecker
    from modules.nlp.difficulty_calculator import DifficultyCalculator, EducationLevel

    NLP_MODULES_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Algunos módulos NLP no disponibles: {e}")
    NLP_MODULES_AVAILABLE = False


    # Definir clases básicas si no están disponibles
    class DifficultyLevel(Enum):
        MUY_FACIL = "muy_facil"
        FACIL = "facil"
        INTERMEDIO = "intermedio"
        DIFICIL = "dificil"
        MUY_DIFICIL = "muy_dificil"


    class EducationLevel(Enum):
        PRIMARIA_INICIAL = "primaria_inicial"
        PRIMARIA_MEDIA = "primaria_media"
        PRIMARIA_SUPERIOR = "primaria_superior"
        SECUNDARIA = "secundaria"
        UNIVERSITARIO = "universitario"

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print("🔧 Inicializando generador de ejercicios...")


# =============================================================================
# ENUMS Y DATACLASSES
# =============================================================================

class ExerciseType(Enum):
    """Tipos de ejercicios disponibles"""
    COMPRENSION_LECTORA = "comprension_lectora"
    GRAMATICA = "gramatica"
    VOCABULARIO = "vocabulario"
    ORTOGRAFIA = "ortografia"
    PUNTUACION = "puntuacion"
    SINONIMOS_ANTONIMOS = "sinonimos_antonimos"
    ORDENAR_PALABRAS = "ordenar_palabras"
    COMPLETAR_ORACIONES = "completar_oraciones"
    IDENTIFICAR_ERRORES = "identificar_errores"
    ANALISIS_MORFOLOGICO = "analisis_morfologico"


class ExerciseDifficulty(Enum):
    """Niveles de dificultad para ejercicios"""
    PRINCIPIANTE = "principiante"
    BASICO = "basico"
    INTERMEDIO = "intermedio"
    AVANZADO = "avanzado"
    EXPERTO = "experto"


class QuestionType(Enum):
    """Tipos de preguntas"""
    MULTIPLE_CHOICE = "multiple_choice"
    TRUE_FALSE = "true_false"
    FILL_IN_BLANK = "fill_in_blank"
    SHORT_ANSWER = "short_answer"
    DRAG_DROP = "drag_drop"
    MATCHING = "matching"


@dataclass
class ExerciseQuestion:
    """Representación de una pregunta de ejercicio"""
    question_text: str
    question_type: QuestionType
    correct_answer: Union[str, List[str]]
    options: Optional[List[str]] = None
    explanation: Optional[str] = None
    hint: Optional[str] = None
    difficulty_points: int = 1
    estimated_time: float = 30.0  # segundos


@dataclass
class Exercise:
    """Representación completa de un ejercicio"""
    title: str
    description: str
    exercise_type: ExerciseType
    difficulty: ExerciseDifficulty
    target_level: EducationLevel
    questions: List[ExerciseQuestion]

    # Metadatos
    estimated_duration: float  # minutos
    total_points: int
    skills_practiced: List[str]
    source_text: Optional[str] = None

    # Configuración
    randomize_questions: bool = True
    allow_retries: bool = True
    show_hints: bool = True


@dataclass
class ExerciseGenerationConfig:
    """Configuración para generación de ejercicios"""
    exercise_type: ExerciseType
    difficulty: ExerciseDifficulty
    target_level: EducationLevel
    num_questions: int = 10
    question_types: List[QuestionType] = None
    use_source_text: bool = True
    adapt_to_user_level: bool = True


# =============================================================================
# CLASE PRINCIPAL DE GENERACIÓN DE EJERCICIOS
# =============================================================================

class ExerciseGenerator:
    """
    Generador de ejercicios adaptativos para AlfaIA
    """

    def __init__(self):
        """Inicializar generador"""
        self.logger = logger

        # Inicializar módulos NLP si están disponibles
        if NLP_MODULES_AVAILABLE:
            self.text_analyzer = TextAnalyzer()
            self.grammar_checker = GrammarChecker()
            self.difficulty_calculator = DifficultyCalculator()
        else:
            self.text_analyzer = None
            self.grammar_checker = None
            self.difficulty_calculator = None

        # Cargar bases de datos de contenido
        self._load_content_databases()

        # Configurar generadores específicos
        self._setup_question_generators()

        print("✅ ExerciseGenerator inicializado")

    def _load_content_databases(self):
        """Cargar bases de datos de contenido para ejercicios"""

        # Vocabulario por nivel
        self.vocabulary_by_level = {
            EducationLevel.PRIMARIA_INICIAL: {
                'sustantivos': ['casa', 'perro', 'gato', 'sol', 'luna', 'agua', 'fuego', 'tierra'],
                'verbos': ['correr', 'saltar', 'comer', 'beber', 'dormir', 'jugar', 'leer', 'escribir'],
                'adjetivos': ['grande', 'pequeño', 'bonito', 'feo', 'rápido', 'lento', 'alto', 'bajo']
            },
            EducationLevel.PRIMARIA_MEDIA: {
                'sustantivos': ['naturaleza', 'educación', 'familia', 'trabajo', 'escuela', 'biblioteca'],
                'verbos': ['estudiar', 'investigar', 'descubrir', 'construir', 'desarrollar', 'explicar'],
                'adjetivos': ['inteligente', 'creativo', 'responsable', 'organizado', 'curioso']
            },
            EducationLevel.SECUNDARIA: {
                'sustantivos': ['tecnología', 'ciencia', 'cultura', 'sociedad', 'economía', 'política'],
                'verbos': ['analizar', 'evaluar', 'interpretar', 'argumentar', 'demostrar', 'comparar'],
                'adjetivos': ['complejo', 'innovador', 'eficiente', 'sostenible', 'democrático']
            }
        }

        # Patrones gramaticales
        self.grammar_patterns = {
            'concordancia': [
                'El niño [come/comen] manzanas',
                'Las flores [es/son] hermosas',
                'Mi hermana [estudia/estudian] medicina'
            ],
            'tiempos_verbales': [
                'Ayer [voy/fui] al parque',
                'Mañana [estudiará/estudió] para el examen',
                'Ahora [está/estuvo] leyendo'
            ],
            'pronombres': [
                '[A mi/A mí] me gusta leer',
                'Ese libro es [tuyo/tuya]',
                '[Se/Sé] que tienes razón'
            ]
        }

        # Textos base para comprensión lectora
        self.reading_texts = {
            EducationLevel.PRIMARIA_INICIAL: [
                "El perro de Ana es muy juguetón. Le gusta correr por el parque y jugar con la pelota. Cada mañana, Ana lo lleva a caminar. El perro se llama Rex y es de color marrón.",
                "En el jardín hay muchas flores. Las rosas son rojas, las margaritas son blancas y los girasoles son amarillos. Las abejas vuelan de flor en flor buscando néctar."
            ],
            EducationLevel.PRIMARIA_MEDIA: [
                "Los ecosistemas son comunidades de seres vivos que interactúan entre sí y con su ambiente. En un bosque, los árboles proporcionan oxígeno, los animales se alimentan de plantas y otros animales, y todo está conectado en un equilibrio natural.",
                "La fotosíntesis es el proceso por el cual las plantas convierten la luz solar en energía. Durante este proceso, las plantas toman dióxido de carbono del aire y agua del suelo para producir glucosa y oxígeno."
            ],
            EducationLevel.SECUNDARIA: [
                "La revolución digital ha transformado radicalmente la forma en que nos comunicamos, trabajamos y accedemos a la información. Las redes sociales han creado nuevas formas de interacción social, mientras que la inteligencia artificial promete revolucionar múltiples sectores de la economía.",
                "El cambio climático representa uno de los desafíos más importantes de nuestro tiempo. Los gases de efecto invernadero, principalmente el dióxido de carbono, están alterando los patrones climáticos globales y amenazando la biodiversidad del planeta."
            ]
        }

        # Palabras con errores comunes
        self.common_spelling_errors = {
            'haber': 'a ver',
            'echo': 'hecho',
            'asta': 'hasta',
            'cojer': 'coger',
            'haiga': 'haya',
            'nadies': 'nadie',
            'dijistes': 'dijiste',
            'fuistes': 'fuiste'
        }

        # Sinónimos y antónimos
        self.synonyms_antonyms = {
            'grande': {
                'sinónimos': ['enorme', 'gigante', 'inmenso', 'colosal'],
                'antónimos': ['pequeño', 'diminuto', 'minúsculo', 'tiny']
            },
            'feliz': {
                'sinónimos': ['alegre', 'contento', 'dichoso', 'gozoso'],
                'antónimos': ['triste', 'melancólico', 'deprimido', 'abatido']
            },
            'rápido': {
                'sinónimos': ['veloz', 'acelerado', 'ligero', 'presto'],
                'antónimos': ['lento', 'pausado', 'moroso', 'tardo']
            }
        }

    def _setup_question_generators(self):
        """Configurar generadores específicos de preguntas"""
        self.question_generators = {
            ExerciseType.COMPRENSION_LECTORA: self._generate_reading_comprehension,
            ExerciseType.GRAMATICA: self._generate_grammar_questions,
            ExerciseType.VOCABULARIO: self._generate_vocabulary_questions,
            ExerciseType.ORTOGRAFIA: self._generate_spelling_questions,
            ExerciseType.SINONIMOS_ANTONIMOS: self._generate_synonyms_antonyms,
            ExerciseType.COMPLETAR_ORACIONES: self._generate_fill_in_blank,
            ExerciseType.IDENTIFICAR_ERRORES: self._generate_error_identification,
            ExerciseType.ORDENAR_PALABRAS: self._generate_word_order
        }

    def generate_exercise(self, config: ExerciseGenerationConfig,
                          source_text: Optional[str] = None) -> Exercise:
        """
        Generar ejercicio completo según configuración

        Args:
            config: Configuración del ejercicio
            source_text: Texto fuente opcional

        Returns:
            Exercise: Ejercicio generado
        """
        try:
            print(f"🎯 Generando ejercicio: {config.exercise_type.value}")
            print(f"📊 Nivel: {config.target_level.value}, Dificultad: {config.difficulty.value}")

            # Seleccionar o analizar texto fuente
            if config.use_source_text and source_text:
                selected_text = source_text
                print(f"📝 Usando texto proporcionado ({len(source_text)} caracteres)")
            else:
                selected_text = self._select_appropriate_text(config.target_level)
                print(f"📝 Texto seleccionado automáticamente")

            # Adaptar dificultad si es necesario
            if config.adapt_to_user_level and self.difficulty_calculator:
                analysis = self.difficulty_calculator.calculate_difficulty(selected_text)
                if analysis.target_education_level != config.target_level:
                    print(
                        f"⚠️ Ajustando dificultad: {analysis.target_education_level.value} → {config.target_level.value}")

            # Generar preguntas
            generator = self.question_generators.get(config.exercise_type)
            if not generator:
                raise ValueError(f"Generador no disponible para {config.exercise_type.value}")

            questions = generator(config, selected_text)

            # Crear ejercicio
            exercise = Exercise(
                title=self._generate_exercise_title(config),
                description=self._generate_exercise_description(config),
                exercise_type=config.exercise_type,
                difficulty=config.difficulty,
                target_level=config.target_level,
                questions=questions[:config.num_questions],
                estimated_duration=self._calculate_duration(questions[:config.num_questions]),
                total_points=sum(q.difficulty_points for q in questions[:config.num_questions]),
                skills_practiced=self._identify_skills_practiced(config.exercise_type),
                source_text=selected_text if config.use_source_text else None
            )

            print(f"✅ Ejercicio generado: {len(exercise.questions)} preguntas, {exercise.total_points} puntos")
            return exercise

        except Exception as e:
            error_msg = f"Error generando ejercicio: {str(e)}"
            self.logger.error(error_msg)
            return self._create_fallback_exercise(config)

    def _select_appropriate_text(self, level: EducationLevel) -> str:
        """Seleccionar texto apropiado para el nivel"""
        texts = self.reading_texts.get(level, self.reading_texts[EducationLevel.PRIMARIA_MEDIA])
        return random.choice(texts)

    def _generate_exercise_title(self, config: ExerciseGenerationConfig) -> str:
        """Generar título del ejercicio"""
        type_names = {
            ExerciseType.COMPRENSION_LECTORA: "Comprensión Lectora",
            ExerciseType.GRAMATICA: "Gramática",
            ExerciseType.VOCABULARIO: "Vocabulario",
            ExerciseType.ORTOGRAFIA: "Ortografía",
            ExerciseType.SINONIMOS_ANTONIMOS: "Sinónimos y Antónimos",
            ExerciseType.COMPLETAR_ORACIONES: "Completar Oraciones",
            ExerciseType.IDENTIFICAR_ERRORES: "Identificar Errores",
            ExerciseType.ORDENAR_PALABRAS: "Ordenar Palabras"
        }

        base_title = type_names.get(config.exercise_type, "Ejercicio")
        level_suffix = config.difficulty.value.capitalize()

        return f"{base_title} - Nivel {level_suffix}"

    def _generate_exercise_description(self, config: ExerciseGenerationConfig) -> str:
        """Generar descripción del ejercicio"""
        descriptions = {
            ExerciseType.COMPRENSION_LECTORA: "Lee atentamente el texto y responde las preguntas sobre su contenido.",
            ExerciseType.GRAMATICA: "Identifica y corrige los errores gramaticales en las oraciones.",
            ExerciseType.VOCABULARIO: "Demuestra tu conocimiento del vocabulario respondiendo las preguntas.",
            ExerciseType.ORTOGRAFIA: "Encuentra y corrige los errores ortográficos.",
            ExerciseType.SINONIMOS_ANTONIMOS: "Identifica sinónimos y antónimos de las palabras indicadas.",
            ExerciseType.COMPLETAR_ORACIONES: "Completa las oraciones con las palabras correctas.",
            ExerciseType.IDENTIFICAR_ERRORES: "Encuentra los errores en el texto y propón correcciones.",
            ExerciseType.ORDENAR_PALABRAS: "Ordena las palabras para formar oraciones correctas."
        }

        return descriptions.get(config.exercise_type, "Completa este ejercicio siguiendo las instrucciones.")

    def _calculate_duration(self, questions: List[ExerciseQuestion]) -> float:
        """Calcular duración estimada en minutos"""
        total_seconds = sum(q.estimated_time for q in questions)
        return total_seconds / 60.0

    def _identify_skills_practiced(self, exercise_type: ExerciseType) -> List[str]:
        """Identificar habilidades que se practican"""
        skills_map = {
            ExerciseType.COMPRENSION_LECTORA: ["Comprensión", "Análisis", "Inferencia"],
            ExerciseType.GRAMATICA: ["Gramática", "Sintaxis", "Morfología"],
            ExerciseType.VOCABULARIO: ["Vocabulario", "Semántica", "Léxico"],
            ExerciseType.ORTOGRAFIA: ["Ortografía", "Escritura", "Normativa"],
            ExerciseType.SINONIMOS_ANTONIMOS: ["Vocabulario", "Semántica", "Relaciones léxicas"],
            ExerciseType.COMPLETAR_ORACIONES: ["Gramática", "Vocabulario", "Contexto"],
            ExerciseType.IDENTIFICAR_ERRORES: ["Revisión", "Corrección", "Normativa"],
            ExerciseType.ORDENAR_PALABRAS: ["Sintaxis", "Orden", "Estructura"]
        }

        return skills_map.get(exercise_type, ["Lengua española"])

    # =============================================================================
    # GENERADORES ESPECÍFICOS DE PREGUNTAS
    # =============================================================================

    def _generate_reading_comprehension(self, config: ExerciseGenerationConfig,
                                        text: str) -> List[ExerciseQuestion]:
        """Generar preguntas de comprensión lectora"""
        questions = []

        # Analizar texto si tenemos las herramientas
        words = text.lower().split()
        sentences = text.split('.')

        # Pregunta literal
        questions.append(ExerciseQuestion(
            question_text=f"¿Cuál es la idea principal del texto?",
            question_type=QuestionType.MULTIPLE_CHOICE,
            correct_answer="Opción basada en el contenido principal",
            options=[
                "Opción basada en el contenido principal",
                "Opción incorrecta 1",
                "Opción incorrecta 2",
                "Opción incorrecta 3"
            ],
            explanation="La idea principal se identifica analizando el tema central del texto.",
            difficulty_points=2,
            estimated_time=45.0
        ))

        # Pregunta de detalle
        if len(sentences) > 1:
            questions.append(ExerciseQuestion(
                question_text="¿Qué información específica menciona el texto?",
                question_type=QuestionType.TRUE_FALSE,
                correct_answer="Verdadero",
                explanation="Esta información se menciona explícitamente en el texto.",
                difficulty_points=1,
                estimated_time=30.0
            ))

        # Pregunta de inferencia
        questions.append(ExerciseQuestion(
            question_text="¿Qué se puede inferir del texto?",
            question_type=QuestionType.MULTIPLE_CHOICE,
            correct_answer="Inferencia lógica basada en el contenido",
            options=[
                "Inferencia lógica basada en el contenido",
                "Inferencia incorrecta 1",
                "Inferencia incorrecta 2",
                "Información no relacionada"
            ],
            explanation="Esta inferencia se basa en la información implícita del texto.",
            difficulty_points=3,
            estimated_time=60.0
        ))

        return questions

    def _generate_grammar_questions(self, config: ExerciseGenerationConfig,
                                    text: str) -> List[ExerciseQuestion]:
        """Generar preguntas de gramática"""
        questions = []

        # Usar patrones gramaticales predefinidos
        for category, patterns in self.grammar_patterns.items():
            pattern = random.choice(patterns)

            # Extraer la opción correcta
            correct_option = self._extract_correct_grammar_option(pattern)

            questions.append(ExerciseQuestion(
                question_text=f"Selecciona la opción correcta: {pattern}",
                question_type=QuestionType.MULTIPLE_CHOICE,
                correct_answer=correct_option,
                options=self._generate_grammar_options(pattern),
                explanation=f"Esta es una regla de {category.replace('_', ' ')}.",
                difficulty_points=2,
                estimated_time=40.0
            ))

        return questions

    def _generate_vocabulary_questions(self, config: ExerciseGenerationConfig,
                                       text: str) -> List[ExerciseQuestion]:
        """Generar preguntas de vocabulario"""
        questions = []

        # Obtener vocabulario del nivel
        vocab = self.vocabulary_by_level.get(config.target_level, {})

        for category, words in vocab.items():
            if words:
                word = random.choice(words)

                questions.append(ExerciseQuestion(
                    question_text=f"¿Qué tipo de palabra es '{word}'?",
                    question_type=QuestionType.MULTIPLE_CHOICE,
                    correct_answer=category.capitalize(),
                    options=[category.capitalize(), "Adverbio", "Preposición", "Conjunción"],
                    explanation=f"'{word}' es un {category[:-1]} porque {self._get_word_explanation(category)}.",
                    difficulty_points=1,
                    estimated_time=25.0
                ))

        return questions

    def _generate_spelling_questions(self, config: ExerciseGenerationConfig,
                                     text: str) -> List[ExerciseQuestion]:
        """Generar preguntas de ortografía"""
        questions = []

        for incorrect, correct in self.common_spelling_errors.items():
            questions.append(ExerciseQuestion(
                question_text=f"¿Cuál es la forma correcta?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                correct_answer=correct,
                options=[correct, incorrect, "Ambas son correctas", "Ninguna es correcta"],
                explanation=f"La forma correcta es '{correct}', no '{incorrect}'.",
                difficulty_points=2,
                estimated_time=30.0
            ))

        return questions

    def _generate_synonyms_antonyms(self, config: ExerciseGenerationConfig,
                                    text: str) -> List[ExerciseQuestion]:
        """Generar preguntas de sinónimos y antónimos"""
        questions = []

        for word, relations in self.synonyms_antonyms.items():
            # Pregunta de sinónimo
            synonym = random.choice(relations['sinónimos'])
            antonym = random.choice(relations['antónimos'])

            questions.append(ExerciseQuestion(
                question_text=f"¿Cuál es un sinónimo de '{word}'?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                correct_answer=synonym,
                options=[synonym, antonym, "palabra_inventada", "otra_palabra"],
                explanation=f"'{synonym}' es sinónimo de '{word}' porque tienen significado similar.",
                difficulty_points=2,
                estimated_time=35.0
            ))

            # Pregunta de antónimo
            questions.append(ExerciseQuestion(
                question_text=f"¿Cuál es un antónimo de '{word}'?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                correct_answer=antonym,
                options=[antonym, synonym, "palabra_inventada", "otra_palabra"],
                explanation=f"'{antonym}' es antónimo de '{word}' porque tienen significado opuesto.",
                difficulty_points=2,
                estimated_time=35.0
            ))

        return questions

    def _generate_fill_in_blank(self, config: ExerciseGenerationConfig,
                                text: str) -> List[ExerciseQuestion]:
        """Generar preguntas de completar oraciones"""
        questions = []

        # Crear oraciones con espacios en blanco
        sentences = [
            "El ____ es el animal más grande del océano.",
            "Mi hermana ____ estudiando medicina.",
            "Los niños ____ jugando en el parque."
        ]

        answers = ["ballena", "está", "están"]

        for sentence, answer in zip(sentences, answers):
            questions.append(ExerciseQuestion(
                question_text=f"Completa la oración: {sentence}",
                question_type=QuestionType.FILL_IN_BLANK,
                correct_answer=answer,
                explanation=f"La palabra correcta es '{answer}' por el contexto de la oración.",
                difficulty_points=2,
                estimated_time=40.0
            ))

        return questions

    def _generate_error_identification(self, config: ExerciseGenerationConfig,
                                       text: str) -> List[ExerciseQuestion]:
        """Generar preguntas de identificación de errores"""
        questions = []

        # Oraciones con errores intencionados
        error_sentences = [
            "Los niños a comprado dulces en la tienda.",
            "Mi mama cocina muy rica.",
            "El perro de Juan son muy travieso."
        ]

        corrections = [
            "han comprado",
            "mamá",
            "es"
        ]

        for sentence, correction in zip(error_sentences, corrections):
            questions.append(ExerciseQuestion(
                question_text=f"Identifica y corrige el error: '{sentence}'",
                question_type=QuestionType.SHORT_ANSWER,
                correct_answer=correction,
                explanation=f"El error está en '{correction}' por reglas gramaticales.",
                difficulty_points=3,
                estimated_time=50.0
            ))

        return questions

    def _generate_word_order(self, config: ExerciseGenerationConfig,
                             text: str) -> List[ExerciseQuestion]:
        """Generar preguntas de ordenar palabras"""
        questions = []

        # Oraciones desordenadas
        word_sets = [
            (["gusta", "Me", "leer", "libros"], "Me gusta leer libros"),
            (["perro", "El", "está", "corriendo"], "El perro está corriendo"),
            (["mañana", "Vamos", "al", "parque"], "Vamos al parque mañana")
        ]

        for words, correct_sentence in word_sets:
            shuffled_words = words.copy()
            random.shuffle(shuffled_words)

            questions.append(ExerciseQuestion(
                question_text=f"Ordena las palabras: {' | '.join(shuffled_words)}",
                question_type=QuestionType.DRAG_DROP,
                correct_answer=correct_sentence,
                explanation=f"El orden correcto sigue la estructura gramatical del español.",
                difficulty_points=2,
                estimated_time=45.0
            ))

        return questions

    # =============================================================================
    # MÉTODOS AUXILIARES
    # =============================================================================

    def _extract_correct_grammar_option(self, pattern: str) -> str:
        """Extraer la opción correcta de un patrón gramatical"""
        # Buscar opciones entre corchetes
        match = re.search(r'\[([^/]+)/[^\]]+\]', pattern)
        if match:
            return match.group(1)
        return "opción_correcta"

    def _generate_grammar_options(self, pattern: str) -> List[str]:
        """Generar opciones para pregunta gramatical"""
        # Extraer las opciones del patrón
        match = re.search(r'\[([^/]+)/([^\]]+)\]', pattern)
        if match:
            return [match.group(1), match.group(2), "opción_3", "opción_4"]
        return ["opción_1", "opción_2", "opción_3", "opción_4"]

    def _get_word_explanation(self, category: str) -> str:
        """Obtener explicación de categoría de palabra"""
        explanations = {
            'sustantivos': 'nombra a personas, animales, cosas o conceptos',
            'verbos': 'expresa acciones, estados o procesos',
            'adjetivos': 'describe o califica a los sustantivos'
        }
        return explanations.get(category, 'es una categoría gramatical')

    def _create_fallback_exercise(self, config: ExerciseGenerationConfig) -> Exercise:
        """Crear ejercicio básico en caso de error"""
        fallback_question = ExerciseQuestion(
            question_text="¿Cuál es la capital de España?",
            question_type=QuestionType.MULTIPLE_CHOICE,
            correct_answer="Madrid",
            options=["Madrid", "Barcelona", "Valencia", "Sevilla"],
            explanation="Madrid es la capital de España.",
            difficulty_points=1,
            estimated_time=30.0
        )

        return Exercise(
            title="Ejercicio de Prueba",
            description="Ejercicio básico generado automáticamente.",
            exercise_type=config.exercise_type,
            difficulty=config.difficulty,
            target_level=config.target_level,
            questions=[fallback_question],
            estimated_duration=0.5,
            total_points=1,
            skills_practiced=["Conocimiento general"],
            source_text=None
        )


# =============================================================================
# FUNCIONES DE UTILIDAD
# =============================================================================

def create_quick_exercise(exercise_type: ExerciseType,
                          difficulty: ExerciseDifficulty,
                          num_questions: int = 5) -> Exercise:
    """
    Crear ejercicio rápido con configuración mínima

    Args:
        exercise_type: Tipo de ejercicio
        difficulty: Nivel de dificultad
        num_questions: Número de preguntas

    Returns:
        Exercise: Ejercicio generado
    """
    # Mapear dificultad a nivel educativo
    difficulty_to_level = {
        ExerciseDifficulty.PRINCIPIANTE: EducationLevel.PRIMARIA_INICIAL,
        ExerciseDifficulty.BASICO: EducationLevel.PRIMARIA_MEDIA,
        ExerciseDifficulty.INTERMEDIO: EducationLevel.PRIMARIA_SUPERIOR,
        ExerciseDifficulty.AVANZADO: EducationLevel.SECUNDARIA,
        ExerciseDifficulty.EXPERTO: EducationLevel.UNIVERSITARIO
    }

    config = ExerciseGenerationConfig(
        exercise_type=exercise_type,
        difficulty=difficulty,
        target_level=difficulty_to_level.get(difficulty, EducationLevel.PRIMARIA_MEDIA),
        num_questions=num_questions,
        use_source_text=False,
        adapt_to_user_level=False
    )

    generator = ExerciseGenerator()
    return generator.generate_exercise(config)


def generate_adaptive_exercise(user_level: EducationLevel,
                               weak_skills: List[str],
                               preferred_types: List[ExerciseType] = None) -> Exercise:
    """
    Generar ejercicio adaptativo basado en el perfil del usuario

    Args:
        user_level: Nivel educativo del usuario
        weak_skills: Habilidades que necesita reforzar
        preferred_types: Tipos de ejercicio preferidos

    Returns:
        Exercise: Ejercicio adaptado al usuario
    """
    # Mapear habilidades débiles a tipos de ejercicio
    skills_to_types = {
        'gramática': ExerciseType.GRAMATICA,
        'vocabulario': ExerciseType.VOCABULARIO,
        'ortografía': ExerciseType.ORTOGRAFIA,
        'comprensión': ExerciseType.COMPRENSION_LECTORA,
        'sintaxis': ExerciseType.ORDENAR_PALABRAS
    }

    # Seleccionar tipo de ejercicio
    if preferred_types:
        exercise_type = random.choice(preferred_types)
    elif weak_skills:
        # Priorizar habilidades débiles
        skill_types = [skills_to_types.get(skill.lower()) for skill in weak_skills]
        skill_types = [t for t in skill_types if t is not None]
        exercise_type = random.choice(skill_types) if skill_types else ExerciseType.VOCABULARIO
    else:
        exercise_type = ExerciseType.VOCABULARIO

    # Mapear nivel educativo a dificultad
    level_to_difficulty = {
        EducationLevel.PRIMARIA_INICIAL: ExerciseDifficulty.PRINCIPIANTE,
        EducationLevel.PRIMARIA_MEDIA: ExerciseDifficulty.BASICO,
        EducationLevel.PRIMARIA_SUPERIOR: ExerciseDifficulty.INTERMEDIO,
        EducationLevel.SECUNDARIA: ExerciseDifficulty.AVANZADO,
        EducationLevel.UNIVERSITARIO: ExerciseDifficulty.EXPERTO
    }

    config = ExerciseGenerationConfig(
        exercise_type=exercise_type,
        difficulty=level_to_difficulty.get(user_level, ExerciseDifficulty.INTERMEDIO),
        target_level=user_level,
        num_questions=8,
        adapt_to_user_level=True
    )

    generator = ExerciseGenerator()
    return generator.generate_exercise(config)


def batch_generate_exercises(configs: List[ExerciseGenerationConfig]) -> List[Exercise]:
    """
    Generar múltiples ejercicios en lote

    Args:
        configs: Lista de configuraciones

    Returns:
        List[Exercise]: Lista de ejercicios generados
    """
    generator = ExerciseGenerator()
    exercises = []

    for i, config in enumerate(configs):
        print(f"📝 Generando ejercicio {i + 1}/{len(configs)}...")
        try:
            exercise = generator.generate_exercise(config)
            exercises.append(exercise)
        except Exception as e:
            print(f"⚠️ Error en ejercicio {i + 1}: {e}")
            # Continuar con el siguiente

    print(f"✅ Generados {len(exercises)} ejercicios de {len(configs)} solicitados")
    return exercises


def analyze_exercise_difficulty(exercise: Exercise) -> Dict[str, Any]:
    """
    Analizar la dificultad real de un ejercicio generado

    Args:
        exercise: Ejercicio a analizar

    Returns:
        Dict con análisis de dificultad
    """
    # Calcular métricas básicas
    avg_time_per_question = exercise.estimated_duration / len(exercise.questions) * 60
    points_distribution = [q.difficulty_points for q in exercise.questions]

    # Clasificar tipos de preguntas
    question_types = Counter(q.question_type for q in exercise.questions)

    # Calcular índice de dificultad
    difficulty_index = (
                               exercise.total_points / len(exercise.questions) +
                               avg_time_per_question / 30 +
                               len(question_types) / 5
                       ) / 3

    return {
        'exercise_title': exercise.title,
        'total_questions': len(exercise.questions),
        'total_points': exercise.total_points,
        'estimated_duration_minutes': round(exercise.estimated_duration, 1),
        'avg_time_per_question_seconds': round(avg_time_per_question, 1),
        'difficulty_index': round(difficulty_index, 2),
        'question_types_distribution': dict(question_types),
        'points_range': f"{min(points_distribution)}-{max(points_distribution)}",
        'skills_practiced': exercise.skills_practiced,
        'has_source_text': exercise.source_text is not None
    }


# =============================================================================
# CÓDIGO DE PRUEBA
# =============================================================================

if __name__ == "__main__":
    print("🧪 Probando generador de ejercicios...")

    # Configuraciones de prueba
    test_configs = [
        ExerciseGenerationConfig(
            exercise_type=ExerciseType.COMPRENSION_LECTORA,
            difficulty=ExerciseDifficulty.BASICO,
            target_level=EducationLevel.PRIMARIA_MEDIA,
            num_questions=3
        ),
        ExerciseGenerationConfig(
            exercise_type=ExerciseType.GRAMATICA,
            difficulty=ExerciseDifficulty.INTERMEDIO,
            target_level=EducationLevel.PRIMARIA_SUPERIOR,
            num_questions=4
        ),
        ExerciseGenerationConfig(
            exercise_type=ExerciseType.VOCABULARIO,
            difficulty=ExerciseDifficulty.PRINCIPIANTE,
            target_level=EducationLevel.PRIMARIA_INICIAL,
            num_questions=5
        )
    ]

    generator = ExerciseGenerator()

    print("\n🎯 GENERACIÓN DE EJERCICIOS DE PRUEBA:")
    print("=" * 60)

    for i, config in enumerate(test_configs, 1):
        print(f"\n📚 EJERCICIO {i}:")
        print(f"Tipo: {config.exercise_type.value}")
        print(f"Dificultad: {config.difficulty.value}")
        print(f"Nivel: {config.target_level.value}")

        try:
            # Generar ejercicio
            exercise = generator.generate_exercise(config)

            print(f"\n✅ EJERCICIO GENERADO:")
            print(f"📖 Título: {exercise.title}")
            print(f"📝 Descripción: {exercise.description}")
            print(f"⏱️ Duración estimada: {exercise.estimated_duration:.1f} minutos")
            print(f"🎯 Puntos totales: {exercise.total_points}")
            print(f"🧠 Habilidades: {', '.join(exercise.skills_practiced)}")
            print(f"❓ Preguntas: {len(exercise.questions)}")

            # Mostrar primera pregunta como ejemplo
            if exercise.questions:
                q = exercise.questions[0]
                print(f"\n📋 PREGUNTA DE EJEMPLO:")
                print(f"❓ {q.question_text}")
                print(f"🎯 Tipo: {q.question_type.value}")
                print(f"✅ Respuesta: {q.correct_answer}")
                if q.options:
                    print(f"📊 Opciones: {', '.join(q.options)}")
                if q.explanation:
                    print(f"💡 Explicación: {q.explanation}")
                print(f"⏱️ Tiempo estimado: {q.estimated_time} segundos")
                print(f"🎯 Puntos: {q.difficulty_points}")

            # Análisis de dificultad
            analysis = analyze_exercise_difficulty(exercise)
            print(f"\n📊 ANÁLISIS DE DIFICULTAD:")
            print(f"Índice de dificultad: {analysis['difficulty_index']}")
            print(f"Tiempo promedio por pregunta: {analysis['avg_time_per_question_seconds']}s")
            print(f"Distribución de tipos: {analysis['question_types_distribution']}")

        except Exception as e:
            print(f"❌ Error generando ejercicio: {e}")
            import traceback

            traceback.print_exc()

        print("-" * 60)

    # Prueba de función rápida
    print(f"\n⚡ PRUEBA DE EJERCICIO RÁPIDO:")
    try:
        quick_exercise = create_quick_exercise(
            ExerciseType.SINONIMOS_ANTONIMOS,
            ExerciseDifficulty.BASICO,
            3
        )
        print(f"✅ Ejercicio rápido: {quick_exercise.title}")
        print(f"📝 {len(quick_exercise.questions)} preguntas generadas")
    except Exception as e:
        print(f"❌ Error en ejercicio rápido: {e}")

    # Prueba de ejercicio adaptativo
    print(f"\n🎯 PRUEBA DE EJERCICIO ADAPTATIVO:")
    try:
        adaptive_exercise = generate_adaptive_exercise(
            user_level=EducationLevel.PRIMARIA_SUPERIOR,
            weak_skills=['gramática', 'vocabulario'],
            preferred_types=[ExerciseType.GRAMATICA, ExerciseType.VOCABULARIO]
        )
        print(f"✅ Ejercicio adaptativo: {adaptive_exercise.title}")
        print(f"🎯 Enfocado en: {', '.join(adaptive_exercise.skills_practiced)}")
    except Exception as e:
        print(f"❌ Error en ejercicio adaptativo: {e}")

    print(f"\n✅ Pruebas del generador de ejercicios completadas!")
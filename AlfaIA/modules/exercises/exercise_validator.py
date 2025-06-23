# =============================================================================
# AlfaIA/modules/exercises/exercise_validator.py - Validador de Respuestas de Ejercicios
# =============================================================================

import re
import difflib
import logging
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass
from enum import Enum
import sys
from pathlib import Path
from datetime import datetime

# Agregar el directorio raíz al path para imports
sys.path.append(str(Path(__file__).parent.parent.parent))

# Imports de módulos de ejercicios
try:
    from modules.exercises.exercise_generator import (
        Exercise, ExerciseQuestion, QuestionType, ExerciseType, ExerciseDifficulty
    )

    EXERCISE_MODULES_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Módulos de ejercicios no disponibles: {e}")
    EXERCISE_MODULES_AVAILABLE = False


    # Definir clases básicas si no están disponibles
    class QuestionType(Enum):
        MULTIPLE_CHOICE = "multiple_choice"
        TRUE_FALSE = "true_false"
        FILL_IN_BLANK = "fill_in_blank"
        SHORT_ANSWER = "short_answer"
        DRAG_DROP = "drag_drop"
        MATCHING = "matching"

# Imports de módulos NLP para validación avanzada
try:
    from modules.nlp.text_analyzer import TextAnalyzer
    from modules.nlp.grammar_checker import GrammarChecker

    NLP_VALIDATION_AVAILABLE = True
except ImportError:
    print("⚠️ Módulos NLP no disponibles para validación avanzada")
    NLP_VALIDATION_AVAILABLE = False

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print("🔧 Inicializando validador de ejercicios...")


# =============================================================================
# ENUMS Y DATACLASSES
# =============================================================================

class ValidationResult(Enum):
    """Resultados de validación"""
    CORRECT = "correct"
    INCORRECT = "incorrect"
    PARTIALLY_CORRECT = "partially_correct"
    INVALID_FORMAT = "invalid_format"
    TIMEOUT = "timeout"


class FeedbackType(Enum):
    """Tipos de retroalimentación"""
    POSITIVE = "positive"
    CORRECTIVE = "corrective"
    HINT = "hint"
    ENCOURAGEMENT = "encouragement"
    EXPLANATION = "explanation"


@dataclass
class QuestionResponse:
    """Respuesta del usuario a una pregunta"""
    question_id: str
    user_answer: Union[str, List[str]]
    time_taken: float  # segundos
    attempts: int = 1
    hints_used: int = 0
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class ValidationFeedback:
    """Retroalimentación de validación"""
    is_correct: bool
    score: float  # 0.0 - 1.0
    feedback_message: str
    feedback_type: FeedbackType
    detailed_explanation: Optional[str] = None
    suggestions: List[str] = None
    correct_answer: Optional[str] = None
    similarity_score: Optional[float] = None  # Para respuestas textuales

    def __post_init__(self):
        if self.suggestions is None:
            self.suggestions = []


@dataclass
class QuestionValidationResult:
    """Resultado de validación de una pregunta"""
    question_id: str
    result: ValidationResult
    feedback: ValidationFeedback
    points_earned: float
    max_points: float
    processing_time: float

    # Métricas adicionales
    accuracy: float  # 0.0 - 1.0
    confidence: float  # 0.0 - 1.0 (confianza en la validación)
    difficulty_adjustment: float  # -1.0 a 1.0 (ajuste sugerido de dificultad)


@dataclass
class ExerciseValidationResult:
    """Resultado de validación completo del ejercicio"""
    exercise_id: str
    question_results: List[QuestionValidationResult]

    # Métricas generales
    total_score: float
    max_possible_score: float
    percentage_score: float
    total_time: float

    # Análisis de rendimiento
    strengths: List[str]
    weaknesses: List[str]
    recommendations: List[str]

    # Adaptación para futuros ejercicios
    suggested_difficulty: ExerciseDifficulty
    suggested_focus_areas: List[str]

    # Metadatos
    validation_timestamp: datetime
    confidence_score: float


# =============================================================================
# CLASE PRINCIPAL DE VALIDACIÓN
# =============================================================================

class ExerciseValidator:
    """
    Validador inteligente de respuestas de ejercicios para AlfaIA
    """

    def __init__(self):
        """Inicializar validador"""
        self.logger = logger

        # Inicializar módulos NLP si están disponibles
        if NLP_VALIDATION_AVAILABLE:
            self.text_analyzer = TextAnalyzer()
            self.grammar_checker = GrammarChecker()
        else:
            self.text_analyzer = None
            self.grammar_checker = None

        # Configurar validadores específicos
        self._setup_validation_methods()

        # Cargar bases de datos de validación
        self._load_validation_databases()

        print("✅ ExerciseValidator inicializado")

    def _setup_validation_methods(self):
        """Configurar métodos de validación por tipo de pregunta"""
        self.validation_methods = {
            QuestionType.MULTIPLE_CHOICE: self._validate_multiple_choice,
            QuestionType.TRUE_FALSE: self._validate_true_false,
            QuestionType.FILL_IN_BLANK: self._validate_fill_in_blank,
            QuestionType.SHORT_ANSWER: self._validate_short_answer,
            QuestionType.DRAG_DROP: self._validate_drag_drop,
            QuestionType.MATCHING: self._validate_matching
        }

    def _load_validation_databases(self):
        """Cargar bases de datos para validación"""

        # Sinónimos para respuestas flexibles
        self.answer_synonyms = {
            'sí': ['si', 'yes', 'correcto', 'verdadero', 'cierto', 'afirmativo'],
            'no': ['nope', 'incorrecto', 'falso', 'negativo', 'erróneo'],
            'grande': ['enorme', 'gigante', 'inmenso', 'colosal', 'vasto'],
            'pequeño': ['diminuto', 'minúsculo', 'chico', 'tiny', 'reducido'],
            'rápido': ['veloz', 'acelerado', 'ligero', 'presto', 'ágil'],
            'lento': ['pausado', 'moroso', 'tardo', 'despacio']
        }

        # Patrones de respuestas comunes
        self.common_patterns = {
            'affirmative': r'^(sí|si|yes|correcto|verdadero|cierto|v)$',
            'negative': r'^(no|nope|incorrecto|falso|f)$',
            'number': r'^\d+(\.\d+)?$',
            'word': r'^[a-zA-ZáéíóúüñÁÉÍÓÚÜÑ]+$',
            'sentence': r'^[A-ZÁÉÍÓÚÜÑ][^.!?]*[.!?]$'
        }

        # Errores comunes y sus correcciones
        self.common_errors = {
            'mas': 'más',
            'tu': 'tú',
            'el': 'él',
            'si': 'sí',
            'haber': 'a ver',
            'echo': 'hecho',
            'asta': 'hasta'
        }

        # Umbrales de similitud para diferentes tipos de validación
        self.similarity_thresholds = {
            'exact': 1.0,
            'high': 0.9,
            'medium': 0.7,
            'low': 0.5
        }

    def validate_exercise(self, exercise: 'Exercise',
                          responses: List[QuestionResponse]) -> ExerciseValidationResult:
        """
        Validar ejercicio completo

        Args:
            exercise: Ejercicio a validar
            responses: Respuestas del usuario

        Returns:
            ExerciseValidationResult: Resultado completo de validación
        """
        import time
        start_time = time.time()

        try:
            print(f"🔍 Validando ejercicio: {exercise.title}")
            print(f"📝 {len(responses)} respuestas recibidas")

            # Validar cada pregunta individualmente
            question_results = []
            total_time = 0.0

            for i, response in enumerate(responses):
                if i < len(exercise.questions):
                    question = exercise.questions[i]
                    print(f"📋 Validando pregunta {i + 1}/{len(responses)}")

                    result = self.validate_question(question, response)
                    question_results.append(result)
                    total_time += response.time_taken
                else:
                    print(f"⚠️ Respuesta extra ignorada: {i + 1}")

            # Calcular métricas generales
            total_score = sum(r.points_earned for r in question_results)
            max_possible_score = sum(r.max_points for r in question_results)
            percentage_score = (total_score / max_possible_score * 100) if max_possible_score > 0 else 0

            # Analizar rendimiento
            strengths, weaknesses = self._analyze_performance(question_results, exercise)
            recommendations = self._generate_recommendations(question_results, exercise)

            # Sugerir ajustes para futuros ejercicios
            suggested_difficulty = self._suggest_difficulty_adjustment(question_results, exercise)
            suggested_focus_areas = self._identify_focus_areas(question_results, exercise)

            # Calcular confianza en la validación
            confidence_score = self._calculate_validation_confidence(question_results)

            processing_time = time.time() - start_time

            result = ExerciseValidationResult(
                exercise_id=f"exercise_{int(time.time())}",
                question_results=question_results,
                total_score=total_score,
                max_possible_score=max_possible_score,
                percentage_score=percentage_score,
                total_time=total_time,
                strengths=strengths,
                weaknesses=weaknesses,
                recommendations=recommendations,
                suggested_difficulty=suggested_difficulty,
                suggested_focus_areas=suggested_focus_areas,
                validation_timestamp=datetime.now(),
                confidence_score=confidence_score
            )

            print(f"✅ Validación completada en {processing_time:.2f}s")
            print(f"📊 Puntuación: {total_score:.1f}/{max_possible_score} ({percentage_score:.1f}%)")

            return result

        except Exception as e:
            error_msg = f"Error validando ejercicio: {str(e)}"
            self.logger.error(error_msg)
            return self._create_fallback_validation_result(exercise, responses)

    def validate_question(self, question: 'ExerciseQuestion',
                          response: QuestionResponse) -> QuestionValidationResult:
        """
        Validar una pregunta individual

        Args:
            question: Pregunta del ejercicio
            response: Respuesta del usuario

        Returns:
            QuestionValidationResult: Resultado de validación
        """
        import time
        start_time = time.time()

        try:
            # Seleccionar método de validación apropiado
            validator = self.validation_methods.get(question.question_type)
            if not validator:
                raise ValueError(f"Validador no disponible para {question.question_type.value}")

            # Ejecutar validación específica
            validation_result, feedback = validator(question, response)

            # Calcular puntos ganados
            points_earned = self._calculate_points_earned(
                validation_result, feedback.score, question.difficulty_points, response.attempts
            )

            # Calcular métricas adicionales
            accuracy = feedback.score
            confidence = self._calculate_question_confidence(question, response, feedback)
            difficulty_adjustment = self._calculate_difficulty_adjustment(response, feedback)

            processing_time = time.time() - start_time

            return QuestionValidationResult(
                question_id=f"q_{hash(question.question_text) % 10000}",
                result=validation_result,
                feedback=feedback,
                points_earned=points_earned,
                max_points=question.difficulty_points,
                processing_time=processing_time,
                accuracy=accuracy,
                confidence=confidence,
                difficulty_adjustment=difficulty_adjustment
            )

        except Exception as e:
            self.logger.error(f"Error validando pregunta: {e}")
            return self._create_fallback_question_result(question, response)

    # =============================================================================
    # VALIDADORES ESPECÍFICOS POR TIPO DE PREGUNTA
    # =============================================================================

    def _validate_multiple_choice(self, question: 'ExerciseQuestion',
                                  response: QuestionResponse) -> Tuple[ValidationResult, ValidationFeedback]:
        """Validar pregunta de opción múltiple"""
        user_answer = str(response.user_answer).strip()
        correct_answer = str(question.correct_answer).strip()

        # Validación exacta
        is_correct = user_answer.lower() == correct_answer.lower()

        if is_correct:
            feedback = ValidationFeedback(
                is_correct=True,
                score=1.0,
                feedback_message="¡Correcto! Excelente trabajo.",
                feedback_type=FeedbackType.POSITIVE,
                detailed_explanation=question.explanation
            )
            return ValidationResult.CORRECT, feedback
        else:
            feedback = ValidationFeedback(
                is_correct=False,
                score=0.0,
                feedback_message="Respuesta incorrecta. Revisa las opciones nuevamente.",
                feedback_type=FeedbackType.CORRECTIVE,
                detailed_explanation=question.explanation,
                correct_answer=correct_answer,
                suggestions=["Lee cuidadosamente todas las opciones", "Busca pistas en la pregunta"]
            )
            return ValidationResult.INCORRECT, feedback

    def _validate_true_false(self, question: 'ExerciseQuestion',
                             response: QuestionResponse) -> Tuple[ValidationResult, ValidationFeedback]:
        """Validar pregunta verdadero/falso"""
        user_answer = str(response.user_answer).strip().lower()
        correct_answer = str(question.correct_answer).strip().lower()

        # Normalizar respuestas
        user_normalized = self._normalize_boolean_answer(user_answer)
        correct_normalized = self._normalize_boolean_answer(correct_answer)

        is_correct = user_normalized == correct_normalized

        if is_correct:
            feedback = ValidationFeedback(
                is_correct=True,
                score=1.0,
                feedback_message="¡Correcto!",
                feedback_type=FeedbackType.POSITIVE,
                detailed_explanation=question.explanation
            )
            return ValidationResult.CORRECT, feedback
        else:
            feedback = ValidationFeedback(
                is_correct=False,
                score=0.0,
                feedback_message=f"Incorrecto. La respuesta correcta es: {correct_answer}",
                feedback_type=FeedbackType.CORRECTIVE,
                detailed_explanation=question.explanation,
                correct_answer=correct_answer
            )
            return ValidationResult.INCORRECT, feedback

    def _validate_fill_in_blank(self, question: 'ExerciseQuestion',
                                response: QuestionResponse) -> Tuple[ValidationResult, ValidationFeedback]:
        """Validar pregunta de llenar espacios en blanco"""
        user_answer = str(response.user_answer).strip()
        correct_answer = str(question.correct_answer).strip()

        # Calcular similitud
        similarity = self._calculate_text_similarity(user_answer, correct_answer)

        # Verificar sinónimos
        synonym_match = self._check_synonym_match(user_answer, correct_answer)

        if similarity >= self.similarity_thresholds['exact'] or synonym_match:
            feedback = ValidationFeedback(
                is_correct=True,
                score=1.0,
                feedback_message="¡Perfecto!",
                feedback_type=FeedbackType.POSITIVE,
                detailed_explanation=question.explanation,
                similarity_score=similarity
            )
            return ValidationResult.CORRECT, feedback

        elif similarity >= self.similarity_thresholds['high']:
            feedback = ValidationFeedback(
                is_correct=True,
                score=0.8,
                feedback_message="Muy bien, respuesta casi exacta.",
                feedback_type=FeedbackType.POSITIVE,
                detailed_explanation=question.explanation,
                similarity_score=similarity
            )
            return ValidationResult.PARTIALLY_CORRECT, feedback

        elif similarity >= self.similarity_thresholds['medium']:
            feedback = ValidationFeedback(
                is_correct=False,
                score=0.5,
                feedback_message="Te acercas, pero revisa tu respuesta.",
                feedback_type=FeedbackType.HINT,
                correct_answer=correct_answer,
                similarity_score=similarity,
                suggestions=["Verifica la ortografía", "Considera sinónimos"]
            )
            return ValidationResult.PARTIALLY_CORRECT, feedback

        else:
            feedback = ValidationFeedback(
                is_correct=False,
                score=0.0,
                feedback_message="Respuesta incorrecta.",
                feedback_type=FeedbackType.CORRECTIVE,
                detailed_explanation=question.explanation,
                correct_answer=correct_answer,
                similarity_score=similarity
            )
            return ValidationResult.INCORRECT, feedback

    def _validate_short_answer(self, question: 'ExerciseQuestion',
                               response: QuestionResponse) -> Tuple[ValidationResult, ValidationFeedback]:
        """Validar respuesta corta"""
        user_answer = str(response.user_answer).strip()
        correct_answer = str(question.correct_answer).strip()

        # Usar análisis NLP si está disponible
        if self.text_analyzer and len(user_answer) > 10:
            return self._validate_short_answer_nlp(question, response)
        else:
            return self._validate_short_answer_basic(question, response)

    def _validate_short_answer_nlp(self, question: 'ExerciseQuestion',
                                   response: QuestionResponse) -> Tuple[ValidationResult, ValidationFeedback]:
        """Validar respuesta corta usando NLP"""
        user_answer = str(response.user_answer).strip()
        correct_answer = str(question.correct_answer).strip()

        # Analizar ambas respuestas
        user_analysis = self.text_analyzer.analyze_text(user_answer)
        correct_analysis = self.text_analyzer.analyze_text(correct_answer)

        # Comparar conceptos clave (simplificado)
        user_words = set(word.lower() for word in user_analysis.stats.word_count if len(word) > 3)
        correct_words = set(word.lower() for word in correct_analysis.stats.word_count if len(word) > 3)

        overlap = len(user_words.intersection(correct_words))
        total_concepts = len(correct_words)
        concept_score = overlap / max(total_concepts, 1)

        # Verificar gramática si está disponible
        grammar_score = 1.0
        if self.grammar_checker:
            grammar_result = self.grammar_checker.check_text(user_answer)
            grammar_score = max(0.5, 1.0 - len(grammar_result.errors) * 0.1)

        # Puntuación combinada
        final_score = (concept_score * 0.7) + (grammar_score * 0.3)

        if final_score >= 0.8:
            feedback = ValidationFeedback(
                is_correct=True,
                score=final_score,
                feedback_message="Excelente respuesta con buena comprensión.",
                feedback_type=FeedbackType.POSITIVE,
                detailed_explanation=question.explanation
            )
            return ValidationResult.CORRECT, feedback
        elif final_score >= 0.6:
            feedback = ValidationFeedback(
                is_correct=True,
                score=final_score,
                feedback_message="Buena respuesta, aunque puede mejorarse.",
                feedback_type=FeedbackType.POSITIVE,
                suggestions=["Incluye más detalles específicos", "Revisa la gramática"]
            )
            return ValidationResult.PARTIALLY_CORRECT, feedback
        else:
            feedback = ValidationFeedback(
                is_correct=False,
                score=final_score,
                feedback_message="La respuesta necesita más desarrollo.",
                feedback_type=FeedbackType.CORRECTIVE,
                detailed_explanation=question.explanation,
                suggestions=["Incluye conceptos clave", "Desarrolla más tu idea"]
            )
            return ValidationResult.INCORRECT, feedback

    def _validate_short_answer_basic(self, question: 'ExerciseQuestion',
                                     response: QuestionResponse) -> Tuple[ValidationResult, ValidationFeedback]:
        """Validar respuesta corta básica"""
        user_answer = str(response.user_answer).strip()
        correct_answer = str(question.correct_answer).strip()

        # Similitud textual básica
        similarity = self._calculate_text_similarity(user_answer, correct_answer)

        if similarity >= 0.8:
            feedback = ValidationFeedback(
                is_correct=True,
                score=similarity,
                feedback_message="¡Correcto!",
                feedback_type=FeedbackType.POSITIVE,
                similarity_score=similarity
            )
            return ValidationResult.CORRECT, feedback
        elif similarity >= 0.5:
            feedback = ValidationFeedback(
                is_correct=True,
                score=similarity,
                feedback_message="Respuesta parcialmente correcta.",
                feedback_type=FeedbackType.HINT,
                similarity_score=similarity
            )
            return ValidationResult.PARTIALLY_CORRECT, feedback
        else:
            feedback = ValidationFeedback(
                is_correct=False,
                score=similarity,
                feedback_message="Respuesta incorrecta.",
                feedback_type=FeedbackType.CORRECTIVE,
                correct_answer=correct_answer,
                similarity_score=similarity
            )
            return ValidationResult.INCORRECT, feedback

    def _validate_drag_drop(self, question: 'ExerciseQuestion',
                            response: QuestionResponse) -> Tuple[ValidationResult, ValidationFeedback]:
        """Validar pregunta de arrastrar y soltar"""
        user_order = response.user_answer
        correct_order = question.correct_answer

        if isinstance(user_order, str):
            user_order = user_order.split()
        if isinstance(correct_order, str):
            correct_order = correct_order.split()

        # Comparar secuencias
        if user_order == correct_order:
            feedback = ValidationFeedback(
                is_correct=True,
                score=1.0,
                feedback_message="¡Perfecto! Orden correcto.",
                feedback_type=FeedbackType.POSITIVE
            )
            return ValidationResult.CORRECT, feedback
        else:
            # Calcular similitud de orden
            matches = sum(1 for i, (u, c) in enumerate(zip(user_order, correct_order)) if u == c)
            similarity = matches / max(len(correct_order), 1)

            if similarity >= 0.7:
                feedback = ValidationFeedback(
                    is_correct=True,
                    score=similarity,
                    feedback_message="Casi correcto, solo algunos elementos fuera de lugar.",
                    feedback_type=FeedbackType.HINT
                )
                return ValidationResult.PARTIALLY_CORRECT, feedback
            else:
                feedback = ValidationFeedback(
                    is_correct=False,
                    score=similarity,
                    feedback_message="Orden incorrecto. Intenta nuevamente.",
                    feedback_type=FeedbackType.CORRECTIVE,
                    correct_answer=" ".join(correct_order)
                )
                return ValidationResult.INCORRECT, feedback

    def _validate_matching(self, question: 'ExerciseQuestion',
                           response: QuestionResponse) -> Tuple[ValidationResult, ValidationFeedback]:
        """Validar pregunta de emparejar"""
        # Simplificado - asumir que la respuesta es un diccionario o lista de pares
        user_matches = response.user_answer
        correct_matches = question.correct_answer

        # Convertir a formato estándar si es necesario
        if isinstance(user_matches, str):
            # Formato simple: "A-1,B-2,C-3"
            user_pairs = [pair.split('-') for pair in user_matches.split(',')]
            user_dict = {pair[0]: pair[1] for pair in user_pairs if len(pair) == 2}
        else:
            user_dict = user_matches

        if isinstance(correct_matches, str):
            correct_pairs = [pair.split('-') for pair in correct_matches.split(',')]
            correct_dict = {pair[0]: pair[1] for pair in correct_pairs if len(pair) == 2}
        else:
            correct_dict = correct_matches

        # Calcular coincidencias
        total_pairs = len(correct_dict)
        correct_pairs_count = sum(1 for k, v in user_dict.items() if correct_dict.get(k) == v)
        score = correct_pairs_count / max(total_pairs, 1)

        if score == 1.0:
            feedback = ValidationFeedback(
                is_correct=True,
                score=1.0,
                feedback_message="¡Perfecto! Todos los emparejamientos son correctos.",
                feedback_type=FeedbackType.POSITIVE
            )
            return ValidationResult.CORRECT, feedback
        elif score >= 0.7:
            feedback = ValidationFeedback(
                is_correct=True,
                score=score,
                feedback_message=f"Muy bien, {correct_pairs_count} de {total_pairs} emparejamientos correctos.",
                feedback_type=FeedbackType.POSITIVE
            )
            return ValidationResult.PARTIALLY_CORRECT, feedback
        else:
            feedback = ValidationFeedback(
                is_correct=False,
                score=score,
                feedback_message=f"Solo {correct_pairs_count} de {total_pairs} emparejamientos correctos.",
                feedback_type=FeedbackType.CORRECTIVE
            )
            return ValidationResult.INCORRECT, feedback

    # =============================================================================
    # MÉTODOS AUXILIARES
    # =============================================================================

    def _normalize_boolean_answer(self, answer: str) -> str:
        """Normalizar respuesta booleana"""
        answer = answer.lower().strip()

        if re.match(self.common_patterns['affirmative'], answer):
            return 'true'
        elif re.match(self.common_patterns['negative'], answer):
            return 'false'
        else:
            return answer

    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calcular similitud entre dos textos"""
        # Normalizar textos
        text1 = self._normalize_text(text1)
        text2 = self._normalize_text(text2)

        # Usar difflib para similitud de secuencias
        matcher = difflib.SequenceMatcher(None, text1, text2)
        return matcher.ratio()

    def _normalize_text(self, text: str) -> str:
        """Normalizar texto para comparación"""
        # Convertir a minúsculas
        text = text.lower()

        # Eliminar acentos básicos
        replacements = {'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u', 'ñ': 'n'}
        for accented, plain in replacements.items():
            text = text.replace(accented, plain)

        # Eliminar puntuación extra
        text = re.sub(r'[^\w\s]', '', text)

        # Normalizar espacios
        text = re.sub(r'\s+', ' ', text).strip()

        return text

    def _check_synonym_match(self, user_answer: str, correct_answer: str) -> bool:
        """Verificar si hay coincidencia de sinónimos"""
        user_normalized = self._normalize_text(user_answer)
        correct_normalized = self._normalize_text(correct_answer)

        # Buscar en base de sinónimos
        for word, synonyms in self.answer_synonyms.items():
            if correct_normalized == word:
                return user_normalized in synonyms
            elif user_normalized == word:
                return correct_normalized in synonyms

        return False

    def _calculate_points_earned(self, result: ValidationResult, score: float,
                                 max_points: int, attempts: int) -> float:
        """Calcular puntos ganados considerando intentos"""
        base_points = score * max_points

        # Penalización por intentos múltiples
        attempt_penalty = max(0.1, 1.0 - (attempts - 1) * 0.2)

        return base_points * attempt_penalty

    def _calculate_question_confidence(self, question: 'ExerciseQuestion',
                                       response: QuestionResponse,
                                       feedback: ValidationFeedback) -> float:
        """Calcular confianza en la validación de la pregunta"""
        confidence = 1.0

        # Reducir confianza para respuestas textuales
        if question.question_type in [QuestionType.SHORT_ANSWER, QuestionType.FILL_IN_BLANK]:
            confidence *= 0.8

        # Reducir confianza si no hay análisis NLP disponible
        if not NLP_VALIDATION_AVAILABLE and question.question_type == QuestionType.SHORT_ANSWER:
            confidence *= 0.6

        # Ajustar por similitud en respuestas textuales
        if hasattr(feedback, 'similarity_score') and feedback.similarity_score is not None:
            if feedback.similarity_score < 0.9:
                confidence *= 0.9

        # Ajustar por tiempo de respuesta (muy rápido o muy lento reduce confianza)
        if response.time_taken < 5:  # Muy rápido, posible adivinanza
            confidence *= 0.8
        elif response.time_taken > 300:  # Muy lento, posible ayuda externa
            confidence *= 0.9

        return max(0.1, confidence)

    def _calculate_difficulty_adjustment(self, response: QuestionResponse,
                                         feedback: ValidationFeedback) -> float:
        """Calcular ajuste de dificultad sugerido (-1.0 a 1.0)"""
        adjustment = 0.0

        # Si fue muy fácil (respuesta rápida y correcta)
        if feedback.is_correct and response.time_taken < 15:
            adjustment = 0.3  # Sugerir aumentar dificultad

        # Si fue muy difícil (respuesta lenta e incorrecta)
        elif not feedback.is_correct and response.time_taken > 120:
            adjustment = -0.3  # Sugerir reducir dificultad

        # Ajustar por intentos múltiples
        if response.attempts > 2:
            adjustment -= 0.2

        # Ajustar por uso de pistas
        if response.hints_used > 1:
            adjustment -= 0.1

        return max(-1.0, min(1.0, adjustment))

    def _analyze_performance(self, question_results: List[QuestionValidationResult],
                             exercise: 'Exercise') -> Tuple[List[str], List[str]]:
        """Analizar fortalezas y debilidades del rendimiento"""
        strengths = []
        weaknesses = []

        # Analizar por tipo de pregunta
        correct_by_type = {}
        total_by_type = {}

        for result in question_results:
            # Obtener tipo de pregunta (simplificado)
            question_type = "general"  # Placeholder

            if question_type not in correct_by_type:
                correct_by_type[question_type] = 0
                total_by_type[question_type] = 0

            total_by_type[question_type] += 1
            if result.result == ValidationResult.CORRECT:
                correct_by_type[question_type] += 1

        # Identificar fortalezas (>75% correcto)
        for q_type, correct in correct_by_type.items():
            total = total_by_type[q_type]
            if correct / total >= 0.75:
                strengths.append(f"Excelente rendimiento en {q_type}")

        # Identificar debilidades (<50% correcto)
        for q_type, correct in correct_by_type.items():
            total = total_by_type[q_type]
            if correct / total < 0.5:
                weaknesses.append(f"Necesita mejorar en {q_type}")

        # Analizar tiempo de respuesta
        avg_time = sum(r.processing_time for r in question_results) / len(question_results)
        if avg_time < 20:
            strengths.append("Respuestas rápidas y eficientes")
        elif avg_time > 90:
            weaknesses.append("Toma mucho tiempo en responder")

        # Analizar consistencia
        scores = [r.accuracy for r in question_results]
        if len(scores) > 1:
            score_variance = sum((s - sum(scores) / len(scores)) ** 2 for s in scores) / len(scores)
            if score_variance < 0.1:
                strengths.append("Rendimiento consistente")
            else:
                weaknesses.append("Rendimiento inconsistente")

        return strengths, weaknesses

    def _generate_recommendations(self, question_results: List[QuestionValidationResult],
                                  exercise: 'Exercise') -> List[str]:
        """Generar recomendaciones personalizadas"""
        recommendations = []

        # Calcular estadísticas generales
        total_score = sum(r.points_earned for r in question_results)
        max_score = sum(r.max_points for r in question_results)
        percentage = (total_score / max_score * 100) if max_score > 0 else 0

        # Recomendaciones por nivel de rendimiento
        if percentage >= 90:
            recommendations.append("🌟 ¡Excelente trabajo! Considera ejercicios más desafiantes")
            recommendations.append("📈 Puedes avanzar al siguiente nivel de dificultad")
        elif percentage >= 70:
            recommendations.append("👍 Buen trabajo. Repasa las áreas donde tuviste errores")
            recommendations.append("🔄 Practica ejercicios similares para reforzar el aprendizaje")
        elif percentage >= 50:
            recommendations.append("📚 Necesitas más práctica en estos temas")
            recommendations.append("💡 Considera revisar el material de estudio")
            recommendations.append("🎯 Enfócate en ejercicios de nivel básico")
        else:
            recommendations.append("🔄 Repasa los conceptos fundamentales")
            recommendations.append("👨‍🏫 Considera buscar ayuda adicional")
            recommendations.append("📖 Dedica más tiempo al estudio de la teoría")

        # Recomendaciones específicas por errores comunes
        incorrect_results = [r for r in question_results if r.result == ValidationResult.INCORRECT]
        if len(incorrect_results) > len(question_results) / 2:
            recommendations.append("⏰ Tómate más tiempo para leer las preguntas")
            recommendations.append("🤔 Piensa cuidadosamente antes de responder")

        # Recomendaciones por tiempo
        avg_time = sum(r.processing_time for r in question_results) / len(question_results)
        if avg_time > 120:
            recommendations.append("⚡ Practica para mejorar la velocidad de respuesta")
        elif avg_time < 10:
            recommendations.append("🔍 Dedica más tiempo a analizar las preguntas")

        return recommendations[:5]  # Máximo 5 recomendaciones

    def _suggest_difficulty_adjustment(self, question_results: List[QuestionValidationResult],
                                       exercise: 'Exercise') -> 'ExerciseDifficulty':
        """Sugerir ajuste de dificultad para futuros ejercicios"""
        avg_adjustment = sum(r.difficulty_adjustment for r in question_results) / len(question_results)
        current_difficulty = exercise.difficulty

        # Mapear dificultades a números para cálculo
        difficulty_levels = [
            ExerciseDifficulty.PRINCIPIANTE,
            ExerciseDifficulty.BASICO,
            ExerciseDifficulty.INTERMEDIO,
            ExerciseDifficulty.AVANZADO,
            ExerciseDifficulty.EXPERTO
        ]

        current_index = difficulty_levels.index(current_difficulty)

        if avg_adjustment > 0.2:  # Aumentar dificultad
            new_index = min(len(difficulty_levels) - 1, current_index + 1)
        elif avg_adjustment < -0.2:  # Reducir dificultad
            new_index = max(0, current_index - 1)
        else:
            new_index = current_index

        return difficulty_levels[new_index]

    def _identify_focus_areas(self, question_results: List[QuestionValidationResult],
                              exercise: 'Exercise') -> List[str]:
        """Identificar áreas de enfoque para futuros ejercicios"""
        focus_areas = []

        # Analizar habilidades practicadas en el ejercicio
        skills = exercise.skills_practiced

        # Identificar habilidades con bajo rendimiento
        incorrect_count = len([r for r in question_results if r.result == ValidationResult.INCORRECT])
        total_count = len(question_results)

        if incorrect_count / total_count > 0.5:
            # Más del 50% incorrecto
            focus_areas.extend(skills)
        elif incorrect_count / total_count > 0.3:
            # 30-50% incorrecto, enfoque moderado
            focus_areas.extend(skills[:2])  # Solo las primeras 2 habilidades

        # Añadir áreas específicas basadas en tipos de error
        if any(r.accuracy < 0.5 for r in question_results):
            focus_areas.append("Comprensión básica")

        if any(r.processing_time > 120 for r in question_results):
            focus_areas.append("Velocidad de procesamiento")

        return list(set(focus_areas))[:5]  # Máximo 5 áreas, sin duplicados

    def _calculate_validation_confidence(self, question_results: List[QuestionValidationResult]) -> float:
        """Calcular confianza general en la validación"""
        if not question_results:
            return 0.1

        avg_confidence = sum(r.confidence for r in question_results) / len(question_results)

        # Ajustar por consistencia de resultados
        confidence_variance = sum((r.confidence - avg_confidence) ** 2 for r in question_results) / len(
            question_results)
        consistency_factor = max(0.5, 1.0 - confidence_variance)

        return avg_confidence * consistency_factor

    def _create_fallback_validation_result(self, exercise: 'Exercise',
                                           responses: List[QuestionResponse]) -> ExerciseValidationResult:
        """Crear resultado de validación básico en caso de error"""
        fallback_results = []

        for i, response in enumerate(responses):
            if i < len(exercise.questions):
                question = exercise.questions[i]
                fallback_result = self._create_fallback_question_result(question, response)
                fallback_results.append(fallback_result)

        total_score = sum(r.points_earned for r in fallback_results)
        max_score = sum(r.max_points for r in fallback_results)

        return ExerciseValidationResult(
            exercise_id=f"fallback_{int(datetime.now().timestamp())}",
            question_results=fallback_results,
            total_score=total_score,
            max_possible_score=max_score,
            percentage_score=(total_score / max_score * 100) if max_score > 0 else 0,
            total_time=sum(r.time_taken for r in responses),
            strengths=["Completó el ejercicio"],
            weaknesses=["Error en validación automática"],
            recommendations=["Revisar manualmente las respuestas"],
            suggested_difficulty=exercise.difficulty,
            suggested_focus_areas=exercise.skills_practiced,
            validation_timestamp=datetime.now(),
            confidence_score=0.1
        )

    def _create_fallback_question_result(self, question: 'ExerciseQuestion',
                                         response: QuestionResponse) -> QuestionValidationResult:
        """Crear resultado de pregunta básico en caso de error"""
        fallback_feedback = ValidationFeedback(
            is_correct=False,
            score=0.0,
            feedback_message="Error en validación automática. Revisar manualmente.",
            feedback_type=FeedbackType.EXPLANATION
        )

        return QuestionValidationResult(
            question_id=f"fallback_{hash(question.question_text) % 1000}",
            result=ValidationResult.INVALID_FORMAT,
            feedback=fallback_feedback,
            points_earned=0.0,
            max_points=question.difficulty_points,
            processing_time=0.0,
            accuracy=0.0,
            confidence=0.1,
            difficulty_adjustment=0.0
        )


# =============================================================================
# FUNCIONES DE UTILIDAD
# =============================================================================

def quick_validate_answer(question_text: str, question_type: QuestionType,
                          correct_answer: str, user_answer: str) -> Dict[str, Any]:
    """
    Validación rápida de una respuesta individual

    Args:
        question_text: Texto de la pregunta
        question_type: Tipo de pregunta
        correct_answer: Respuesta correcta
        user_answer: Respuesta del usuario

    Returns:
        Dict con resultado de validación
    """
    from modules.exercises.exercise_generator import ExerciseQuestion

    # Crear objetos mínimos
    question = ExerciseQuestion(
        question_text=question_text,
        question_type=question_type,
        correct_answer=correct_answer,
        difficulty_points=1
    )

    response = QuestionResponse(
        question_id="quick_validate",
        user_answer=user_answer,
        time_taken=30.0
    )

    # Validar
    validator = ExerciseValidator()
    result = validator.validate_question(question, response)

    return {
        'is_correct': result.feedback.is_correct,
        'score': result.feedback.score,
        'message': result.feedback.feedback_message,
        'confidence': result.confidence,
        'points_earned': result.points_earned
    }


def batch_validate_responses(questions: List['ExerciseQuestion'],
                             responses: List[QuestionResponse]) -> List[Dict[str, Any]]:
    """
    Validar múltiples respuestas en lote

    Args:
        questions: Lista de preguntas
        responses: Lista de respuestas

    Returns:
        Lista de resultados de validación
    """
    validator = ExerciseValidator()
    results = []

    for question, response in zip(questions, responses):
        try:
            result = validator.validate_question(question, response)
            results.append({
                'question_id': result.question_id,
                'is_correct': result.feedback.is_correct,
                'score': result.feedback.score,
                'points_earned': result.points_earned,
                'feedback': result.feedback.feedback_message
            })
        except Exception as e:
            results.append({
                'question_id': f"error_{len(results)}",
                'is_correct': False,
                'score': 0.0,
                'points_earned': 0.0,
                'feedback': f"Error de validación: {str(e)}"
            })

    return results


def analyze_learning_progress(validation_results: List[ExerciseValidationResult]) -> Dict[str, Any]:
    """
    Analizar progreso de aprendizaje basado en múltiples ejercicios

    Args:
        validation_results: Lista de resultados de ejercicios

    Returns:
        Dict con análisis de progreso
    """
    if not validation_results:
        return {"error": "No hay resultados para analizar"}

    # Calcular tendencias
    scores = [r.percentage_score for r in validation_results]
    times = [r.total_time for r in validation_results]

    # Progreso en puntuación
    if len(scores) > 1:
        score_trend = scores[-1] - scores[0]  # Diferencia entre último y primer ejercicio
        improving = score_trend > 5  # Mejora de más del 5%
    else:
        score_trend = 0
        improving = False

    # Progreso en velocidad
    if len(times) > 1:
        time_trend = times[0] - times[-1]  # Reducción de tiempo es positiva
        getting_faster = time_trend > 0
    else:
        time_trend = 0
        getting_faster = False

    # Áreas de fortaleza y debilidad consistentes
    all_strengths = []
    all_weaknesses = []
    for result in validation_results:
        all_strengths.extend(result.strengths)
        all_weaknesses.extend(result.weaknesses)

    # Contar frecuencias
    from collections import Counter
    strength_counts = Counter(all_strengths)
    weakness_counts = Counter(all_weaknesses)

    return {
        'total_exercises': len(validation_results),
        'average_score': sum(scores) / len(scores),
        'latest_score': scores[-1],
        'score_trend': score_trend,
        'improving': improving,
        'average_time': sum(times) / len(times),
        'getting_faster': getting_faster,
        'consistent_strengths': [item for item, count in strength_counts.most_common(3)],
        'consistent_weaknesses': [item for item, count in weakness_counts.most_common(3)],
        'confidence_trend': [r.confidence_score for r in validation_results]
    }


# =============================================================================
# CÓDIGO DE PRUEBA
# =============================================================================

if __name__ == "__main__":
    print("🧪 Probando validador de ejercicios...")

    # Importar clases necesarias para las pruebas
    try:
        from modules.exercises.exercise_generator import ExerciseQuestion, QuestionType
    except ImportError:
        print("⚠️ Usando definiciones básicas para pruebas")


        @dataclass
        class ExerciseQuestion:
            question_text: str
            question_type: QuestionType
            correct_answer: str
            options: List[str] = None
            explanation: str = "Explicación de prueba"
            difficulty_points: int = 1

    # Crear preguntas de prueba
    test_questions = [
        ExerciseQuestion(
            question_text="¿Cuál es la capital de Francia?",
            question_type=QuestionType.MULTIPLE_CHOICE,
            correct_answer="París",
            options=["París", "Londres", "Madrid", "Roma"],
            difficulty_points=1
        ),
        ExerciseQuestion(
            question_text="El agua hierve a 100 grados Celsius",
            question_type=QuestionType.TRUE_FALSE,
            correct_answer="Verdadero",
            difficulty_points=1
        ),
        ExerciseQuestion(
            question_text="Completa: El _____ es el animal más grande del océano",
            question_type=QuestionType.FILL_IN_BLANK,
            correct_answer="ballena",
            difficulty_points=2
        ),
        ExerciseQuestion(
            question_text="Explica qué es la fotosíntesis",
            question_type=QuestionType.SHORT_ANSWER,
            correct_answer="Proceso por el cual las plantas convierten luz solar en energía",
            difficulty_points=3
        )
    ]

    # Crear respuestas de prueba
    test_responses = [
        QuestionResponse("q1", "París", 15.0),
        QuestionResponse("q2", "Verdadero", 8.0),
        QuestionResponse("q3", "ballena", 12.0),
        QuestionResponse("q4", "Es cuando las plantas usan el sol para hacer energia", 45.0, attempts=2)
    ]

    validator = ExerciseValidator()

    print("\n🔍 VALIDACIÓN DE PREGUNTAS INDIVIDUALES:")
    print("=" * 60)

    for i, (question, response) in enumerate(zip(test_questions, test_responses), 1):
        print(f"\n📋 PREGUNTA {i}:")
        print(f"❓ {question.question_text}")
        print(f"✅ Respuesta correcta: {question.correct_answer}")
        print(f"👤 Respuesta usuario: {response.user_answer}")
        print(f"⏱️ Tiempo: {response.time_taken}s")

        try:
            result = validator.validate_question(question, response)

            print(f"\n📊 RESULTADO:")
            print(f"✅ Correcto: {result.feedback.is_correct}")
            print(f"🎯 Puntuación: {result.feedback.score:.2f}")
            print(f"💰 Puntos ganados: {result.points_earned:.1f}/{result.max_points}")
            print(f"💬 Mensaje: {result.feedback.feedback_message}")
            print(f"🎯 Confianza: {result.confidence:.2f}")

            if result.feedback.suggestions:
                print(f"💡 Sugerencias:")
                for suggestion in result.feedback.suggestions:
                    print(f"  • {suggestion}")

            if hasattr(result.feedback, 'similarity_score') and result.feedback.similarity_score:
                print(f"📊 Similitud: {result.feedback.similarity_score:.2f}")

        except Exception as e:
            print(f"❌ Error validando pregunta: {e}")

        print("-" * 60)

    # Prueba de validación rápida
    print(f"\n⚡ PRUEBA DE VALIDACIÓN RÁPIDA:")
    try:
        quick_result = quick_validate_answer(
            "¿Cuál es 2+2?",
            QuestionType.SHORT_ANSWER,
            "4",
            "cuatro"
        )
        print(f"Resultado rápido: {quick_result}")
    except Exception as e:
        print(f"❌ Error en validación rápida: {e}")

    # Prueba de validación en lote
    print(f"\n📦 PRUEBA DE VALIDACIÓN EN LOTE:")
    try:
        batch_results = batch_validate_responses(test_questions[:2], test_responses[:2])
        print(f"Resultados en lote:")
        for result in batch_results:
            print(f"  • {result['question_id']}: {result['is_correct']} ({result['score']:.2f})")
    except Exception as e:
        print(f"❌ Error en validación en lote: {e}")

    print(f"\n✅ Pruebas del validador de ejercicios completadas!")
# =============================================================================
# AlfaIA/modules/nlp/difficulty_calculator.py - Calculador de Dificultad de Texto
# =============================================================================

import re
import math
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import sys
from pathlib import Path
from collections import Counter

# Agregar el directorio raíz al path para imports
sys.path.append(str(Path(__file__).parent.parent.parent))

# Imports de otros módulos NLP
try:
    from modules.nlp.text_analyzer import TextAnalyzer, DifficultyLevel

    ANALYZER_AVAILABLE = True
except ImportError:
    print("⚠️ TextAnalyzer no disponible, usando implementación básica")
    ANALYZER_AVAILABLE = False


    # Definir DifficultyLevel si no está disponible
    class DifficultyLevel(Enum):
        MUY_FACIL = "muy_facil"
        FACIL = "facil"
        INTERMEDIO = "intermedio"
        DIFICIL = "dificil"
        MUY_DIFICIL = "muy_dificil"

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print("🔧 Inicializando calculador de dificultad...")


# =============================================================================
# ENUMS Y DATACLASSES
# =============================================================================

class EducationLevel(Enum):
    """Niveles educativos para calibrar dificultad"""
    PRIMARIA_INICIAL = "primaria_inicial"  # 6-8 años
    PRIMARIA_MEDIA = "primaria_media"  # 9-11 años
    PRIMARIA_SUPERIOR = "primaria_superior"  # 12-14 años
    SECUNDARIA = "secundaria"  # 15-18 años
    UNIVERSITARIO = "universitario"  # 18+ años
    PROFESIONAL = "profesional"  # Nivel avanzado


class ReadingSkillLevel(Enum):
    """Niveles de habilidad lectora"""
    INICIAL = "inicial"
    BASICO = "basico"
    INTERMEDIO = "intermedio"
    AVANZADO = "avanzado"
    EXPERTO = "experto"


class TextComplexityFactor(Enum):
    """Factores que afectan la complejidad del texto"""
    VOCABULARIO = "vocabulario"
    SINTAXIS = "sintaxis"
    SEMANTICA = "semantica"
    LONGITUD = "longitud"
    ESTRUCTURA = "estructura"
    COHESION = "cohesion"


@dataclass
class ComplexityMetrics:
    """Métricas de complejidad del texto"""
    # Métricas léxicas
    vocabulary_complexity: float  # 0-100
    rare_words_ratio: float  # 0-1
    academic_words_ratio: float  # 0-1
    avg_word_length: float  # Promedio de caracteres por palabra

    # Métricas sintácticas
    avg_sentence_length: float  # Promedio de palabras por oración
    syntax_complexity: float  # 0-100
    subordinate_clauses_ratio: float  # 0-1

    # Métricas semánticas
    semantic_density: float  # 0-100
    concept_complexity: float  # 0-100
    abstract_concepts_ratio: float  # 0-1

    # Métricas estructurales
    text_organization: float  # 0-100
    cohesion_score: float  # 0-100
    information_density: float  # 0-100


@dataclass
class DifficultyAssessment:
    """Evaluación completa de dificultad"""
    overall_difficulty: DifficultyLevel
    difficulty_score: float  # 0-100
    complexity_metrics: ComplexityMetrics
    target_education_level: EducationLevel
    target_reading_skill: ReadingSkillLevel

    # Análisis por factores
    factor_scores: Dict[TextComplexityFactor, float]

    # Recomendaciones
    recommendations: List[str]
    adaptations_needed: List[str]

    # Estimaciones
    estimated_reading_time: float  # Minutos
    estimated_comprehension: float  # 0-100

    # Metadatos
    confidence_score: float  # 0-1
    processing_time: float


# =============================================================================
# CLASE PRINCIPAL DE CÁLCULO DE DIFICULTAD
# =============================================================================

class DifficultyCalculator:
    """
    Calculador avanzado de dificultad de texto para AlfaIA
    """

    def __init__(self):
        """Inicializar calculador"""
        self.logger = logger

        # Cargar base de datos de vocabulario
        self._load_vocabulary_databases()

        # Configurar parámetros de cálculo
        self._setup_calculation_parameters()

        # Inicializar analizador de texto si está disponible
        if ANALYZER_AVAILABLE:
            self.text_analyzer = TextAnalyzer()
        else:
            self.text_analyzer = None

        print("✅ DifficultyCalculator inicializado")

    def _load_vocabulary_databases(self):
        """Cargar bases de datos de vocabulario"""
        # Palabras básicas (más comunes del español)
        self.basic_vocabulary = {
            'a', 'ante', 'bajo', 'cabe', 'con', 'contra', 'de', 'desde', 'durante', 'en',
            'entre', 'hacia', 'hasta', 'mediante', 'para', 'por', 'según', 'sin', 'so',
            'sobre', 'tras', 'versus', 'vía', 'el', 'la', 'los', 'las', 'un', 'una',
            'unos', 'unas', 'este', 'esta', 'estos', 'estas', 'ese', 'esa', 'esos',
            'esas', 'aquel', 'aquella', 'aquellos', 'aquellas', 'yo', 'tú', 'él',
            'ella', 'nosotros', 'vosotros', 'ellos', 'ellas', 'me', 'te', 'se', 'nos',
            'os', 'le', 'les', 'lo', 'la', 'los', 'las', 'mi', 'tu', 'su', 'nuestro',
            'vuestro', 'ser', 'estar', 'tener', 'hacer', 'decir', 'ir', 'ver', 'dar',
            'saber', 'querer', 'llegar', 'pasar', 'deber', 'poner', 'parecer', 'quedar',
            'creer', 'hablar', 'llevar', 'dejar', 'seguir', 'encontrar', 'llamar',
            'venir', 'pensar', 'salir', 'volver', 'tomar', 'conocer', 'vivir', 'sentir',
            'tratar', 'mirar', 'contar', 'empezar', 'esperar', 'buscar', 'existir',
            'entrar', 'trabajar', 'escribir', 'perder', 'producir', 'ocurrir'
        }

        # Palabras de nivel intermedio
        self.intermediate_vocabulary = {
            'análisis', 'sistema', 'proceso', 'desarrollo', 'estructura', 'función',
            'elemento', 'aspecto', 'concepto', 'método', 'técnica', 'información',
            'conocimiento', 'experiencia', 'investigación', 'resultado', 'conclusión',
            'objetivo', 'estrategia', 'evaluación', 'descripción', 'explicación',
            'interpretación', 'aplicación', 'implementación', 'organización',
            'comunicación', 'participación', 'colaboración', 'coordinación',
            'administración', 'gestión', 'planificación', 'programación',
            'establecimiento', 'mantenimiento', 'mejoramiento', 'optimización'
        }

        # Palabras académicas/técnicas
        self.academic_vocabulary = {
            'epistemología', 'paradigma', 'metodología', 'hermenéutica', 'heurística',
            'dialéctica', 'fenomenología', 'ontología', 'axiología', 'teleología',
            'empirismo', 'racionalismo', 'positivismo', 'relativismo', 'nihilismo',
            'existencialismo', 'pragmatismo', 'estructuralismo', 'funcionalismo',
            'conductismo', 'cognitivismo', 'constructivismo', 'deconstrucción',
            'interdisciplinario', 'multidisciplinario', 'transdisciplinario',
            'metacognición', 'autorregulación', 'heterogeneidad', 'homogeneidad',
            'isomorfismo', 'polimorfismo', 'morfogénesis', 'diferenciación',
            'especialización', 'generalización', 'categorización', 'taxonomía'
        }

        # Conectores y marcadores discursivos por nivel
        self.discourse_markers = {
            'basic': {'y', 'pero', 'porque', 'cuando', 'si', 'que', 'como', 'donde'},
            'intermediate': {'además', 'sin embargo', 'por tanto', 'aunque', 'mientras',
                             'puesto que', 'a pesar de', 'en cambio', 'por ejemplo'},
            'advanced': {'no obstante', 'por consiguiente', 'en consecuencia',
                         'asimismo', 'por ende', 'en virtud de', 'habida cuenta',
                         'en aras de', 'empero', 'con todo'}
        }

    def _setup_calculation_parameters(self):
        """Configurar parámetros para cálculos de dificultad"""
        # Pesos para diferentes factores de complejidad
        self.complexity_weights = {
            TextComplexityFactor.VOCABULARIO: 0.25,
            TextComplexityFactor.SINTAXIS: 0.20,
            TextComplexityFactor.SEMANTICA: 0.20,
            TextComplexityFactor.LONGITUD: 0.15,
            TextComplexityFactor.ESTRUCTURA: 0.10,
            TextComplexityFactor.COHESION: 0.10
        }

        # Umbrales para clasificación de dificultad
        self.difficulty_thresholds = {
            DifficultyLevel.MUY_FACIL: (0, 20),
            DifficultyLevel.FACIL: (20, 40),
            DifficultyLevel.INTERMEDIO: (40, 60),
            DifficultyLevel.DIFICIL: (60, 80),
            DifficultyLevel.MUY_DIFICIL: (80, 100)
        }

        # Velocidades de lectura por nivel (palabras por minuto)
        self.reading_speeds = {
            EducationLevel.PRIMARIA_INICIAL: 80,
            EducationLevel.PRIMARIA_MEDIA: 120,
            EducationLevel.PRIMARIA_SUPERIOR: 160,
            EducationLevel.SECUNDARIA: 200,
            EducationLevel.UNIVERSITARIO: 250,
            EducationLevel.PROFESIONAL: 300
        }

    def calculate_difficulty(self, text: str, target_level: Optional[EducationLevel] = None) -> DifficultyAssessment:
        """
        Calcular dificultad completa de un texto

        Args:
            text: Texto a analizar
            target_level: Nivel educativo objetivo (opcional)

        Returns:
            DifficultyAssessment: Evaluación completa de dificultad
        """
        import time
        start_time = time.time()

        try:
            print(f"📊 Calculando dificultad de texto de {len(text)} caracteres...")

            # 1. Calcular métricas de complejidad
            complexity_metrics = self._calculate_complexity_metrics(text)

            # 2. Calcular puntuaciones por factor
            factor_scores = self._calculate_factor_scores(text, complexity_metrics)

            # 3. Calcular dificultad general
            difficulty_score = self._calculate_overall_difficulty_score(factor_scores)
            overall_difficulty = self._classify_difficulty_level(difficulty_score)

            # 4. Determinar niveles objetivo
            target_education_level = target_level or self._estimate_education_level(difficulty_score)
            target_reading_skill = self._estimate_reading_skill_level(difficulty_score)

            # 5. Generar recomendaciones
            recommendations = self._generate_recommendations(
                complexity_metrics, factor_scores, overall_difficulty
            )
            adaptations_needed = self._suggest_adaptations(
                complexity_metrics, target_education_level
            )

            # 6. Calcular estimaciones
            word_count = len(self._tokenize_words(text))
            reading_speed = self.reading_speeds.get(target_education_level, 200)
            estimated_reading_time = word_count / reading_speed
            estimated_comprehension = self._estimate_comprehension(
                difficulty_score, target_education_level
            )

            # 7. Calcular confianza
            confidence_score = self._calculate_confidence(text, complexity_metrics)

            processing_time = time.time() - start_time

            result = DifficultyAssessment(
                overall_difficulty=overall_difficulty,
                difficulty_score=difficulty_score,
                complexity_metrics=complexity_metrics,
                target_education_level=target_education_level,
                target_reading_skill=target_reading_skill,
                factor_scores=factor_scores,
                recommendations=recommendations,
                adaptations_needed=adaptations_needed,
                estimated_reading_time=estimated_reading_time,
                estimated_comprehension=estimated_comprehension,
                confidence_score=confidence_score,
                processing_time=processing_time
            )

            print(f"✅ Cálculo de dificultad completado en {processing_time:.2f}s")
            return result

        except Exception as e:
            error_msg = f"Error calculando dificultad: {str(e)}"
            self.logger.error(error_msg)

            # Retornar evaluación mínima en caso de error
            return self._create_fallback_assessment(text, time.time() - start_time)

    def _calculate_complexity_metrics(self, text: str) -> ComplexityMetrics:
        """Calcular métricas detalladas de complejidad"""
        words = self._tokenize_words(text)
        sentences = self._split_sentences(text)

        # Métricas léxicas
        vocabulary_complexity = self._calculate_vocabulary_complexity(words)
        rare_words_ratio = self._calculate_rare_words_ratio(words)
        academic_words_ratio = self._calculate_academic_words_ratio(words)
        avg_word_length = sum(len(word) for word in words) / len(words) if words else 0

        # Métricas sintácticas
        avg_sentence_length = len(words) / len(sentences) if sentences else 0
        syntax_complexity = self._calculate_syntax_complexity(text)
        subordinate_clauses_ratio = self._calculate_subordinate_clauses_ratio(text)

        # Métricas semánticas
        semantic_density = self._calculate_semantic_density(words)
        concept_complexity = self._calculate_concept_complexity(words)
        abstract_concepts_ratio = self._calculate_abstract_concepts_ratio(words)

        # Métricas estructurales
        text_organization = self._calculate_text_organization(text)
        cohesion_score = self._calculate_cohesion_score(text)
        information_density = self._calculate_information_density(text)

        return ComplexityMetrics(
            vocabulary_complexity=vocabulary_complexity,
            rare_words_ratio=rare_words_ratio,
            academic_words_ratio=academic_words_ratio,
            avg_word_length=avg_word_length,
            avg_sentence_length=avg_sentence_length,
            syntax_complexity=syntax_complexity,
            subordinate_clauses_ratio=subordinate_clauses_ratio,
            semantic_density=semantic_density,
            concept_complexity=concept_complexity,
            abstract_concepts_ratio=abstract_concepts_ratio,
            text_organization=text_organization,
            cohesion_score=cohesion_score,
            information_density=information_density
        )

    def _tokenize_words(self, text: str) -> List[str]:
        """Tokenizar texto en palabras"""
        words = re.findall(r'\b[a-zA-ZáéíóúüñÁÉÍÓÚÜÑ]+\b', text.lower())
        return words

    def _split_sentences(self, text: str) -> List[str]:
        """Dividir texto en oraciones"""
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        return sentences

    def _calculate_vocabulary_complexity(self, words: List[str]) -> float:
        """Calcular complejidad del vocabulario (0-100)"""
        if not words:
            return 0.0

        total_words = len(words)
        basic_words = sum(1 for word in words if word in self.basic_vocabulary)
        intermediate_words = sum(1 for word in words if word in self.intermediate_vocabulary)
        academic_words = sum(1 for word in words if word in self.academic_vocabulary)

        # Puntuación ponderada
        basic_score = (basic_words / total_words) * 10
        intermediate_score = (intermediate_words / total_words) * 50
        academic_score = (academic_words / total_words) * 90

        # Palabras no clasificadas contribuyen según longitud
        unclassified_words = total_words - basic_words - intermediate_words - academic_words
        avg_unclassified_length = sum(
            len(word) for word in words
            if word not in self.basic_vocabulary
            and word not in self.intermediate_vocabulary
            and word not in self.academic_vocabulary
        ) / max(unclassified_words, 1)

        unclassified_score = (unclassified_words / total_words) * min(avg_unclassified_length * 8, 70)

        complexity = basic_score + intermediate_score + academic_score + unclassified_score
        return min(complexity, 100.0)

    def _calculate_rare_words_ratio(self, words: List[str]) -> float:
        """Calcular ratio de palabras raras"""
        if not words:
            return 0.0

        word_counts = Counter(words)
        rare_words = sum(1 for count in word_counts.values() if count == 1)
        return rare_words / len(word_counts)

    def _calculate_academic_words_ratio(self, words: List[str]) -> float:
        """Calcular ratio de palabras académicas"""
        if not words:
            return 0.0

        academic_words = sum(1 for word in words if word in self.academic_vocabulary)
        return academic_words / len(words)

    def _calculate_syntax_complexity(self, text: str) -> float:
        """Calcular complejidad sintáctica (0-100)"""
        # Buscar indicadores de complejidad sintáctica
        complexity_indicators = [
            r'\bque\b.*\bque\b',  # Oraciones con múltiples "que"
            r'\b(aunque|sin embargo|no obstante|por tanto)\b',  # Conectores complejos
            r'\b(habiendo|siendo|estando)\b',  # Gerundios complejos
            r'[,;:]{2,}',  # Puntuación compleja
            r'\([^)]+\)',  # Paréntesis
            r'".+"',  # Citas
        ]

        complexity_score = 0
        text_lower = text.lower()

        for pattern in complexity_indicators:
            matches = len(re.findall(pattern, text_lower))
            complexity_score += matches * 10

        # Normalizar por longitud del texto
        sentences = self._split_sentences(text)
        if sentences:
            complexity_score = (complexity_score / len(sentences)) * 10

        return min(complexity_score, 100.0)

    def _calculate_subordinate_clauses_ratio(self, text: str) -> float:
        """Calcular ratio de cláusulas subordinadas"""
        subordinate_markers = [
            'que', 'cuando', 'donde', 'como', 'porque', 'aunque', 'si', 'mientras',
            'hasta que', 'para que', 'sin que', 'con tal de que', 'a fin de que'
        ]

        text_lower = text.lower()
        total_clauses = 0

        for marker in subordinate_markers:
            total_clauses += len(re.findall(r'\b' + marker + r'\b', text_lower))

        sentences = self._split_sentences(text)
        return total_clauses / max(len(sentences), 1)

    def _calculate_semantic_density(self, words: List[str]) -> float:
        """Calcular densidad semántica (0-100)"""
        if not words:
            return 0.0

        # Palabras de contenido vs palabras funcionales
        function_words = self.basic_vocabulary
        content_words = [word for word in words if word not in function_words]

        semantic_density = len(content_words) / len(words) * 100
        return min(semantic_density, 100.0)

    def _calculate_concept_complexity(self, words: List[str]) -> float:
        """Calcular complejidad conceptual (0-100)"""
        # Indicadores de conceptos complejos
        complex_suffixes = ['ción', 'sión', 'idad', 'ismo', 'ología', 'mente']
        abstract_prefixes = ['meta', 'pseudo', 'anti', 'contra', 'sub', 'inter', 'trans']

        complex_concepts = 0
        for word in words:
            if any(word.endswith(suffix) for suffix in complex_suffixes):
                complex_concepts += 1
            if any(word.startswith(prefix) for prefix in abstract_prefixes):
                complex_concepts += 1

        return min((complex_concepts / max(len(words), 1)) * 200, 100.0)

    def _calculate_abstract_concepts_ratio(self, words: List[str]) -> float:
        """Calcular ratio de conceptos abstractos"""
        abstract_indicators = [
            'idea', 'concepto', 'teoría', 'principio', 'método', 'sistema',
            'proceso', 'análisis', 'síntesis', 'evaluación', 'interpretación'
        ]

        abstract_words = sum(1 for word in words if word in abstract_indicators)
        return abstract_words / max(len(words), 1)

    def _calculate_text_organization(self, text: str) -> float:
        """Calcular calidad de organización del texto (0-100)"""
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]

        organization_score = 0

        # Puntos por tener múltiples párrafos
        if len(paragraphs) > 1:
            organization_score += 30

        # Puntos por uso de conectores
        discourse_markers_found = 0
        text_lower = text.lower()

        for level, markers in self.discourse_markers.items():
            for marker in markers:
                if marker in text_lower:
                    discourse_markers_found += 1

        organization_score += min(discourse_markers_found * 5, 40)

        # Puntos por estructura equilibrada
        if paragraphs:
            lengths = [len(p.split()) for p in paragraphs]
            if lengths:
                avg_length = sum(lengths) / len(lengths)
                variance = sum((l - avg_length) ** 2 for l in lengths) / len(lengths)
                if variance < avg_length:  # Baja varianza indica equilibrio
                    organization_score += 30

        return min(organization_score, 100.0)

    def _calculate_cohesion_score(self, text: str) -> float:
        """Calcular puntuación de cohesión (0-100)"""
        words = self._tokenize_words(text)

        if len(words) < 10:
            return 50.0  # Texto muy corto

        # Repetición léxica (indicador básico de cohesión)
        word_counts = Counter(words)
        repeated_words = sum(1 for count in word_counts.values() if count > 1)
        repetition_ratio = repeated_words / len(word_counts)

        # Uso de pronombres y referencias
        pronouns = ['él', 'ella', 'ellos', 'ellas', 'este', 'esta', 'estos', 'estas', 'eso', 'aquello']
        pronoun_count = sum(1 for word in words if word in pronouns)
        pronoun_ratio = pronoun_count / len(words)

        # Conectores cohesivos
        cohesive_connectors = [
            'además', 'también', 'asimismo', 'por otro lado', 'en cambio',
            'sin embargo', 'no obstante', 'por tanto', 'por consiguiente'
        ]
        connector_count = sum(1 for connector in cohesive_connectors if connector in text.lower())

        cohesion_score = (repetition_ratio * 40) + (pronoun_ratio * 100) + (connector_count * 10)
        return min(cohesion_score, 100.0)

    def _calculate_information_density(self, text: str) -> float:
        """Calcular densidad de información (0-100)"""
        words = self._tokenize_words(text)
        sentences = self._split_sentences(text)

        if not words or not sentences:
            return 0.0

        # Ratio de palabras de contenido por oración
        content_words_per_sentence = len(words) / len(sentences)

        # Normalizar: 10-15 palabras de contenido por oración = densidad media
        density_score = min((content_words_per_sentence / 12.5) * 50, 100.0)

        return density_score

    def _calculate_factor_scores(self, text: str, metrics: ComplexityMetrics) -> Dict[TextComplexityFactor, float]:
        """Calcular puntuaciones por factor de complejidad"""
        return {
            TextComplexityFactor.VOCABULARIO: metrics.vocabulary_complexity,
            TextComplexityFactor.SINTAXIS: metrics.syntax_complexity,
            TextComplexityFactor.SEMANTICA: metrics.semantic_density,
            TextComplexityFactor.LONGITUD: min((metrics.avg_sentence_length / 20) * 100, 100),
            TextComplexityFactor.ESTRUCTURA: metrics.text_organization,
            TextComplexityFactor.COHESION: metrics.cohesion_score
        }

    def _calculate_overall_difficulty_score(self, factor_scores: Dict[TextComplexityFactor, float]) -> float:
        """Calcular puntuación general de dificultad"""
        weighted_score = 0.0

        for factor, score in factor_scores.items():
            weight = self.complexity_weights.get(factor, 0.0)
            weighted_score += score * weight

        return min(weighted_score, 100.0)

    def _classify_difficulty_level(self, difficulty_score: float) -> DifficultyLevel:
        """Clasificar nivel de dificultad basado en puntuación"""
        for level, (min_score, max_score) in self.difficulty_thresholds.items():
            if min_score <= difficulty_score < max_score:
                return level

        return DifficultyLevel.MUY_DIFICIL  # Por defecto si está fuera de rango

    def _estimate_education_level(self, difficulty_score: float) -> EducationLevel:
        """Estimar nivel educativo apropiado"""
        if difficulty_score < 25:
            return EducationLevel.PRIMARIA_INICIAL
        elif difficulty_score < 35:
            return EducationLevel.PRIMARIA_MEDIA
        elif difficulty_score < 45:
            return EducationLevel.PRIMARIA_SUPERIOR
        elif difficulty_score < 65:
            return EducationLevel.SECUNDARIA
        elif difficulty_score < 80:
            return EducationLevel.UNIVERSITARIO
        else:
            return EducationLevel.PROFESIONAL

    def _estimate_reading_skill_level(self, difficulty_score: float) -> ReadingSkillLevel:
        """Estimar nivel de habilidad lectora requerida"""
        if difficulty_score < 20:
            return ReadingSkillLevel.INICIAL
        elif difficulty_score < 40:
            return ReadingSkillLevel.BASICO
        elif difficulty_score < 60:
            return ReadingSkillLevel.INTERMEDIO
        elif difficulty_score < 80:
            return ReadingSkillLevel.AVANZADO
        else:
            return ReadingSkillLevel.EXPERTO

    def _estimate_comprehension(self, difficulty_score: float, education_level: EducationLevel) -> float:
        """Estimar nivel de comprensión esperado"""
        # Mapear niveles educativos a capacidades
        level_capabilities = {
            EducationLevel.PRIMARIA_INICIAL: 30,
            EducationLevel.PRIMARIA_MEDIA: 45,
            EducationLevel.PRIMARIA_SUPERIOR: 60,
            EducationLevel.SECUNDARIA: 75,
            EducationLevel.UNIVERSITARIO: 85,
            EducationLevel.PROFESIONAL: 95
        }

        base_capability = level_capabilities.get(education_level, 70)

        # Ajustar según dificultad del texto
        difficulty_penalty = max(0, difficulty_score - base_capability) * 0.5
        comprehension = max(10, base_capability - difficulty_penalty)

        return min(comprehension, 100.0)

    def _generate_recommendations(self, metrics: ComplexityMetrics,
                                  factor_scores: Dict[TextComplexityFactor, float],
                                  difficulty: DifficultyLevel) -> List[str]:
        """Generar recomendaciones para mejorar legibilidad"""
        recommendations = []

        # Recomendaciones por vocabulario
        if metrics.vocabulary_complexity > 70:
            recommendations.append("📚 Considera simplificar el vocabulario usando sinónimos más comunes")

        if metrics.academic_words_ratio > 0.15:
            recommendations.append("🎓 Alto uso de términos académicos. Añade definiciones o explicaciones")

        if metrics.avg_word_length > 8:
            recommendations.append("✂️ Las palabras son muy largas en promedio. Usa términos más concisos")

        # Recomendaciones por sintaxis
        if metrics.avg_sentence_length > 25:
            recommendations.append("📝 Las oraciones son muy largas. Divídelas en oraciones más cortas")

        if metrics.subordinate_clauses_ratio > 0.4:
            recommendations.append("🔗 Muchas cláusulas subordinadas. Simplifica la estructura sintáctica")

        # Recomendaciones por organización
        if metrics.text_organization < 50:
            recommendations.append("📋 Mejora la organización del texto con párrafos y conectores claros")

        if metrics.cohesion_score < 40:
            recommendations.append("🔄 Aumenta la cohesión usando más pronombres y referencias")

        # Recomendaciones específicas por nivel de dificultad
        if difficulty == DifficultyLevel.MUY_DIFICIL:
            recommendations.append("⚠️ Texto muy complejo. Considera crear una versión simplificada")
        elif difficulty == DifficultyLevel.MUY_FACIL:
            recommendations.append("📈 El texto podría ser más rico y elaborado para el público objetivo")

        if not recommendations:
            recommendations.append("✅ El texto tiene un nivel de complejidad apropiado")

        return recommendations

    def _suggest_adaptations(self, metrics: ComplexityMetrics,
                             target_level: EducationLevel) -> List[str]:
        """Sugerir adaptaciones específicas para el nivel objetivo"""
        adaptations = []

        # Adaptaciones por nivel educativo
        if target_level in [EducationLevel.PRIMARIA_INICIAL, EducationLevel.PRIMARIA_MEDIA]:
            if metrics.avg_sentence_length > 12:
                adaptations.append("✂️ Reducir oraciones a máximo 12 palabras")

            if metrics.vocabulary_complexity > 40:
                adaptations.append("📚 Reemplazar palabras complejas con vocabulario básico")

            if metrics.academic_words_ratio > 0.05:
                adaptations.append("🎓 Eliminar o explicar términos académicos")

            adaptations.append("🎨 Añadir elementos visuales para apoyar la comprensión")

        elif target_level == EducationLevel.PRIMARIA_SUPERIOR:
            if metrics.avg_sentence_length > 18:
                adaptations.append("✂️ Reducir oraciones a máximo 18 palabras")

            if metrics.syntax_complexity > 60:
                adaptations.append("🔗 Simplificar estructuras sintácticas complejas")

        elif target_level == EducationLevel.SECUNDARIA:
            if metrics.information_density > 80:
                adaptations.append("📊 Reducir densidad de información por párrafo")

            if metrics.abstract_concepts_ratio > 0.3:
                adaptations.append("💭 Proporcionar ejemplos concretos para conceptos abstractos")

        # Adaptaciones generales
        if metrics.text_organization < 60:
            adaptations.append("📋 Añadir subtítulos y mejorar estructura del texto")

        if metrics.cohesion_score < 50:
            adaptations.append("🔄 Mejorar conectores entre ideas y párrafos")

        return adaptations

    def _calculate_confidence(self, text: str, metrics: ComplexityMetrics) -> float:
        """Calcular confianza en la evaluación"""
        confidence = 1.0

        # Penalizar textos muy cortos
        word_count = len(self._tokenize_words(text))
        if word_count < 50:
            confidence *= 0.7
        elif word_count < 20:
            confidence *= 0.5

        # Penalizar si faltan métricas importantes
        if metrics.vocabulary_complexity == 0:
            confidence *= 0.8

        if metrics.text_organization < 20:
            confidence *= 0.9

        return max(0.1, confidence)

    def _create_fallback_assessment(self, text: str, processing_time: float) -> DifficultyAssessment:
        """Crear evaluación mínima en caso de error"""
        words = self._tokenize_words(text)
        word_count = len(words)

        # Estimación muy básica
        basic_difficulty_score = min((word_count / 100) * 50, 80)

        return DifficultyAssessment(
            overall_difficulty=DifficultyLevel.INTERMEDIO,
            difficulty_score=basic_difficulty_score,
            complexity_metrics=ComplexityMetrics(
                vocabulary_complexity=0, rare_words_ratio=0, academic_words_ratio=0,
                avg_word_length=0, avg_sentence_length=0, syntax_complexity=0,
                subordinate_clauses_ratio=0, semantic_density=0, concept_complexity=0,
                abstract_concepts_ratio=0, text_organization=0, cohesion_score=0,
                information_density=0
            ),
            target_education_level=EducationLevel.SECUNDARIA,
            target_reading_skill=ReadingSkillLevel.INTERMEDIO,
            factor_scores={factor: 0.0 for factor in TextComplexityFactor},
            recommendations=["Error en el análisis, evaluación básica aplicada"],
            adaptations_needed=["Revisar texto manualmente"],
            estimated_reading_time=word_count / 200,
            estimated_comprehension=50.0,
            confidence_score=0.1,
            processing_time=processing_time
        )


# =============================================================================
# FUNCIONES DE UTILIDAD
# =============================================================================

def quick_difficulty_check(text: str) -> Dict[str, Any]:
    """
    Verificación rápida de dificultad que retorna un diccionario simple

    Args:
        text: Texto a analizar

    Returns:
        Dict con métricas básicas de dificultad
    """
    calculator = DifficultyCalculator()
    assessment = calculator.calculate_difficulty(text)

    return {
        'difficulty_level': assessment.overall_difficulty.value,
        'difficulty_score': round(assessment.difficulty_score, 1),
        'target_education_level': assessment.target_education_level.value,
        'estimated_reading_time': round(assessment.estimated_reading_time, 1),
        'estimated_comprehension': round(assessment.estimated_comprehension, 1),
        'confidence_score': round(assessment.confidence_score, 2),
        'processing_time': round(assessment.processing_time, 3)
    }


def get_difficulty_level_only(text: str) -> str:
    """
    Obtener solo el nivel de dificultad del texto

    Args:
        text: Texto a analizar

    Returns:
        str: Nivel de dificultad
    """
    calculator = DifficultyCalculator()
    assessment = calculator.calculate_difficulty(text)
    return assessment.overall_difficulty.value


def analyze_for_education_level(text: str, education_level: EducationLevel) -> Dict[str, Any]:
    """
    Analizar texto para un nivel educativo específico

    Args:
        text: Texto a analizar
        education_level: Nivel educativo objetivo

    Returns:
        Dict con análisis específico para el nivel
    """
    calculator = DifficultyCalculator()
    assessment = calculator.calculate_difficulty(text, education_level)

    return {
        'is_appropriate': assessment.estimated_comprehension >= 70,
        'comprehension_level': round(assessment.estimated_comprehension, 1),
        'adaptations_needed': assessment.adaptations_needed,
        'reading_time_minutes': round(assessment.estimated_reading_time, 1),
        'difficulty_factors': {
            factor.value: round(score, 1)
            for factor, score in assessment.factor_scores.items()
        }
    }


def compare_text_difficulties(texts: List[str]) -> List[Dict[str, Any]]:
    """
    Comparar dificultades de múltiples textos

    Args:
        texts: Lista de textos a comparar

    Returns:
        Lista de evaluaciones ordenadas por dificultad
    """
    calculator = DifficultyCalculator()
    results = []

    for i, text in enumerate(texts):
        assessment = calculator.calculate_difficulty(text)
        results.append({
            'text_index': i,
            'text_preview': text[:100] + "..." if len(text) > 100 else text,
            'difficulty_level': assessment.overall_difficulty.value,
            'difficulty_score': round(assessment.difficulty_score, 1),
            'target_level': assessment.target_education_level.value,
            'estimated_reading_time': round(assessment.estimated_reading_time, 1)
        })

    # Ordenar por dificultad
    results.sort(key=lambda x: x['difficulty_score'])

    return results


# =============================================================================
# CÓDIGO DE PRUEBA
# =============================================================================

if __name__ == "__main__":
    print("🧪 Probando calculador de dificultad...")

    # Textos de prueba con diferentes niveles de dificultad
    test_texts = [
        # Texto simple
        """
        El gato subió al árbol. Era un gato negro muy bonito. 
        Le gustaba jugar en el jardín. Su dueña lo quería mucho.
        """,

        # Texto intermedio
        """
        La tecnología moderna ha transformado nuestra forma de comunicarnos. 
        Las redes sociales permiten conectar con personas de todo el mundo. 
        Sin embargo, también presentan desafíos relacionados con la privacidad 
        y la veracidad de la información que circula.
        """,

        # Texto complejo
        """
        La epistemología contemporánea aborda la problemática del conocimiento 
        desde una perspectiva multidisciplinaria que integra elementos de la 
        filosofía analítica, la fenomenología y el paradigma constructivista. 
        Esta síntesis metodológica permite una hermenéutica más comprehensiva 
        de los procesos cognitivos y metacognitivos inherentes a la 
        construcción del saber científico.
        """
    ]

    calculator = DifficultyCalculator()

    print("\n🔍 ANÁLISIS COMPARATIVO DE DIFICULTAD:")
    print("=" * 60)

    for i, text in enumerate(test_texts, 1):
        print(f"\n📄 TEXTO {i}:")
        print(f"Contenido: {text.strip()[:80]}...")

        # Análisis completo
        assessment = calculator.calculate_difficulty(text)

        print(f"🎯 Dificultad: {assessment.overall_difficulty.value}")
        print(f"📊 Puntuación: {assessment.difficulty_score:.1f}/100")
        print(f"🎓 Nivel objetivo: {assessment.target_education_level.value}")
        print(f"📚 Habilidad lectora: {assessment.target_reading_skill.value}")
        print(f"⏱️ Tiempo de lectura: {assessment.estimated_reading_time:.1f} min")
        print(f"🧠 Comprensión estimada: {assessment.estimated_comprehension:.1f}%")
        print(f"🎯 Confianza: {assessment.confidence_score:.2f}")

        print(f"\n💡 RECOMENDACIONES:")
        for rec in assessment.recommendations[:3]:  # Mostrar solo las primeras 3
            print(f"  • {rec}")

        if assessment.adaptations_needed:
            print(f"\n🔧 ADAPTACIONES SUGERIDAS:")
            for adapt in assessment.adaptations_needed[:2]:  # Mostrar solo las primeras 2
                print(f"  • {adapt}")

        print(f"\n📈 FACTORES DE COMPLEJIDAD:")
        for factor, score in assessment.factor_scores.items():
            print(f"  {factor.value.capitalize()}: {score:.1f}")

        print("-" * 60)

    # Prueba de función rápida
    print(f"\n⚡ PRUEBA DE ANÁLISIS RÁPIDO:")
    quick_result = quick_difficulty_check(test_texts[1])
    print(f"Resultado rápido: {quick_result}")

    # Comparación de textos
    print(f"\n📊 COMPARACIÓN DE TEXTOS:")
    comparison = compare_text_difficulties(test_texts)
    for result in comparison:
        print(f"Texto {result['text_index'] + 1}: {result['difficulty_level']} "
              f"({result['difficulty_score']} pts)")

    print("\n✅ Pruebas completadas exitosamente!")
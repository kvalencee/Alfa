# =============================================================================
# AlfaIA/modules/nlp/text_analyzer.py - Analizador Principal de Texto con NLP
# =============================================================================

import re
import spacy
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import statistics
from collections import Counter
import sys
from pathlib import Path

# Agregar el directorio raíz al path para imports
sys.path.append(str(Path(__file__).parent.parent.parent))

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print("🔧 Inicializando módulo de análisis de texto...")


# =============================================================================
# CONFIGURACIÓN DE SPACY
# =============================================================================

class SpacyManager:
    """Gestor del modelo de spaCy con carga lazy y fallback"""

    def __init__(self):
        self._nlp = None
        self._model_loaded = False
        self._fallback_mode = False

    def get_nlp(self):
        """Obtener instancia de spaCy con carga lazy"""
        if self._nlp is None:
            self._load_model()
        return self._nlp

    def _load_model(self):
        """Cargar modelo de spaCy con fallback"""
        try:
            print("📚 Cargando modelo de spaCy (es_core_news_sm)...")
            self._nlp = spacy.load("es_core_news_sm")
            self._model_loaded = True
            print("✅ Modelo de spaCy cargado exitosamente")
        except OSError:
            print("⚠️ Modelo es_core_news_sm no encontrado")
            try:
                print("🔄 Intentando cargar modelo básico...")
                self._nlp = spacy.blank("es")
                self._fallback_mode = True
                print("✅ Modelo básico de spaCy cargado")
            except Exception as e:
                print(f"❌ Error cargando spaCy: {e}")
                self._nlp = None
                self._fallback_mode = True

    def is_available(self) -> bool:
        """Verificar si spaCy está disponible"""
        return self._nlp is not None

    def is_fallback(self) -> bool:
        """Verificar si está en modo fallback"""
        return self._fallback_mode


# Instancia global del gestor
spacy_manager = SpacyManager()


# =============================================================================
# ENUMS Y DATACLASSES
# =============================================================================

class DifficultyLevel(Enum):
    """Niveles de dificultad del texto"""
    MUY_FACIL = "muy_facil"
    FACIL = "facil"
    INTERMEDIO = "intermedio"
    DIFICIL = "dificil"
    MUY_DIFICIL = "muy_dificil"


class TextType(Enum):
    """Tipos de texto"""
    NARRATIVO = "narrativo"
    DESCRIPTIVO = "descriptivo"
    EXPOSITIVO = "expositivo"
    ARGUMENTATIVO = "argumentativo"
    DIALOGICO = "dialogico"
    POETICO = "poetico"


@dataclass
class TextStats:
    """Estadísticas básicas del texto"""
    char_count: int
    char_count_no_spaces: int
    word_count: int
    sentence_count: int
    paragraph_count: int
    avg_words_per_sentence: float
    avg_chars_per_word: float
    unique_words: int
    lexical_diversity: float  # Unique words / Total words


@dataclass
class GrammarAnalysis:
    """Análisis gramatical del texto"""
    pos_tags: Dict[str, int]  # Conteo de etiquetas POS
    lemmas: List[str]
    entities: List[Dict[str, str]]  # Entidades nombradas
    dependency_relations: List[Dict[str, str]]
    complex_sentences: int
    simple_sentences: int


@dataclass
class VocabularyAnalysis:
    """Análisis de vocabulario"""
    common_words: List[Tuple[str, int]]  # Palabras más comunes
    rare_words: List[str]
    difficult_words: List[str]
    academic_words: List[str]
    vocabulary_level: DifficultyLevel


@dataclass
class ReadabilityMetrics:
    """Métricas de legibilidad"""
    flesch_score: float
    flesch_level: DifficultyLevel
    average_sentence_length: float
    syllable_count: int
    complex_words_ratio: float


@dataclass
class TextAnalysisResult:
    """Resultado completo del análisis de texto"""
    original_text: str
    clean_text: str
    stats: TextStats
    grammar: GrammarAnalysis
    vocabulary: VocabularyAnalysis
    readability: ReadabilityMetrics
    text_type: TextType
    overall_difficulty: DifficultyLevel
    recommendations: List[str]
    processing_time: float
    errors: List[str]


# =============================================================================
# CLASE PRINCIPAL DE ANÁLISIS
# =============================================================================

class TextAnalyzer:
    """
    Analizador principal de texto usando NLP para AlfaIA
    """

    def __init__(self):
        """Inicializar analizador"""
        self.spacy_manager = spacy_manager
        self.logger = logger

        # Palabras comunes en español (para filtrar)
        self.common_words = {
            'el', 'la', 'de', 'que', 'y', 'a', 'en', 'un', 'es', 'se',
            'no', 'te', 'lo', 'le', 'da', 'su', 'por', 'son', 'con', 'para',
            'al', 'del', 'los', 'las', 'una', 'como', 'pero', 'sus', 'me',
            'ya', 'si', 'muy', 'más', 'todo', 'todos', 'esta', 'ese', 'era'
        }

        # Palabras académicas/difíciles (ejemplos)
        self.academic_words = {
            'análisis', 'síntesis', 'paradigma', 'metodología', 'epistemología',
            'hermenéutica', 'dialéctica', 'empírico', 'conceptual', 'teórico',
            'hipótesis', 'inferencia', 'deducción', 'inducción', 'abstracción'
        }

        print("✅ TextAnalyzer inicializado")

    def analyze_text(self, text: str) -> TextAnalysisResult:
        """
        Análisis completo de texto

        Args:
            text: Texto a analizar

        Returns:
            TextAnalysisResult: Resultado completo del análisis
        """
        import time
        start_time = time.time()

        try:
            print(f"🔍 Analizando texto de {len(text)} caracteres...")

            # Limpiar texto
            clean_text = self._clean_text(text)

            # Análisis básico (siempre disponible)
            stats = self._calculate_basic_stats(clean_text)
            readability = self._calculate_readability(clean_text, stats)

            # Análisis con spaCy (si está disponible)
            if self.spacy_manager.is_available():
                grammar = self._analyze_grammar_spacy(clean_text)
                vocabulary = self._analyze_vocabulary_spacy(clean_text)
            else:
                grammar = self._analyze_grammar_fallback(clean_text)
                vocabulary = self._analyze_vocabulary_fallback(clean_text)

            # Determinar tipo de texto y dificultad
            text_type = self._classify_text_type(clean_text)
            overall_difficulty = self._calculate_overall_difficulty(
                readability, vocabulary, stats
            )

            # Generar recomendaciones
            recommendations = self._generate_recommendations(
                stats, readability, vocabulary, overall_difficulty
            )

            processing_time = time.time() - start_time

            result = TextAnalysisResult(
                original_text=text,
                clean_text=clean_text,
                stats=stats,
                grammar=grammar,
                vocabulary=vocabulary,
                readability=readability,
                text_type=text_type,
                overall_difficulty=overall_difficulty,
                recommendations=recommendations,
                processing_time=processing_time,
                errors=[]
            )

            print(f"✅ Análisis completado en {processing_time:.2f}s")
            return result

        except Exception as e:
            error_msg = f"Error en análisis de texto: {str(e)}"
            self.logger.error(error_msg)

            # Retornar resultado mínimo en caso de error
            return TextAnalysisResult(
                original_text=text,
                clean_text=text[:100] + "..." if len(text) > 100 else text,
                stats=TextStats(0, 0, 0, 0, 0, 0.0, 0.0, 0, 0.0),
                grammar=GrammarAnalysis({}, [], [], [], 0, 0),
                vocabulary=VocabularyAnalysis([], [], [], [], DifficultyLevel.INTERMEDIO),
                readability=ReadabilityMetrics(0.0, DifficultyLevel.INTERMEDIO, 0.0, 0, 0.0),
                text_type=TextType.NARRATIVO,
                overall_difficulty=DifficultyLevel.INTERMEDIO,
                recommendations=["Error en el análisis"],
                processing_time=time.time() - start_time,
                errors=[error_msg]
            )

    def _clean_text(self, text: str) -> str:
        """Limpiar y normalizar texto"""
        if not text:
            return ""

        # Eliminar caracteres de control
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x84\x86-\x9f]', '', text)

        # Normalizar espacios
        text = re.sub(r'\s+', ' ', text)

        # Eliminar espacios al inicio y final
        text = text.strip()

        return text

    def _calculate_basic_stats(self, text: str) -> TextStats:
        """Calcular estadísticas básicas del texto"""
        if not text:
            return TextStats(0, 0, 0, 0, 0, 0.0, 0.0, 0, 0.0)

        # Conteos básicos
        char_count = len(text)
        char_count_no_spaces = len(text.replace(' ', ''))

        # Palabras
        words = self._tokenize_words(text)
        word_count = len(words)

        # Oraciones
        sentences = self._split_sentences(text)
        sentence_count = len(sentences)

        # Párrafos
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        paragraph_count = len(paragraphs)

        # Promedios
        avg_words_per_sentence = word_count / sentence_count if sentence_count > 0 else 0.0
        avg_chars_per_word = char_count_no_spaces / word_count if word_count > 0 else 0.0

        # Diversidad léxica
        unique_words = len(set(word.lower() for word in words))
        lexical_diversity = unique_words / word_count if word_count > 0 else 0.0

        return TextStats(
            char_count=char_count,
            char_count_no_spaces=char_count_no_spaces,
            word_count=word_count,
            sentence_count=sentence_count,
            paragraph_count=paragraph_count,
            avg_words_per_sentence=avg_words_per_sentence,
            avg_chars_per_word=avg_chars_per_word,
            unique_words=unique_words,
            lexical_diversity=lexical_diversity
        )

    def _tokenize_words(self, text: str) -> List[str]:
        """Tokenizar texto en palabras"""
        # Regex para palabras (incluye acentos)
        words = re.findall(r'\b[a-zA-ZáéíóúüñÁÉÍÓÚÜÑ]+\b', text)
        return words

    def _split_sentences(self, text: str) -> List[str]:
        """Dividir texto en oraciones"""
        # Regex básica para oraciones
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        return sentences

    def _calculate_readability(self, text: str, stats: TextStats) -> ReadabilityMetrics:
        """Calcular métricas de legibilidad"""
        if stats.word_count == 0:
            return ReadabilityMetrics(0.0, DifficultyLevel.INTERMEDIO, 0.0, 0, 0.0)

        # Contar sílabas (aproximación)
        syllable_count = self._count_syllables(text)

        # Palabras complejas (más de 2 sílabas)
        words = self._tokenize_words(text)
        complex_words = sum(1 for word in words if self._count_word_syllables(word) > 2)
        complex_words_ratio = complex_words / len(words) if len(words) > 0 else 0.0

        # Fórmula de Flesch adaptada para español
        # Flesch = 206.835 - (1.015 * ASL) - (84.6 * ASW)
        # ASL = Average Sentence Length
        # ASW = Average Syllables per Word
        asl = stats.avg_words_per_sentence
        asw = syllable_count / stats.word_count if stats.word_count > 0 else 0.0

        flesch_score = 206.835 - (1.015 * asl) - (84.6 * asw)
        flesch_score = max(0, min(100, flesch_score))  # Clamp entre 0-100

        # Determinar nivel de dificultad basado en Flesch
        if flesch_score >= 90:
            flesch_level = DifficultyLevel.MUY_FACIL
        elif flesch_score >= 70:
            flesch_level = DifficultyLevel.FACIL
        elif flesch_score >= 50:
            flesch_level = DifficultyLevel.INTERMEDIO
        elif flesch_score >= 30:
            flesch_level = DifficultyLevel.DIFICIL
        else:
            flesch_level = DifficultyLevel.MUY_DIFICIL

        return ReadabilityMetrics(
            flesch_score=flesch_score,
            flesch_level=flesch_level,
            average_sentence_length=asl,
            syllable_count=syllable_count,
            complex_words_ratio=complex_words_ratio
        )

    def _count_syllables(self, text: str) -> int:
        """Contar sílabas en el texto completo"""
        words = self._tokenize_words(text)
        total_syllables = sum(self._count_word_syllables(word) for word in words)
        return total_syllables

    def _count_word_syllables(self, word: str) -> int:
        """Contar sílabas en una palabra (aproximación)"""
        word = word.lower()

        # Vocales en español
        vowels = 'aeiouáéíóúü'

        # Contar grupos de vocales
        syllable_count = 0
        prev_was_vowel = False

        for char in word:
            is_vowel = char in vowels
            if is_vowel and not prev_was_vowel:
                syllable_count += 1
            prev_was_vowel = is_vowel

        # Mínimo 1 sílaba por palabra
        return max(1, syllable_count)

    def _analyze_grammar_spacy(self, text: str) -> GrammarAnalysis:
        """Análisis gramatical usando spaCy"""
        try:
            nlp = self.spacy_manager.get_nlp()
            doc = nlp(text)

            # Etiquetas POS
            pos_tags = Counter(token.pos_ for token in doc if not token.is_space)

            # Lemmas
            lemmas = [token.lemma_ for token in doc if not token.is_space and not token.is_punct]

            # Entidades nombradas
            entities = [
                {"text": ent.text, "label": ent.label_, "start": ent.start_char, "end": ent.end_char}
                for ent in doc.ents
            ]

            # Relaciones de dependencia
            dependency_relations = [
                {"token": token.text, "dep": token.dep_, "head": token.head.text}
                for token in doc if not token.is_space
            ]

            # Oraciones complejas vs simples (heurística)
            sentences = list(doc.sents)
            complex_sentences = sum(1 for sent in sentences if len(sent) > 15)
            simple_sentences = len(sentences) - complex_sentences

            return GrammarAnalysis(
                pos_tags=dict(pos_tags),
                lemmas=lemmas,
                entities=entities,
                dependency_relations=dependency_relations,
                complex_sentences=complex_sentences,
                simple_sentences=simple_sentences
            )

        except Exception as e:
            self.logger.warning(f"Error en análisis gramatical con spaCy: {e}")
            return self._analyze_grammar_fallback(text)

    def _analyze_grammar_fallback(self, text: str) -> GrammarAnalysis:
        """Análisis gramatical sin spaCy (básico)"""
        words = self._tokenize_words(text)
        sentences = self._split_sentences(text)

        # Análisis muy básico
        return GrammarAnalysis(
            pos_tags={"UNKNOWN": len(words)},
            lemmas=words,
            entities=[],
            dependency_relations=[],
            complex_sentences=len([s for s in sentences if len(s.split()) > 15]),
            simple_sentences=len([s for s in sentences if len(s.split()) <= 15])
        )

    def _analyze_vocabulary_spacy(self, text: str) -> VocabularyAnalysis:
        """Análisis de vocabulario usando spaCy"""
        words = self._tokenize_words(text)
        word_counter = Counter(word.lower() for word in words)

        # Palabras más comunes (excluyendo stop words)
        common_words = [
            (word, count) for word, count in word_counter.most_common(20)
            if word not in self.common_words
        ]

        # Palabras raras (frecuencia = 1)
        rare_words = [word for word, count in word_counter.items() if count == 1]

        # Palabras difíciles (más de 8 caracteres o académicas)
        difficult_words = [
            word for word in word_counter.keys()
            if len(word) > 8 or word in self.academic_words
        ]

        # Palabras académicas encontradas
        academic_words = [word for word in word_counter.keys() if word in self.academic_words]

        # Nivel de vocabulario basado en complejidad
        vocab_level = self._calculate_vocabulary_level(
            len(difficult_words), len(academic_words), len(words)
        )

        return VocabularyAnalysis(
            common_words=common_words[:10],  # Top 10
            rare_words=rare_words[:20],  # Top 20
            difficult_words=difficult_words[:15],  # Top 15
            academic_words=academic_words,
            vocabulary_level=vocab_level
        )

    def _analyze_vocabulary_fallback(self, text: str) -> VocabularyAnalysis:
        """Análisis de vocabulario sin spaCy"""
        return self._analyze_vocabulary_spacy(text)  # El método es el mismo

    def _calculate_vocabulary_level(self, difficult_count: int, academic_count: int,
                                    total_words: int) -> DifficultyLevel:
        """Calcular nivel de vocabulario"""
        if total_words == 0:
            return DifficultyLevel.INTERMEDIO

        difficult_ratio = difficult_count / total_words
        academic_ratio = academic_count / total_words

        if academic_ratio > 0.1 or difficult_ratio > 0.3:
            return DifficultyLevel.MUY_DIFICIL
        elif academic_ratio > 0.05 or difficult_ratio > 0.2:
            return DifficultyLevel.DIFICIL
        elif difficult_ratio > 0.1:
            return DifficultyLevel.INTERMEDIO
        elif difficult_ratio > 0.05:
            return DifficultyLevel.FACIL
        else:
            return DifficultyLevel.MUY_FACIL

    def _classify_text_type(self, text: str) -> TextType:
        """Clasificar tipo de texto (heurística básica)"""
        text_lower = text.lower()

        # Indicadores de diferentes tipos de texto
        narrative_indicators = ['había', 'era', 'entonces', 'después', 'mientras', 'cuando']
        descriptive_indicators = ['es', 'está', 'tiene', 'posee', 'caracteriza', 'describe']
        expository_indicators = ['porque', 'debido', 'causa', 'consecuencia', 'explica', 'define']
        argumentative_indicators = ['opino', 'creo', 'considero', 'argumento', 'defiende', 'critica']
        dialogic_indicators = ['dijo', 'preguntó', 'respondió', '—', '"', 'conversación']
        poetic_indicators = ['verso', 'rima', 'estrofa', 'poema', 'lírica']

        # Contar indicadores
        scores = {
            TextType.NARRATIVO: sum(1 for ind in narrative_indicators if ind in text_lower),
            TextType.DESCRIPTIVO: sum(1 for ind in descriptive_indicators if ind in text_lower),
            TextType.EXPOSITIVO: sum(1 for ind in expository_indicators if ind in text_lower),
            TextType.ARGUMENTATIVO: sum(1 for ind in argumentative_indicators if ind in text_lower),
            TextType.DIALOGICO: sum(1 for ind in dialogic_indicators if ind in text_lower),
            TextType.POETICO: sum(1 for ind in poetic_indicators if ind in text_lower)
        }

        # Retornar el tipo con mayor puntuación
        return max(scores, key=scores.get)

    def _calculate_overall_difficulty(self, readability: ReadabilityMetrics,
                                      vocabulary: VocabularyAnalysis,
                                      stats: TextStats) -> DifficultyLevel:
        """Calcular dificultad general del texto"""

        # Mapear niveles a números para cálculo
        level_to_num = {
            DifficultyLevel.MUY_FACIL: 1,
            DifficultyLevel.FACIL: 2,
            DifficultyLevel.INTERMEDIO: 3,
            DifficultyLevel.DIFICIL: 4,
            DifficultyLevel.MUY_DIFICIL: 5
        }

        num_to_level = {v: k for k, v in level_to_num.items()}

        # Factores de dificultad
        readability_score = level_to_num[readability.flesch_level]
        vocabulary_score = level_to_num[vocabulary.vocabulary_level]

        # Factor de longitud de oraciones
        length_score = 1
        if stats.avg_words_per_sentence > 25:
            length_score = 5
        elif stats.avg_words_per_sentence > 20:
            length_score = 4
        elif stats.avg_words_per_sentence > 15:
            length_score = 3
        elif stats.avg_words_per_sentence > 10:
            length_score = 2

        # Promedio ponderado
        overall_score = (
                readability_score * 0.4 +
                vocabulary_score * 0.4 +
                length_score * 0.2
        )

        # Redondear y convertir de vuelta
        final_level = round(overall_score)
        final_level = max(1, min(5, final_level))  # Clamp entre 1-5

        return num_to_level[final_level]

    def _generate_recommendations(self, stats: TextStats, readability: ReadabilityMetrics,
                                  vocabulary: VocabularyAnalysis, difficulty: DifficultyLevel) -> List[str]:
        """Generar recomendaciones basadas en el análisis"""
        recommendations = []

        # Recomendaciones por longitud de oraciones
        if stats.avg_words_per_sentence > 20:
            recommendations.append("📝 Considera dividir las oraciones largas para mejorar la legibilidad.")
        elif stats.avg_words_per_sentence < 8:
            recommendations.append("📝 Podrías usar oraciones más elaboradas para enriquecer el texto.")

        # Recomendaciones por diversidad léxica
        if stats.lexical_diversity < 0.3:
            recommendations.append("🎯 Intenta usar un vocabulario más variado para evitar repeticiones.")
        elif stats.lexical_diversity > 0.8:
            recommendations.append("🎯 Excelente diversidad léxica, el texto es rico en vocabulario.")

        # Recomendaciones por legibilidad
        if readability.flesch_level == DifficultyLevel.MUY_DIFICIL:
            recommendations.append("📖 El texto es muy complejo. Considera simplificar el vocabulario y la estructura.")
        elif readability.flesch_level == DifficultyLevel.MUY_FACIL:
            recommendations.append("📖 El texto es muy simple. Podrías añadir más complejidad si es apropiado.")

        # Recomendaciones por vocabulario
        if len(vocabulary.difficult_words) > 10:
            recommendations.append("📚 Hay muchas palabras complejas. Asegúrate de que sean necesarias.")

        # Recomendación general
        if difficulty == DifficultyLevel.INTERMEDIO:
            recommendations.append("✅ El texto tiene un nivel de dificultad equilibrado y apropiado.")

        if not recommendations:
            recommendations.append("✅ El análisis no detectó áreas específicas que requieran mejoras.")

        return recommendations


# =============================================================================
# FUNCIONES DE UTILIDAD
# =============================================================================

def quick_analyze(text: str) -> Dict[str, Any]:
    """
    Análisis rápido de texto que retorna un diccionario simple

    Args:
        text: Texto a analizar

    Returns:
        Dict con métricas básicas
    """
    analyzer = TextAnalyzer()
    result = analyzer.analyze_text(text)

    return {
        'word_count': result.stats.word_count,
        'sentence_count': result.stats.sentence_count,
        'difficulty': result.overall_difficulty.value,
        'readability_score': result.readability.flesch_score,
        'lexical_diversity': result.stats.lexical_diversity,
        'text_type': result.text_type.value,
        'processing_time': result.processing_time
    }


def get_text_difficulty_only(text: str) -> str:
    """
    Obtener solo el nivel de dificultad del texto

    Args:
        text: Texto a analizar

    Returns:
        str: Nivel de dificultad
    """
    analyzer = TextAnalyzer()
    result = analyzer.analyze_text(text)
    return result.overall_difficulty.value


# =============================================================================
# CÓDIGO DE PRUEBA
# =============================================================================

if __name__ == "__main__":
    print("🧪 Probando módulo de análisis de texto...")

    # Texto de prueba
    test_text = """
    El procesamiento de lenguaje natural es una disciplina fascinante que combina 
    la lingüística computacional con la inteligencia artificial. Los algoritmos 
    modernos pueden analizar, comprender y generar texto humano de manera 
    sorprendentemente efectiva.

    Esta tecnología tiene aplicaciones en múltiples áreas: traducción automática, 
    análisis de sentimientos, chatbots inteligentes y sistemas de recomendación. 
    Sin embargo, aún existen desafíos significativos como la ambigüedad semántica 
    y el entendimiento del contexto cultural.
    """

    # Crear analizador
    analyzer = TextAnalyzer()

    # Análisis completo
    print("🔍 Realizando análisis completo...")
    result = analyzer.analyze_text(test_text)

    # Mostrar resultados
    print(f"\n📊 RESULTADOS DEL ANÁLISIS:")
    print(f"Palabras: {result.stats.word_count}")
    print(f"Oraciones: {result.stats.sentence_count}")
    print(f"Párrafos: {result.stats.paragraph_count}")
    print(f"Dificultad: {result.overall_difficulty.value}")
    print(f"Tipo de texto: {result.text_type.value}")
    print(f"Puntuación Flesch: {result.readability.flesch_score:.1f}")
    print(f"Diversidad léxica: {result.stats.lexical_diversity:.2f}")
    print(f"Tiempo de procesamiento: {result.processing_time:.3f}s")

    print(f"\n🎯 RECOMENDACIONES:")
    for rec in result.recommendations:
        print(f"  • {rec}")
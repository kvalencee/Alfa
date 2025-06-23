# =============================================================================
# AlfaIA/modules/nlp/grammar_checker.py - Corrector Gramatical y Ortográfico
# =============================================================================

import re
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import sys
from pathlib import Path

# Agregar el directorio raíz al path para imports
sys.path.append(str(Path(__file__).parent.parent.parent))

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print("🔧 Inicializando módulo de corrección gramatical...")


# =============================================================================
# CONFIGURACIÓN DE LANGUAGE TOOL
# =============================================================================

class LanguageToolManager:
    """Gestor de LanguageTool con carga lazy y fallback"""

    def __init__(self):
        self._tool = None
        self._available = None
        self._fallback_mode = False

    def get_tool(self):
        """Obtener instancia de LanguageTool con carga lazy"""
        if self._tool is None:
            self._load_tool()
        return self._tool

    def _load_tool(self):
        """Cargar LanguageTool con fallback"""
        try:
            print("📝 Cargando LanguageTool para español...")
            import language_tool_python
            self._tool = language_tool_python.LanguageTool('es')
            self._available = True
            print("✅ LanguageTool cargado exitosamente")
        except ImportError:
            print("⚠️ LanguageTool no está instalado")
            self._tool = None
            self._available = False
            self._fallback_mode = True
        except Exception as e:
            print(f"⚠️ Error cargando LanguageTool: {e}")
            self._tool = None
            self._available = False
            self._fallback_mode = True

    def is_available(self) -> bool:
        """Verificar si LanguageTool está disponible"""
        if self._available is None:
            self.get_tool()
        return self._available

    def is_fallback(self) -> bool:
        """Verificar si está en modo fallback"""
        return self._fallback_mode


# Instancia global del gestor
language_tool_manager = LanguageToolManager()


# =============================================================================
# ENUMS Y DATACLASSES
# =============================================================================

class ErrorType(Enum):
    """Tipos de errores detectados"""
    ORTOGRAFIA = "ortografia"
    GRAMATICA = "gramatica"
    PUNTUACION = "puntuacion"
    ESTILO = "estilo"
    REPETICION = "repeticion"
    ACENTUACION = "acentuacion"
    MAYUSCULAS = "mayusculas"
    CONCORDANCIA = "concordancia"
    OTRO = "otro"


class ErrorSeverity(Enum):
    """Severidad del error"""
    CRITICO = "critico"
    IMPORTANTE = "importante"
    MENOR = "menor"
    SUGERENCIA = "sugerencia"


@dataclass
class GrammarError:
    """Representación de un error gramatical"""
    text: str  # Texto del error
    start: int  # Posición inicial
    end: int  # Posición final
    error_type: ErrorType  # Tipo de error
    severity: ErrorSeverity  # Severidad
    message: str  # Mensaje explicativo
    suggestions: List[str]  # Sugerencias de corrección
    rule_id: str  # ID de la regla (si disponible)
    context: str  # Contexto del error


@dataclass
class CorrectionResult:
    """Resultado de la corrección"""
    original_text: str
    corrected_text: str
    errors: List[GrammarError]
    corrections_applied: int
    errors_remaining: int
    confidence_score: float  # 0-1, confianza en las correcciones
    processing_time: float
    tool_used: str  # "LanguageTool" o "Fallback"


# =============================================================================
# CLASE PRINCIPAL DE CORRECCIÓN
# =============================================================================

class GrammarChecker:
    """
    Corrector gramatical y ortográfico para AlfaIA
    """

    def __init__(self):
        """Inicializar corrector"""
        self.language_tool_manager = language_tool_manager
        self.logger = logger

        # Diccionario de correcciones comunes (fallback)
        self.common_corrections = {
            # Acentuación común
            'mas': 'más',
            'tu': 'tú',
            'el': 'él',
            'mi': 'mí',
            'si': 'sí',
            'te': 'té',
            'de': 'dé',
            'se': 'sé',

            # Errores ortográficos frecuentes
            'q': 'que',
            'x': 'por',
            'xq': 'porque',
            'xa': 'para',
            'bn': 'bien',
            'tmb': 'también',
            'q': 'qué',

            # Contracciones incorrectas
            'del': 'del',
            'al': 'al',
        }

        # Patrones de errores comunes (para corrección básica)
        self.correction_patterns = [
            # Espacios antes de puntuación
            (r'\s+([.,;:!?])', r'\1'),
            # Múltiples espacios
            (r'\s{2,}', ' '),
        ]

        print("✅ GrammarChecker inicializado")

    def check_text(self, text: str, auto_correct: bool = False) -> CorrectionResult:
        """
        Revisar texto en busca de errores gramaticales y ortográficos

        Args:
            text: Texto a revisar
            auto_correct: Si aplicar correcciones automáticamente

        Returns:
            CorrectionResult: Resultado de la revisión
        """
        import time
        start_time = time.time()

        try:
            print(f"📝 Revisando texto de {len(text)} caracteres...")

            if self.language_tool_manager.is_available():
                result = self._check_with_language_tool(text, auto_correct)
                tool_used = "LanguageTool"
            else:
                result = self._check_with_fallback(text, auto_correct)
                tool_used = "Fallback"

            processing_time = time.time() - start_time

            # Actualizar resultado con metadatos
            result.processing_time = processing_time
            result.tool_used = tool_used

            print(f"✅ Revisión completada en {processing_time:.2f}s")
            print(f"📊 Errores encontrados: {len(result.errors)}")

            return result

        except Exception as e:
            error_msg = f"Error en revisión gramatical: {str(e)}"
            self.logger.error(error_msg)

            return CorrectionResult(
                original_text=text,
                corrected_text=text,
                errors=[],
                corrections_applied=0,
                errors_remaining=0,
                confidence_score=0.0,
                processing_time=time.time() - start_time,
                tool_used="Error"
            )

    def _check_with_language_tool(self, text: str, auto_correct: bool) -> CorrectionResult:
        """Revisar texto usando LanguageTool"""
        tool = self.language_tool_manager.get_tool()

        # Obtener errores
        raw_errors = tool.check(text)

        # Convertir a nuestro formato
        errors = []
        for error in raw_errors:
            grammar_error = GrammarError(
                text=text[error.offset:error.offset + error.errorLength],
                start=error.offset,
                end=error.offset + error.errorLength,
                error_type=self._classify_error_type(error),
                severity=self._classify_error_severity(error),
                message=error.message,
                suggestions=error.replacements[:5],  # Máximo 5 sugerencias
                rule_id=error.ruleId,
                context=self._get_error_context(text, error.offset, error.errorLength)
            )
            errors.append(grammar_error)

        # Aplicar correcciones si se solicita
        corrected_text = text
        corrections_applied = 0

        if auto_correct:
            corrected_text = tool.correct(text)
            # Contar cuántas correcciones se aplicaron
            corrections_applied = sum(1 for error in errors if error.suggestions)

        # Calcular confianza
        confidence_score = self._calculate_confidence(errors, corrections_applied)

        return CorrectionResult(
            original_text=text,
            corrected_text=corrected_text,
            errors=errors,
            corrections_applied=corrections_applied,
            errors_remaining=len(errors) - corrections_applied,
            confidence_score=confidence_score,
            processing_time=0.0,  # Se asignará después
            tool_used=""  # Se asignará después
        )

    def _check_with_fallback(self, text: str, auto_correct: bool) -> CorrectionResult:
        """Revisar texto usando métodos fallback"""
        errors = []
        corrected_text = text
        corrections_applied = 0

        # 1. Revisar patrones básicos
        pattern_errors = self._check_basic_patterns(text)
        errors.extend(pattern_errors)

        # 2. Revisar palabras comunes
        word_errors = self._check_common_words(text)
        errors.extend(word_errors)

        # 3. Revisar acentuación básica
        accent_errors = self._check_basic_accents(text)
        errors.extend(accent_errors)

        # 4. Revisar puntuación
        punctuation_errors = self._check_punctuation(text)
        errors.extend(punctuation_errors)

        # Aplicar correcciones automáticas si se solicita
        if auto_correct:
            corrected_text, corrections_applied = self._apply_fallback_corrections(text, errors)

        # Calcular confianza (menor para fallback)
        confidence_score = self._calculate_confidence(errors, corrections_applied) * 0.7

        return CorrectionResult(
            original_text=text,
            corrected_text=corrected_text,
            errors=errors,
            corrections_applied=corrections_applied,
            errors_remaining=len(errors) - corrections_applied,
            confidence_score=confidence_score,
            processing_time=0.0,
            tool_used=""
        )

    def _classify_error_type(self, error) -> ErrorType:
        """Clasificar tipo de error basado en LanguageTool"""
        rule_id = error.ruleId.lower()
        category = error.category.lower() if hasattr(error, 'category') else ""

        if 'spell' in rule_id or 'ortograf' in rule_id:
            return ErrorType.ORTOGRAFIA
        elif 'grammar' in rule_id or 'gramat' in rule_id:
            return ErrorType.GRAMATICA
        elif 'punct' in rule_id or 'puntuac' in rule_id:
            return ErrorType.PUNTUACION
        elif 'style' in rule_id or 'estilo' in rule_id:
            return ErrorType.ESTILO
        elif 'repeat' in rule_id or 'repet' in rule_id:
            return ErrorType.REPETICION
        elif 'accent' in rule_id or 'acent' in rule_id:
            return ErrorType.ACENTUACION
        elif 'case' in rule_id or 'mayusc' in rule_id:
            return ErrorType.MAYUSCULAS
        elif 'agreement' in rule_id or 'concord' in rule_id:
            return ErrorType.CONCORDANCIA
        else:
            return ErrorType.OTRO

    def _classify_error_severity(self, error) -> ErrorSeverity:
        """Clasificar severidad del error"""
        # Heurística basada en el tipo de error
        rule_id = error.ruleId.lower()

        if any(word in rule_id for word in ['spell', 'ortograf', 'grammar']):
            return ErrorSeverity.CRITICO
        elif any(word in rule_id for word in ['punct', 'accent', 'case']):
            return ErrorSeverity.IMPORTANTE
        elif any(word in rule_id for word in ['style', 'repeat']):
            return ErrorSeverity.MENOR
        else:
            return ErrorSeverity.SUGERENCIA

    def _get_error_context(self, text: str, offset: int, length: int) -> str:
        """Obtener contexto del error"""
        start = max(0, offset - 20)
        end = min(len(text), offset + length + 20)
        context = text[start:end]

        # Marcar el error en el contexto
        error_start = offset - start
        error_end = error_start + length
        marked_context = (
                context[:error_start] +
                ">>>" + context[error_start:error_end] + "<<<" +
                context[error_end:]
        )

        return marked_context

    def _check_basic_patterns(self, text: str) -> List[GrammarError]:
        """Revisar patrones básicos de errores"""
        errors = []

        # Revisar múltiples espacios
        for match in re.finditer(r'\s{2,}', text):
            error = GrammarError(
                text=match.group(),
                start=match.start(),
                end=match.end(),
                error_type=ErrorType.ESTILO,
                severity=ErrorSeverity.MENOR,
                message="Múltiples espacios consecutivos",
                suggestions=[' '],
                rule_id="MULTIPLE_SPACES",
                context=self._get_error_context(text, match.start(), len(match.group()))
            )
            errors.append(error)

        # Revisar espacios antes de puntuación
        for match in re.finditer(r'\s+([.,;:!?])', text):
            error = GrammarError(
                text=match.group(),
                start=match.start(),
                end=match.end(),
                error_type=ErrorType.PUNTUACION,
                severity=ErrorSeverity.IMPORTANTE,
                message="Espacio innecesario antes de signo de puntuación",
                suggestions=[match.group(1)],
                rule_id="SPACE_BEFORE_PUNCT",
                context=self._get_error_context(text, match.start(), len(match.group()))
            )
            errors.append(error)

        return errors

    def _check_common_words(self, text: str) -> List[GrammarError]:
        """Revisar palabras con errores comunes"""
        errors = []
        words = re.finditer(r'\b\w+\b', text)

        for match in words:
            word = match.group().lower()
            if word in self.common_corrections:
                correction = self.common_corrections[word]
                if word != correction.lower():  # Solo si realmente es una corrección
                    error = GrammarError(
                        text=match.group(),
                        start=match.start(),
                        end=match.end(),
                        error_type=ErrorType.ORTOGRAFIA,
                        severity=ErrorSeverity.CRITICO,
                        message=f"Posible error ortográfico: '{word}' debería ser '{correction}'",
                        suggestions=[correction],
                        rule_id="COMMON_MISSPELLING",
                        context=self._get_error_context(text, match.start(), len(match.group()))
                    )
                    errors.append(error)

        return errors

    def _check_basic_accents(self, text: str) -> List[GrammarError]:
        """Revisar acentuación básica"""
        errors = []

        # Palabras que siempre deberían llevar acento
        accent_rules = {
            r'\bmas\b': ('más', "La palabra 'mas' (conjunción) debería ser 'más' (adverbio)"),
            r'\btu\b': ('tú', "El pronombre personal debería llevar acento: 'tú'"),
            r'\bel\b(?=\s+[A-Z])': ('él', "El pronombre personal debería llevar acento: 'él'"),
            r'\bsi\b(?=\s*,)': ('sí', "La afirmación debería llevar acento: 'sí'"),
        }

        for pattern, (correction, message) in accent_rules.items():
            for match in re.finditer(pattern, text):
                error = GrammarError(
                    text=match.group(),
                    start=match.start(),
                    end=match.end(),
                    error_type=ErrorType.ACENTUACION,
                    severity=ErrorSeverity.IMPORTANTE,
                    message=message,
                    suggestions=[correction],
                    rule_id="MISSING_ACCENT",
                    context=self._get_error_context(text, match.start(), len(match.group()))
                )
                errors.append(error)

        return errors

    def _check_punctuation(self, text: str) -> List[GrammarError]:
        """Revisar puntuación básica"""
        errors = []

        # Revisar doble puntuación
        for match in re.finditer(r'([.,;:!?])\1+', text):
            error = GrammarError(
                text=match.group(),
                start=match.start(),
                end=match.end(),
                error_type=ErrorType.PUNTUACION,
                severity=ErrorSeverity.IMPORTANTE,
                message="Puntuación duplicada innecesaria",
                suggestions=[match.group(1)],
                rule_id="DUPLICATE_PUNCT",
                context=self._get_error_context(text, match.start(), len(match.group()))
            )
            errors.append(error)

        return errors

    def _apply_fallback_corrections(self, text: str, errors: List[GrammarError]) -> Tuple[str, int]:
        """Aplicar correcciones usando métodos fallback"""
        corrected_text = text
        corrections_applied = 0

        # Ordenar errores por posición (de atrás hacia adelante para no afectar índices)
        sorted_errors = sorted(errors, key=lambda e: e.start, reverse=True)

        for error in sorted_errors:
            if error.suggestions and error.severity in [ErrorSeverity.CRITICO, ErrorSeverity.IMPORTANTE]:
                # Aplicar la primera sugerencia
                suggestion = error.suggestions[0]
                corrected_text = (
                        corrected_text[:error.start] +
                        suggestion +
                        corrected_text[error.end:]
                )
                corrections_applied += 1

        return corrected_text, corrections_applied

    def _calculate_confidence(self, errors: List[GrammarError], corrections_applied: int) -> float:
        """Calcular confianza en las correcciones"""
        if not errors:
            return 1.0

        # Factores de confianza
        correction_ratio = corrections_applied / len(errors) if errors else 1.0

        # Ajustar por severidad de errores
        critical_errors = sum(1 for e in errors if e.severity == ErrorSeverity.CRITICO)
        severity_factor = 1.0 - (critical_errors / len(errors) * 0.3)

        confidence = correction_ratio * severity_factor
        return max(0.0, min(1.0, confidence))

    def get_error_summary(self, errors: List[GrammarError]) -> Dict[str, Any]:
        """Obtener resumen de errores encontrados"""
        if not errors:
            return {
                'total_errors': 0,
                'by_type': {},
                'by_severity': {},
                'most_common_type': None,
                'suggestions_available': 0
            }

        # Contar por tipo
        by_type = {}
        for error in errors:
            error_type = error.error_type.value
            by_type[error_type] = by_type.get(error_type, 0) + 1

        # Contar por severidad
        by_severity = {}
        for error in errors:
            severity = error.severity.value
            by_severity[severity] = by_severity.get(severity, 0) + 1

        # Tipo más común
        most_common_type = max(by_type.items(), key=lambda x: x[1])[0] if by_type else None

        # Errores con sugerencias
        suggestions_available = sum(1 for error in errors if error.suggestions)

        return {
            'total_errors': len(errors),
            'by_type': by_type,
            'by_severity': by_severity,
            'most_common_type': most_common_type,
            'suggestions_available': suggestions_available
        }


# =============================================================================
# FUNCIONES DE UTILIDAD
# =============================================================================

def quick_check(text: str) -> Dict[str, Any]:
    """
    Revisión rápida que retorna un diccionario simple

    Args:
        text: Texto a revisar

    Returns:
        Dict con métricas básicas
    """
    checker = GrammarChecker()
    result = checker.check_text(text)

    summary = checker.get_error_summary(result.errors)

    return {
        'error_count': len(result.errors),
        'corrections_applied': result.corrections_applied,
        'confidence_score': result.confidence_score,
        'tool_used': result.tool_used,
        'most_common_error': summary['most_common_type'],
        'processing_time': result.processing_time
    }


def get_corrections_only(text: str) -> str:
    """
    Obtener solo el texto corregido

    Args:
        text: Texto a corregir

    Returns:
        str: Texto corregido
    """
    checker = GrammarChecker()
    result = checker.check_text(text, auto_correct=True)
    return result.corrected_text


# =============================================================================
# CÓDIGO DE PRUEBA
# =============================================================================

if __name__ == "__main__":
    print("🧪 Probando módulo de corrección gramatical...")

    # Texto de prueba con errores
    test_text = """
    Hola  , como estas ? Me gustaria saber si tu  vienes mañana a la 
    reunion . Es muy inportante que estes ahi porq vamos a hablar 
    de temas importantes .. Espero tu respuesta !!
    """

    # Crear corrector
    checker = GrammarChecker()

    # Revisión sin corrección automática
    print("🔍 Realizando revisión sin corrección automática...")
    result = checker.check_text(test_text, auto_correct=False)

    print(f"\n📊 RESULTADOS DE LA REVISIÓN:")
    print(f"Errores encontrados: {len(result.errors)}")
    print(f"Herramienta usada: {result.tool_used}")
    print(f"Confianza: {result.confidence_score:.2f}")
    print(f"Tiempo de procesamiento: {result.processing_time:.3f}s")

    # Mostrar errores
    if result.errors:
        print(f"\n❌ ERRORES ENCONTRADOS:")
        for i, error in enumerate(result.errors[:5], 1):  # Mostrar solo los primeros 5
            print(f"{i}. [{error.error_type.value}] '{error.text}'")
            print(f"   📝 {error.message}")
            if error.suggestions:
                print(f"   💡 Sugerencias: {', '.join(error.suggestions[:3])}")
            print()

    # Revisión con corrección automática
    print("🔧 Realizando corrección automática...")
    corrected_result = checker.check_text(test_text, auto_correct=True)

    print(f"\n✅ TEXTO CORREGIDO:")
    print(f"Original: {test_text.strip()}")
    print(f"Corregido: {corrected_result.corrected_text.strip()}")
    print(f"Correcciones aplicadas: {corrected_result.corrections_applied}")

    # Resumen de errores
    summary = checker.get_error_summary(result.errors)
    print(f"\n📈 RESUMEN:")
    print(f"Total de errores: {summary['total_errors']}")
    print(f"Tipo más común: {summary['most_common_type']}")
    print(f"Con sugerencias: {summary['suggestions_available']}")
    print(f"Por tipo: {summary['by_type']}")
    print(f"Por severidad: {summary['by_severity']}")
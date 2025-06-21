# =============================================================================
# AlfaIA/core/utils/helpers.py - Funciones Auxiliares y Utilidades
# =============================================================================

import os
import json
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union
from pathlib import Path
import logging


def setup_logging(log_level: str = "INFO", log_file: str = "alfaia.log") -> logging.Logger:
    """
    Configurar sistema de logging para AlfaIA

    Args:
        log_level: Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Archivo de log

    Returns:
        Logger configurado
    """
    # Crear directorio de logs si no existe
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # Configurar formato
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Handler para archivo
    file_handler = logging.FileHandler(log_dir / log_file, encoding='utf-8')
    file_handler.setFormatter(formatter)

    # Handler para consola
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # Configurar logger
    logger = logging.getLogger("AlfaIA")
    logger.setLevel(getattr(logging, log_level.upper()))
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


def validate_json_data(data: Any, schema: Dict[str, type]) -> bool:
    """
    Validar estructura de datos JSON contra un esquema

    Args:
        data: Datos a validar
        schema: Esquema de validación {campo: tipo}

    Returns:
        bool: True si es válido
    """
    if not isinstance(data, dict):
        return False

    for field, expected_type in schema.items():
        if field not in data:
            return False
        if not isinstance(data[field], expected_type):
            return False

    return True


def sanitize_text(text: str, max_length: int = None) -> str:
    """
    Sanitizar texto eliminando caracteres peligrosos

    Args:
        text: Texto a sanitizar
        max_length: Longitud máxima

    Returns:
        str: Texto sanitizado
    """
    if not isinstance(text, str):
        return ""

    # Eliminar caracteres de control
    sanitized = ''.join(char for char in text if ord(char) >= 32 or char in '\t\n\r')

    # Recortar espacios
    sanitized = sanitized.strip()

    # Limitar longitud si se especifica
    if max_length and len(sanitized) > max_length:
        sanitized = sanitized[:max_length]

    return sanitized


def generate_secure_token(length: int = 32) -> str:
    """
    Generar token seguro aleatorio

    Args:
        length: Longitud del token

    Returns:
        str: Token seguro
    """
    return secrets.token_urlsafe(length)


def hash_data(data: str, salt: str = None) -> str:
    """
    Crear hash SHA-256 de datos

    Args:
        data: Datos a hashear
        salt: Salt opcional

    Returns:
        str: Hash hexadecimal
    """
    if salt:
        data = f"{data}{salt}"

    return hashlib.sha256(data.encode('utf-8')).hexdigest()


def format_time_duration(seconds: int) -> str:
    """
    Formatear duración en segundos a formato legible

    Args:
        seconds: Segundos

    Returns:
        str: Duración formateada (ej: "2h 30m 15s")
    """
    if seconds < 60:
        return f"{seconds}s"

    minutes = seconds // 60
    remaining_seconds = seconds % 60

    if minutes < 60:
        if remaining_seconds > 0:
            return f"{minutes}m {remaining_seconds}s"
        return f"{minutes}m"

    hours = minutes // 60
    remaining_minutes = minutes % 60

    result = f"{hours}h"
    if remaining_minutes > 0:
        result += f" {remaining_minutes}m"
    if remaining_seconds > 0:
        result += f" {remaining_seconds}s"

    return result


def calculate_percentage(part: Union[int, float], total: Union[int, float]) -> float:
    """
    Calcular porcentaje con validación

    Args:
        part: Parte
        total: Total

    Returns:
        float: Porcentaje (0-100)
    """
    if total == 0:
        return 0.0

    percentage = (part / total) * 100
    return round(percentage, 2)


def safe_divide(numerator: Union[int, float], denominator: Union[int, float],
                default: Union[int, float] = 0) -> Union[int, float]:
    """
    División segura que evita división por cero

    Args:
        numerator: Numerador
        denominator: Denominador
        default: Valor por defecto si denominador es 0

    Returns:
        Resultado de la división o valor por defecto
    """
    if denominator == 0:
        return default

    return numerator / denominator


def clamp(value: Union[int, float], min_val: Union[int, float],
          max_val: Union[int, float]) -> Union[int, float]:
    """
    Limitar valor entre mínimo y máximo

    Args:
        value: Valor a limitar
        min_val: Valor mínimo
        max_val: Valor máximo

    Returns:
        Valor limitado
    """
    return max(min_val, min(value, max_val))


def get_file_size_human(file_path: Union[str, Path]) -> str:
    """
    Obtener tamaño de archivo en formato legible

    Args:
        file_path: Ruta del archivo

    Returns:
        str: Tamaño formateado (ej: "1.5 MB")
    """
    try:
        size_bytes = Path(file_path).stat().st_size

        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0

        return f"{size_bytes:.1f} PB"

    except (OSError, FileNotFoundError):
        return "0 B"


def ensure_directory(directory: Union[str, Path]) -> bool:
    """
    Asegurar que un directorio existe, creándolo si es necesario

    Args:
        directory: Ruta del directorio

    Returns:
        bool: True si el directorio existe o se creó exitosamente
    """
    try:
        Path(directory).mkdir(parents=True, exist_ok=True)
        return True
    except Exception:
        return False


def load_json_file(file_path: Union[str, Path], default: Any = None) -> Any:
    """
    Cargar archivo JSON de forma segura

    Args:
        file_path: Ruta del archivo JSON
        default: Valor por defecto si hay error

    Returns:
        Datos del JSON o valor por defecto
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, Exception):
        return default


def save_json_file(file_path: Union[str, Path], data: Any, indent: int = 2) -> bool:
    """
    Guardar datos en archivo JSON

    Args:
        file_path: Ruta del archivo
        data: Datos a guardar
        indent: Indentación del JSON

    Returns:
        bool: True si se guardó exitosamente
    """
    try:
        # Asegurar que el directorio padre existe
        ensure_directory(Path(file_path).parent)

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=indent)
        return True
    except Exception:
        return False


def merge_dicts(dict1: Dict, dict2: Dict, deep: bool = True) -> Dict:
    """
    Fusionar dos diccionarios

    Args:
        dict1: Primer diccionario
        dict2: Segundo diccionario (prevalece en conflictos)
        deep: Si hacer fusión profunda

    Returns:
        Dict: Diccionario fusionado
    """
    if not deep:
        result = dict1.copy()
        result.update(dict2)
        return result

    result = dict1.copy()

    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dicts(result[key], value, deep=True)
        else:
            result[key] = value

    return result


def get_timestamp(format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Obtener timestamp actual formateado

    Args:
        format_str: Formato de fecha

    Returns:
        str: Timestamp formateado
    """
    return datetime.now().strftime(format_str)


def parse_timestamp(timestamp_str: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> Optional[datetime]:
    """
    Parsear timestamp desde string

    Args:
        timestamp_str: String de timestamp
        format_str: Formato esperado

    Returns:
        datetime o None si hay error
    """
    try:
        return datetime.strptime(timestamp_str, format_str)
    except ValueError:
        return None


def is_within_time_range(target_time: datetime, start_time: datetime,
                         end_time: datetime) -> bool:
    """
    Verificar si un tiempo está dentro de un rango

    Args:
        target_time: Tiempo a verificar
        start_time: Tiempo de inicio
        end_time: Tiempo de fin

    Returns:
        bool: True si está dentro del rango
    """
    return start_time <= target_time <= end_time


def clean_filename(filename: str) -> str:
    """
    Limpiar nombre de archivo eliminando caracteres problemáticos

    Args:
        filename: Nombre de archivo original

    Returns:
        str: Nombre de archivo limpio
    """
    # Caracteres problemáticos en nombres de archivo
    invalid_chars = '<>:"/\\|?*'

    # Reemplazar caracteres inválidos con guiones bajos
    cleaned = filename
    for char in invalid_chars:
        cleaned = cleaned.replace(char, '_')

    # Eliminar espacios múltiples y reemplazar con guiones bajos
    cleaned = '_'.join(cleaned.split())

    # Limitar longitud
    if len(cleaned) > 100:
        name, ext = os.path.splitext(cleaned)
        cleaned = name[:95] + ext

    return cleaned


def retry_operation(operation, max_attempts: int = 3, delay: float = 1.0,
                    backoff_factor: float = 2.0):
    """
    Reintentar operación con backoff exponencial

    Args:
        operation: Función a ejecutar
        max_attempts: Máximo número de intentos
        delay: Delay inicial en segundos
        backoff_factor: Factor de backoff

    Returns:
        Resultado de la operación

    Raises:
        Exception: Si todos los intentos fallan
    """
    last_exception = None
    current_delay = delay

    for attempt in range(max_attempts):
        try:
            return operation()
        except Exception as e:
            last_exception = e

            if attempt < max_attempts - 1:
                import time
                time.sleep(current_delay)
                current_delay *= backoff_factor

    # Si llegamos aquí, todos los intentos fallaron
    raise last_exception


def validate_email_format(email: str) -> bool:
    """
    Validar formato básico de email

    Args:
        email: Email a validar

    Returns:
        bool: True si el formato es válido
    """
    import re

    if not email or not isinstance(email, str):
        return False

    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}
    return re.match(pattern, email.strip()) is not None


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """
    Truncar texto a longitud máxima agregando sufijo

    Args:
        text: Texto a truncar
        max_length: Longitud máxima
        suffix: Sufijo a agregar

    Returns:
        str: Texto truncado
    """
    if not text or len(text) <= max_length:
        return text

    return text[:max_length - len(suffix)] + suffix


def extract_numbers(text: str) -> List[float]:
    """
    Extraer todos los números de un texto

    Args:
        text: Texto del cual extraer números

    Returns:
        List[float]: Lista de números encontrados
    """
    import re

    if not text:
        return []

    # Patrón para números (enteros y decimales)
    pattern = r'-?\d+\.?\d*'
    matches = re.findall(pattern, text)

    numbers = []
    for match in matches:
        try:
            if '.' in match:
                numbers.append(float(match))
            else:
                numbers.append(float(int(match)))
        except ValueError:
            continue

    return numbers


def calculate_text_difficulty(text: str) -> Dict[str, Any]:
    """
    Calcular métricas básicas de dificultad de texto

    Args:
        text: Texto a analizar

    Returns:
        Dict con métricas de dificultad
    """
    if not text:
        return {
            'word_count': 0,
            'sentence_count': 0,
            'avg_words_per_sentence': 0,
            'avg_chars_per_word': 0,
            'difficulty_level': 1
        }

    import re

    # Contar palabras
    words = re.findall(r'\b\w+\b', text.lower())
    word_count = len(words)

    # Contar oraciones (aproximado)
    sentences = re.split(r'[.!?]+', text)
    sentence_count = len([s for s in sentences if s.strip()])

    # Calcular promedios
    avg_words_per_sentence = safe_divide(word_count, sentence_count, 0)
    avg_chars_per_word = safe_divide(sum(len(word) for word in words), word_count, 0)

    # Calcular nivel de dificultad básico (1-10)
    difficulty_level = 1

    if avg_words_per_sentence > 15:
        difficulty_level += 2
    elif avg_words_per_sentence > 10:
        difficulty_level += 1

    if avg_chars_per_word > 7:
        difficulty_level += 2
    elif avg_chars_per_word > 5:
        difficulty_level += 1

    if word_count > 100:
        difficulty_level += 2
    elif word_count > 50:
        difficulty_level += 1

    difficulty_level = clamp(difficulty_level, 1, 10)

    return {
        'word_count': word_count,
        'sentence_count': sentence_count,
        'avg_words_per_sentence': round(avg_words_per_sentence, 1),
        'avg_chars_per_word': round(avg_chars_per_word, 1),
        'difficulty_level': difficulty_level
    }


def generate_color_palette(base_color: str, variations: int = 5) -> List[str]:
    """
    Generar paleta de colores basada en un color base

    Args:
        base_color: Color base en formato hex (#RRGGBB)
        variations: Número de variaciones a generar

    Returns:
        List[str]: Lista de colores en formato hex
    """
    if not base_color.startswith('#') or len(base_color) != 7:
        return [base_color] * variations

    try:
        # Convertir hex a RGB
        r = int(base_color[1:3], 16)
        g = int(base_color[3:5], 16)
        b = int(base_color[5:7], 16)

        colors = []

        for i in range(variations):
            # Calcular factor de variación
            factor = 0.3 + (i * 0.4 / max(1, variations - 1))

            # Aplicar variación
            new_r = clamp(int(r * factor), 0, 255)
            new_g = clamp(int(g * factor), 0, 255)
            new_b = clamp(int(b * factor), 0, 255)

            # Convertir de vuelta a hex
            color_hex = f"#{new_r:02x}{new_g:02x}{new_b:02x}"
            colors.append(color_hex)

        return colors

    except ValueError:
        return [base_color] * variations


def format_score(score: Union[int, float], max_score: Union[int, float] = 100) -> str:
    """
    Formatear puntuación con indicador visual

    Args:
        score: Puntuación obtenida
        max_score: Puntuación máxima

    Returns:
        str: Puntuación formateada con emoji
    """
    percentage = calculate_percentage(score, max_score)

    if percentage >= 90:
        emoji = "🌟"
    elif percentage >= 80:
        emoji = "⭐"
    elif percentage >= 70:
        emoji = "👍"
    elif percentage >= 60:
        emoji = "👌"
    else:
        emoji = "💪"

    return f"{emoji} {score}/{max_score} ({percentage}%)"


def get_achievement_level(points: int) -> Dict[str, Any]:
    """
    Determinar nivel de logro basado en puntos

    Args:
        points: Puntos acumulados

    Returns:
        Dict con información del nivel
    """
    levels = [
        (0, "Principiante", "🌱"),
        (100, "Aprendiz", "📚"),
        (300, "Estudiante", "🎓"),
        (600, "Competente", "⭐"),
        (1000, "Experto", "🏆"),
        (1500, "Maestro", "👑"),
        (2500, "Leyenda", "🌟")
    ]

    current_level = levels[0]
    next_level = None

    for i, (required_points, name, icon) in enumerate(levels):
        if points >= required_points:
            current_level = (required_points, name, icon)
            if i + 1 < len(levels):
                next_level = levels[i + 1]
        else:
            break

    # Calcular progreso hacia siguiente nivel
    if next_level:
        points_needed = next_level[0] - current_level[0]
        points_progress = points - current_level[0]
        progress_percentage = calculate_percentage(points_progress, points_needed)
    else:
        progress_percentage = 100
        points_needed = 0
        points_progress = 0

    return {
        'current_level': current_level[1],
        'current_icon': current_level[2],
        'current_points': current_level[0],
        'total_points': points,
        'next_level': next_level[1] if next_level else None,
        'next_icon': next_level[2] if next_level else None,
        'points_to_next': next_level[0] - points if next_level else 0,
        'progress_percentage': progress_percentage
    }


def create_backup_filename(base_name: str, extension: str = ".bak") -> str:
    """
    Crear nombre de archivo de respaldo con timestamp

    Args:
        base_name: Nombre base del archivo
        extension: Extensión del respaldo

    Returns:
        str: Nombre del archivo de respaldo
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_clean = clean_filename(base_name)
    return f"{base_clean}_{timestamp}{extension}"


def compress_json_data(data: Any) -> str:
    """
    Comprimir datos JSON usando gzip

    Args:
        data: Datos a comprimir

    Returns:
        str: Datos comprimidos en base64
    """
    import gzip
    import base64

    try:
        json_str = json.dumps(data, ensure_ascii=False)
        compressed = gzip.compress(json_str.encode('utf-8'))
        return base64.b64encode(compressed).decode('ascii')
    except Exception:
        return ""


def decompress_json_data(compressed_data: str) -> Any:
    """
    Descomprimir datos JSON desde base64/gzip

    Args:
        compressed_data: Datos comprimidos en base64

    Returns:
        Datos descomprimidos o None si hay error
    """
    import gzip
    import base64

    try:
        compressed = base64.b64decode(compressed_data.encode('ascii'))
        decompressed = gzip.decompress(compressed)
        return json.loads(decompressed.decode('utf-8'))
    except Exception:
        return None


def validate_spanish_text(text: str) -> Dict[str, Any]:
    """
    Validaciones básicas para texto en español

    Args:
        text: Texto a validar

    Returns:
        Dict con resultados de validación
    """
    import re

    if not text:
        return {
            'is_valid': False,
            'errors': ['Texto vacío'],
            'warnings': [],
            'stats': {}
        }

    errors = []
    warnings = []

    # Verificar caracteres básicos del español
    spanish_pattern = r'^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s\d\.,;:¡!¿?\-\(\)\"\']+
    if not re.match(spanish_pattern, text):
        errors.append('Contiene caracteres no válidos para español')

    # Verificar longitud mínima y máxima
    if len(text.strip()) < 3:
        errors.append('Texto demasiado corto')
    elif len(text) > 10000:
        warnings.append('Texto muy largo')

    # Verificar espacios múltiples
    if '  ' in text:
        warnings.append('Contiene espacios múltiples')

    # Verificar puntuación básica
    if text.strip() and not re.search(r'[.!?], text.strip()):
    warnings.append('Falta puntuación final')

    # Calcular estadísticas
    words = len(re.findall(r'\b\w+\b', text))
    sentences = len(re.findall(r'[.!?]+', text))

    return {
        'is_valid': len(errors) == 0,
        'errors': errors,
        'warnings': warnings,
        'stats': {
            'characters': len(text),
            'words': words,
            'sentences': sentences
        }
    }


# =============================================================================
# DECORADORES ÚTILES
# =============================================================================

def timed_operation(func):
    """
    Decorador para medir tiempo de ejecución de funciones

    Args:
        func: Función a decorar

    Returns:
        Función decorada que mide tiempo
    """
    import functools
    import time

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            end_time = time.time()
            duration = end_time - start_time
            print(f"⏱️  {func.__name__} ejecutado en {duration:.3f}s")

    return wrapper


def safe_operation(default_return=None, log_errors=True):
    """
    Decorador para operaciones seguras que no deben fallar

    Args:
        default_return: Valor a retornar en caso de error
        log_errors: Si registrar errores en log

    Returns:
        Decorador
    """

    def decorator(func):
        import functools

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if log_errors:
                    logger = logging.getLogger("AlfaIA")
                    logger.error(f"Error en {func.__name__}: {str(e)}")
                return default_return

        return wrapper

    return decorator


# =============================================================================
# CONSTANTES ÚTILES
# =============================================================================

# Caracteres especiales del español
SPANISH_ACCENTS = {
    'a': 'á', 'e': 'é', 'i': 'í', 'o': 'ó', 'u': 'ú',
    'A': 'Á', 'E': 'É', 'I': 'Í', 'O': 'Ó', 'U': 'Ú',
    'n': 'ñ', 'N': 'Ñ', 'u': 'ü', 'U': 'Ü'
}

# Palabras comunes en español para validación
COMMON_SPANISH_WORDS = {
    'articles': ['el', 'la', 'los', 'las', 'un', 'una', 'unos', 'unas'],
    'prepositions': ['a', 'ante', 'bajo', 'con', 'de', 'desde', 'en', 'entre', 'hacia', 'hasta', 'para', 'por', 'según',
                     'sin', 'sobre', 'tras'],
    'pronouns': ['yo', 'tú', 'él', 'ella', 'nosotros', 'vosotros', 'ellos', 'ellas', 'me', 'te', 'se', 'nos', 'os']
}

# Niveles de dificultad estándar
DIFFICULTY_LEVELS = {
    1: {'name': 'Muy Fácil', 'color': '#7ED321', 'description': 'Vocabulario básico'},
    2: {'name': 'Fácil', 'color': '#8EE53F', 'description': 'Oraciones simples'},
    3: {'name': 'Principiante', 'color': '#A8F25D', 'description': 'Gramática básica'},
    4: {'name': 'Básico', 'color': '#F5A623', 'description': 'Estructuras comunes'},
    5: {'name': 'Intermedio', 'color': '#F5A623', 'description': 'Textos variados'},
    6: {'name': 'Intermedio+', 'color': '#F2884B', 'description': 'Gramática compleja'},
    7: {'name': 'Avanzado', 'color': '#F2884B', 'description': 'Textos especializados'},
    8: {'name': 'Avanzado+', 'color': '#E85D43', 'description': 'Literatura'},
    9: {'name': 'Experto', 'color': '#D0021B', 'description': 'Lenguaje académico'},
    10: {'name': 'Maestro', 'color': '#9013FE', 'description': 'Dominio completo'}
}


# =============================================================================
# FUNCIONES DE INICIALIZACIÓN
# =============================================================================

def initialize_app_directories() -> bool:
    """
    Inicializar directorios necesarios para la aplicación

    Returns:
        bool: True si se crearon correctamente
    """
    directories = [
        'logs',
        'data/cache',
        'data/exports',
        'data/backups',
        'data/temp',
        'config/user'
    ]

    success = True
    for directory in directories:
        if not ensure_directory(directory):
            success = False

    return success


def cleanup_temp_files(max_age_hours: int = 24) -> int:
    """
    Limpiar archivos temporales antiguos

    Args:
        max_age_hours: Edad máxima en horas

    Returns:
        int: Número de archivos eliminados
    """
    temp_dir = Path('data/temp')
    if not temp_dir.exists():
        return 0

    cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
    files_deleted = 0

    try:
        for file_path in temp_dir.iterdir():
            if file_path.is_file():
                file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                if file_time < cutoff_time:
                    file_path.unlink()
                    files_deleted += 1
    except Exception as e:
        logger = logging.getLogger("AlfaIA")
        logger.warning(f"Error limpiando archivos temporales: {e}")

    return files_deleted


# =============================================================================
# CÓDIGO DE PRUEBA
# =============================================================================

if __name__ == "__main__":
    # Pruebas básicas de las funciones
    print("🧪 Probando funciones auxiliares de AlfaIA")

    # Probar validación de email
    emails = ["test@example.com", "invalid-email", "user@domain.co"]
    for email in emails:
        print(f"Email '{email}': {validate_email_format(email)}")

    # Probar análisis de dificultad de texto
    texto = "Este es un texto de ejemplo para probar la función de análisis de dificultad."
    difficulty = calculate_text_difficulty(texto)
    print(f"Dificultad del texto: {difficulty}")

    # Probar formateo de tiempo
    print(f"Tiempo: {format_time_duration(3661)}")  # 1h 1m 1s

    # Probar nivel de logro
    achievement = get_achievement_level(750)
    print(f"Logro: {achievement['current_level']} {achievement['current_icon']}")

    print("✅ Pruebas completadas")
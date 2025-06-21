# =============================================================================
# AlfaIA/config/nlp_config.py - Configuración de NLP
# =============================================================================

import os
from pathlib import Path


class NLPConfig:
    """Configuración de procesamiento de lenguaje natural"""

    # Modelos de spaCy
    SPACY_MODELS = {
        "small": "es_core_news_sm",  # Modelo pequeño (rápido)
        "medium": "es_core_news_md",  # Modelo mediano (balance)
        "large": "es_core_news_lg"  # Modelo grande (preciso)
    }

    # Modelo por defecto
    DEFAULT_SPACY_MODEL = SPACY_MODELS["small"]

    # Configuración de Language Tool
    LANGUAGE_TOOL_CONFIG = {
        "language": "es",
        "server_url": None,  # None para usar local
        "timeout": 30,
        "strictness": "medium"  # low|medium|high
    }

    # Configuración NLTK
    NLTK_CONFIG = {
        "data_path": Path(__file__).parent.parent / "data" / "nltk_data",
        "required_packages": [
            "punkt",
            "stopwords",
            "wordnet",
            "averaged_perceptron_tagger",
            "omw-1.4"
        ]
    }

    # Configuración de análisis NLP
    ANALYSIS_CONFIG = {
        "pos_tagging": True,
        "lemmatization": True,
        "dependency_parsing": True,
        "named_entity_recognition": True,
        "sentiment_analysis": False,  # Opcional para textos educativos
        "similarity_analysis": True
    }

    # Configuración de cache
    CACHE_CONFIG = {
        "enable_cache": True,
        "cache_size_mb": 128,
        "cache_ttl_hours": 24,
        "cache_path": Path(__file__).parent.parent / "data" / "nlp_cache"
    }

    # Configuración de transformers (Hugging Face)
    TRANSFORMERS_CONFIG = {
        "model_name": "dccuchile/bert-base-spanish-wwm-uncased",
        "cache_dir": Path(__file__).parent.parent / "data" / "transformers_cache",
        "device": "cpu",  # cpu|cuda
        "max_length": 512
    }

    # Configuración de dificultad de texto
    DIFFICULTY_CONFIG = {
        "levels": {
            1: {"min_words": 5, "max_words": 15, "complexity": "very_easy"},
            2: {"min_words": 10, "max_words": 25, "complexity": "easy"},
            3: {"min_words": 20, "max_words": 40, "complexity": "easy_medium"},
            4: {"min_words": 30, "max_words": 60, "complexity": "medium"},
            5: {"min_words": 50, "max_words": 80, "complexity": "medium"},
            6: {"min_words": 60, "max_words": 100, "complexity": "medium_hard"},
            7: {"min_words": 80, "max_words": 120, "complexity": "hard"},
            8: {"min_words": 100, "max_words": 150, "complexity": "hard"},
            9: {"min_words": 120, "max_words": 200, "complexity": "very_hard"},
            10: {"min_words": 150, "max_words": 300, "complexity": "expert"}
        }
    }

    # Patrones de errores comunes en español
    ERROR_PATTERNS = {
        "concordancia_genero": [
            r"(la|una) \w*[aeiou]o\b",  # la/una + palabra terminada en o
            r"(el|un) \w*[aeiou]a\b"  # el/un + palabra terminada en a
        ],
        "concordancia_numero": [
            r"(los|las|unos|unas) \w*[^s]\b",  # plural + singular
            r"(el|la|un|una) \w*s\b"  # singular + plural
        ],
        "tildes_comunes": [
            r"\b(mi|tu|si|se|te|de|mas)\b",  # Palabras que pueden llevar tilde
            r"\b(que|como|cuando|donde)\b"  # Interrogativos sin tilde
        ]
    }

    @classmethod
    def get_model_path(cls, model_type: str = "default") -> str:
        """Retorna la ruta del modelo especificado"""
        if model_type == "default":
            return cls.DEFAULT_SPACY_MODEL
        return cls.SPACY_MODELS.get(model_type, cls.DEFAULT_SPACY_MODEL)

    @classmethod
    def get_difficulty_config(cls, level: int) -> dict:
        """Retorna configuración de dificultad para un nivel específico"""
        return cls.DIFFICULTY_CONFIG["levels"].get(level, cls.DIFFICULTY_CONFIG["levels"][1])
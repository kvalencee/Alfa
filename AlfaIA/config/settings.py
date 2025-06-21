# =============================================================================
# AlfaIA/config/settings.py - Configuración General de la Aplicación
# =============================================================================

import os
from pathlib import Path


class Settings:
    """Configuración general de AlfaIA"""

    # Información de la aplicación
    APP_NAME = "AlfaIA"
    APP_VERSION = "1.0.0"
    APP_DESCRIPTION = "Aplicación Educativa de Escritorio con PyQt6"

    # Directorios
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / "data"
    MODELS_DIR = DATA_DIR / "models"
    CONTENT_DIR = DATA_DIR / "content"
    EXPORTS_DIR = DATA_DIR / "exports"
    RESOURCES_DIR = BASE_DIR / "ui" / "resources"

    # Configuración de apariencia
    APPEARANCE = {
        "theme": "light",  # light|dark|auto
        "font_size": 16,  # Tamaño base de fuente
        "animation_speed": "normal"  # slow|normal|fast
    }

    # Colores de la aplicación (según especificaciones)
    COLORS = {
        # Colores principales
        "blue_educational": "#4A90E2",
        "green_success": "#7ED321",
        "orange_energetic": "#F5A623",
        "purple_creative": "#9013FE",

        # Colores secundarios
        "blue_light": "#E8F4FD",
        "green_mint": "#E8F8F0",
        "peach_soft": "#FFF2E8",
        "lavender": "#F3E8FF",

        # Colores de estado
        "red_soft": "#FF6B6B",
        "yellow_warm": "#FFD93D",
        "gray_neutral": "#8E9AAF",
        "white_pure": "#FFFFFF",

        # Colores de texto
        "text_primary": "#2C3E50",
        "text_secondary": "#7F8C8D",
        "text_emphasis": "#E74C3C"
    }

    # Configuración de aprendizaje
    LEARNING = {
        "daily_goal_exercises": 5,
        "difficulty_auto_adjust": True,
        "nlp_analysis_level": "basic",  # basic|advanced
        "error_feedback_detail": "detailed"  # simple|detailed
    }

    # Configuración de rendimiento
    PERFORMANCE = {
        "max_concurrent_analysis": 5,
        "nlp_timeout_seconds": 30,
        "cache_analysis_results": True,
        "cache_size_mb": 256
    }

    # Tiempos de respuesta objetivo (en segundos)
    RESPONSE_TIMES = {
        "exercise_load": 2.0,
        "nlp_basic_analysis": 1.0,
        "nlp_complex_analysis": 5.0,
        "exercise_generation": 3.0,
        "response_validation": 0.5
    }
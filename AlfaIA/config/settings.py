# =============================================================================
# AlfaIA/config/settings.py - Configuración Actualizada y Mejorada
# =============================================================================

import os
from pathlib import Path


class Settings:
    """Configuración general de AlfaIA con colores corregidos y mejorados"""

    # Información de la aplicación
    APP_NAME = "AlfaIA"
    APP_VERSION = "1.0.0"
    APP_DESCRIPTION = "Aplicación Educativa de Escritorio con PyQt6 y NLP"

    # Directorios
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / "data"
    MODELS_DIR = DATA_DIR / "models"
    CONTENT_DIR = DATA_DIR / "content"
    EXPORTS_DIR = DATA_DIR / "exports"
    CACHE_DIR = DATA_DIR / "cache"
    LOGS_DIR = BASE_DIR / "logs"
    RESOURCES_DIR = BASE_DIR / "ui" / "resources"

    # =============================================================================
    # COLORES CORREGIDOS Y MEJORADOS
    # =============================================================================

    COLORS = {
        # COLORES PRINCIPALES - Alta legibilidad
        "blue_educational": "#4A90E2",  # Azul educativo principal
        "green_success": "#22C55E",  # Verde éxito (más vibrante)
        "orange_energetic": "#F59E0B",  # Naranja energético (mejor contraste)
        "purple_creative": "#8B5CF6",  # Púrpura creativo (mejor legibilidad)

        # COLORES SECUNDARIOS - Fondos suaves
        "blue_light": "#EFF6FF",  # Azul claro para fondos
        "green_light": "#F0FDF4",  # Verde claro para fondos
        "orange_light": "#FFFBEB",  # Naranja claro para fondos
        "purple_light": "#F3E8FF",  # Púrpura claro para fondos

        # COLORES DE TEXTO - Máximo contraste
        "text_primary": "#1F2937",  # Texto principal (casi negro)
        "text_secondary": "#6B7280",  # Texto secundario (gris medio)
        "text_muted": "#9CA3AF",  # Texto deshabilitado (gris claro)
        "text_emphasis": "#DC2626",  # Texto de énfasis (rojo)
        "text_success": "#059669",  # Texto de éxito (verde oscuro)
        "text_warning": "#D97706",  # Texto de advertencia (naranja oscuro)

        # COLORES DE FONDO - Jerarquía visual clara
        "background_primary": "#FFFFFF",  # Fondo principal (blanco puro)
        "background_secondary": "#F9FAFB",  # Fondo secundario (gris muy claro)
        "background_tertiary": "#F3F4F6",  # Fondo terciario (gris claro)
        "background_accent": "#F8FAFC",  # Fondo con acento

        # COLORES DE BORDES - Sutiles pero definidos
        "border_light": "#E5E7EB",  # Borde claro
        "border_medium": "#D1D5DB",  # Borde medio
        "border_dark": "#9CA3AF",  # Borde oscuro
        "border_accent": "#4A90E2",  # Borde con acento

        # COLORES DE ESTADO - Sistema de feedback claro
        "success": "#10B981",  # Verde éxito
        "warning": "#F59E0B",  # Amarillo advertencia
        "error": "#EF4444",  # Rojo error
        "info": "#3B82F6",  # Azul información

        # COLORES DE ESTADO SUAVES
        "success_light": "#D1FAE5",  # Verde éxito suave
        "warning_light": "#FEF3C7",  # Amarillo advertencia suave
        "error_light": "#FEE2E2",  # Rojo error suave
        "info_light": "#DBEAFE",  # Azul información suave

        # COLORES ESPECIALES - Para elementos específicos
        "white_pure": "#FFFFFF",  # Blanco puro
        "black_pure": "#000000",  # Negro puro
        "gray_neutral": "#6B7280",  # Gris neutro
        "shadow": "rgba(0, 0, 0, 0.1)",  # Sombra estándar
        "shadow_dark": "rgba(0, 0, 0, 0.25)",  # Sombra oscura

        # COLORES DE GRADIENTES
        "gradient_blue": "qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 #4A90E2, stop: 1 #5BA3F5)",
        "gradient_green": "qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 #22C55E, stop: 1 #34D399)",
        "gradient_purple": "qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 #8B5CF6, stop: 1 #A78BFA)",
        "gradient_sunset": "qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 #4A90E2, stop: 0.5 #8B5CF6, stop: 1 #F59E0B)",

        # COLORES POR CONTEXTO DE USO
        "sidebar_bg": "#F8FAFC",
        "sidebar_item": "#1F2937",
        "sidebar_item_hover": "#4A90E2",
        "sidebar_item_active": "#FFFFFF",

        "card_bg": "#FFFFFF",
        "card_border": "#E5E7EB",
        "card_shadow": "rgba(0, 0, 0, 0.05)",

        "button_primary": "#4A90E2",
        "button_primary_hover": "#3B82D4",
        "button_primary_text": "#FFFFFF",

        "button_secondary": "#F3F4F6",
        "button_secondary_hover": "#E5E7EB",
        "button_secondary_text": "#374151",

        "input_bg": "#FFFFFF",
        "input_border": "#D1D5DB",
        "input_border_focus": "#4A90E2",
        "input_text": "#1F2937",
        "input_placeholder": "#9CA3AF"
    }

    # =============================================================================
    # PALETAS TEMÁTICAS POR SECCIÓN
    # =============================================================================

    SECTION_THEMES = {
        "dashboard": {
            "primary": COLORS["blue_educational"],
            "secondary": COLORS["green_success"],
            "background": COLORS["blue_light"],
            "text": COLORS["text_primary"]
        },
        "exercises": {
            "primary": COLORS["blue_educational"],
            "secondary": COLORS["orange_energetic"],
            "background": COLORS["background_primary"],
            "text": COLORS["text_primary"]
        },
        "games": {
            "primary": COLORS["purple_creative"],
            "secondary": COLORS["orange_energetic"],
            "background": COLORS["purple_light"],
            "text": COLORS["text_primary"]
        },
        "progress": {
            "primary": COLORS["green_success"],
            "secondary": COLORS["blue_educational"],
            "background": COLORS["green_light"],
            "text": COLORS["text_primary"]
        },
        "profile": {
            "primary": COLORS["gray_neutral"],
            "secondary": COLORS["blue_educational"],
            "background": COLORS["background_secondary"],
            "text": COLORS["text_primary"]
        },
        "settings": {
            "primary": COLORS["gray_neutral"],
            "secondary": COLORS["purple_creative"],
            "background": COLORS["background_tertiary"],
            "text": COLORS["text_primary"]
        }
    }

    # =============================================================================
    # CONFIGURACIÓN DE APARIENCIA
    # =============================================================================

    APPEARANCE = {
        "theme": "light",  # light|dark|auto
        "font_family_primary": "'Segoe UI', 'Inter', 'Roboto', sans-serif",
        "font_family_heading": "'Poppins', 'Montserrat', sans-serif",
        "font_size_small": 12,
        "font_size_normal": 14,
        "font_size_medium": 16,
        "font_size_large": 18,
        "font_size_xl": 24,
        "font_size_xxl": 32,
        "animation_speed": "normal",  # slow|normal|fast
        "border_radius_small": 6,
        "border_radius_medium": 12,
        "border_radius_large": 16,
        "shadow_small": "0 1px 3px rgba(0,0,0,0.1)",
        "shadow_medium": "0 4px 6px rgba(0,0,0,0.1)",
        "shadow_large": "0 10px 25px rgba(0,0,0,0.1)"
    }

    # =============================================================================
    # CONFIGURACIÓN DE APRENDIZAJE
    # =============================================================================

    LEARNING = {
        "daily_goal_exercises": 5,
        "difficulty_auto_adjust": True,
        "nlp_analysis_level": "basic",  # basic|advanced
        "error_feedback_detail": "detailed",  # simple|detailed
        "show_progress_animations": True,
        "enable_achievements": True,
        "streak_reminder": True
    }

    # =============================================================================
    # CONFIGURACIÓN DE RENDIMIENTO
    # =============================================================================

    PERFORMANCE = {
        "max_concurrent_analysis": 5,
        "nlp_timeout_seconds": 30,
        "cache_analysis_results": True,
        "cache_size_mb": 256,
        "auto_save_interval_seconds": 300,
        "database_connection_pool_size": 10,
        "ui_refresh_rate_ms": 100
    }

    # =============================================================================
    # TIEMPOS DE RESPUESTA OBJETIVO
    # =============================================================================

    RESPONSE_TIMES = {
        "exercise_load": 2.0,
        "nlp_basic_analysis": 1.0,
        "nlp_complex_analysis": 5.0,
        "exercise_generation": 3.0,
        "response_validation": 0.5,
        "dashboard_refresh": 1.0,
        "user_data_load": 2.0
    }

    # =============================================================================
    # CONFIGURACIÓN DE UI/UX
    # =============================================================================

    UI_CONFIG = {
        "window_min_width": 1200,
        "window_min_height": 800,
        "sidebar_width": 280,
        "header_height": 60,
        "footer_height": 30,
        "content_padding": 40,
        "card_spacing": 20,
        "animation_duration_ms": 200,
        "tooltip_delay_ms": 500,
        "notification_duration_ms": 3000
    }

    # =============================================================================
    # CONFIGURACIÓN DE ACCESIBILIDAD
    # =============================================================================

    ACCESSIBILITY = {
        "high_contrast_mode": False,
        "large_fonts": False,
        "screen_reader_support": True,
        "keyboard_navigation": True,
        "focus_indicators": True,
        "color_blind_friendly": True,
        "minimum_contrast_ratio": 4.5
    }

    # =============================================================================
    # ESTILOS CSS PRECONFIGURADOS
    # =============================================================================

    @classmethod
    def get_global_stylesheet(cls):
        """Obtener hoja de estilos global para la aplicación"""
        return f"""
            /* Estilos globales base */
            QApplication {{
                font-family: {cls.APPEARANCE['font_family_primary']};
                font-size: {cls.APPEARANCE['font_size_normal']}px;
                color: {cls.COLORS['text_primary']};
                background-color: {cls.COLORS['background_primary']};
            }}

            /* Ventanas principales */
            QMainWindow {{
                background-color: {cls.COLORS['background_primary']};
                color: {cls.COLORS['text_primary']};
            }}

            /* Widgets base */
            QWidget {{
                background-color: transparent;
                color: {cls.COLORS['text_primary']};
                font-family: {cls.APPEARANCE['font_family_primary']};
            }}

            /* Etiquetas */
            QLabel {{
                color: {cls.COLORS['text_primary']};
                background-color: transparent;
                border: none;
            }}

            /* Botones principales */
            QPushButton {{
                background-color: {cls.COLORS['button_primary']};
                color: {cls.COLORS['button_primary_text']};
                border: none;
                border-radius: {cls.APPEARANCE['border_radius_medium']}px;
                padding: 12px 20px;
                font-size: {cls.APPEARANCE['font_size_medium']}px;
                font-weight: 600;
                font-family: {cls.APPEARANCE['font_family_primary']};
            }}

            QPushButton:hover {{
                background-color: {cls.COLORS['button_primary_hover']};
            }}

            QPushButton:pressed {{
                background-color: {cls.COLORS['button_primary_hover']};
                transform: translateY(1px);
            }}

            QPushButton:disabled {{
                background-color: {cls.COLORS['text_muted']};
                color: {cls.COLORS['background_primary']};
            }}

            /* Botones secundarios */
            QPushButton[buttonType="secondary"] {{
                background-color: {cls.COLORS['button_secondary']};
                color: {cls.COLORS['button_secondary_text']};
                border: 2px solid {cls.COLORS['border_medium']};
            }}

            QPushButton[buttonType="secondary"]:hover {{
                background-color: {cls.COLORS['button_secondary_hover']};
                border-color: {cls.COLORS['border_accent']};
            }}

            /* Campos de entrada */
            QLineEdit {{
                background-color: {cls.COLORS['input_bg']};
                color: {cls.COLORS['input_text']};
                border: 2px solid {cls.COLORS['input_border']};
                border-radius: {cls.APPEARANCE['border_radius_medium']}px;
                padding: 12px 16px;
                font-size: {cls.APPEARANCE['font_size_medium']}px;
                font-family: {cls.APPEARANCE['font_family_primary']};
            }}

            QLineEdit:focus {{
                border-color: {cls.COLORS['input_border_focus']};
                box-shadow: 0 0 0 3px {cls.COLORS['input_border_focus']}20;
            }}

            QLineEdit::placeholder {{
                color: {cls.COLORS['input_placeholder']};
            }}

            /* ComboBox */
            QComboBox {{
                background-color: {cls.COLORS['input_bg']};
                color: {cls.COLORS['input_text']};
                border: 2px solid {cls.COLORS['input_border']};
                border-radius: {cls.APPEARANCE['border_radius_medium']}px;
                padding: 12px 16px;
                font-size: {cls.APPEARANCE['font_size_medium']}px;
                min-width: 120px;
            }}

            QComboBox:focus {{
                border-color: {cls.COLORS['input_border_focus']};
            }}

            QComboBox::drop-down {{
                border: none;
                background-color: {cls.COLORS['button_primary']};
                border-radius: {cls.APPEARANCE['border_radius_small']}px;
                margin: 4px;
                width: 30px;
            }}

            QComboBox QAbstractItemView {{
                background-color: {cls.COLORS['background_primary']};
                border: 1px solid {cls.COLORS['border_light']};
                border-radius: {cls.APPEARANCE['border_radius_medium']}px;
                selection-background-color: {cls.COLORS['button_primary']};
                selection-color: {cls.COLORS['button_primary_text']};
                padding: 4px;
            }}

            /* Barras de scroll */
            QScrollBar:vertical {{
                background-color: {cls.COLORS['background_secondary']};
                width: 12px;
                border-radius: 6px;
                margin: 0;
            }}

            QScrollBar::handle:vertical {{
                background-color: {cls.COLORS['border_medium']};
                border-radius: 6px;
                min-height: 20px;
                margin: 2px;
            }}

            QScrollBar::handle:vertical:hover {{
                background-color: {cls.COLORS['button_primary']};
            }}

            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                border: none;
                background: none;
                height: 0px;
            }}

            QScrollBar:horizontal {{
                background-color: {cls.COLORS['background_secondary']};
                height: 12px;
                border-radius: 6px;
                margin: 0;
            }}

            QScrollBar::handle:horizontal {{
                background-color: {cls.COLORS['border_medium']};
                border-radius: 6px;
                min-width: 20px;
                margin: 2px;
            }}

            QScrollBar::handle:horizontal:hover {{
                background-color: {cls.COLORS['button_primary']};
            }}

            /* Frames y contenedores */
            QFrame {{
                background-color: transparent;
                border: none;
            }}

            QFrame[frameType="card"] {{
                background-color: {cls.COLORS['card_bg']};
                border: 1px solid {cls.COLORS['card_border']};
                border-radius: {cls.APPEARANCE['border_radius_large']}px;
            }}

            /* Menús */
            QMenuBar {{
                background-color: {cls.COLORS['background_primary']};
                color: {cls.COLORS['text_primary']};
                border-bottom: 1px solid {cls.COLORS['border_light']};
                padding: 4px 8px;
                font-size: {cls.APPEARANCE['font_size_normal']}px;
            }}

            QMenuBar::item {{
                background-color: transparent;
                padding: 8px 12px;
                border-radius: {cls.APPEARANCE['border_radius_small']}px;
            }}

            QMenuBar::item:selected {{
                background-color: {cls.COLORS['button_primary']}15;
                color: {cls.COLORS['button_primary']};
            }}

            QMenu {{
                background-color: {cls.COLORS['background_primary']};
                border: 1px solid {cls.COLORS['border_light']};
                border-radius: {cls.APPEARANCE['border_radius_medium']}px;
                padding: 8px 4px;
            }}

            QMenu::item {{
                padding: 8px 16px;
                border-radius: {cls.APPEARANCE['border_radius_small']}px;
                margin: 2px;
            }}

            QMenu::item:selected {{
                background-color: {cls.COLORS['button_primary']};
                color: {cls.COLORS['button_primary_text']};
            }}

            /* Barras de herramientas */
            QToolBar {{
                background-color: {cls.COLORS['background_primary']};
                border: none;
                border-bottom: 1px solid {cls.COLORS['border_light']};
                padding: 8px;
                spacing: 8px;
            }}

            QToolButton {{
                background-color: transparent;
                border: none;
                border-radius: {cls.APPEARANCE['border_radius_medium']}px;
                padding: 8px 12px;
                font-size: {cls.APPEARANCE['font_size_normal']}px;
                color: {cls.COLORS['text_primary']};
            }}

            QToolButton:hover {{
                background-color: {cls.COLORS['button_primary']}15;
                color: {cls.COLORS['button_primary']};
            }}

            /* Barra de estado */
            QStatusBar {{
                background-color: {cls.COLORS['background_primary']};
                color: {cls.COLORS['text_secondary']};
                border-top: 1px solid {cls.COLORS['border_light']};
                padding: 4px 8px;
                font-size: {cls.APPEARANCE['font_size_small']}px;
            }}

            /* Tooltips */
            QToolTip {{
                background-color: {cls.COLORS['text_primary']};
                color: {cls.COLORS['background_primary']};
                border: none;
                border-radius: {cls.APPEARANCE['border_radius_small']}px;
                padding: 8px 12px;
                font-size: {cls.APPEARANCE['font_size_small']}px;
            }}

            /* Diálogos */
            QDialog {{
                background-color: {cls.COLORS['background_primary']};
                color: {cls.COLORS['text_primary']};
            }}

            QMessageBox {{
                background-color: {cls.COLORS['background_primary']};
                color: {cls.COLORS['text_primary']};
                font-size: {cls.APPEARANCE['font_size_normal']}px;
                min-width: 350px;
            }}

            QMessageBox QPushButton {{
                min-width: 80px;
                padding: 8px 16px;
            }}

            /* Barras de progreso */
            QProgressBar {{
                background-color: {cls.COLORS['background_secondary']};
                border: none;
                border-radius: {cls.APPEARANCE['border_radius_small']}px;
                text-align: center;
                font-weight: 600;
            }}

            QProgressBar::chunk {{
                background-color: {cls.COLORS['button_primary']};
                border-radius: {cls.APPEARANCE['border_radius_small']}px;
            }}

            /* Checkboxes */
            QCheckBox {{
                color: {cls.COLORS['text_primary']};
                font-size: {cls.APPEARANCE['font_size_normal']}px;
                spacing: 8px;
            }}

            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border: 2px solid {cls.COLORS['border_medium']};
                border-radius: 4px;
                background-color: {cls.COLORS['background_primary']};
            }}

            QCheckBox::indicator:checked {{
                background-color: {cls.COLORS['button_primary']};
                border-color: {cls.COLORS['button_primary']};
            }}

            /* Radio buttons */
            QRadioButton {{
                color: {cls.COLORS['text_primary']};
                font-size: {cls.APPEARANCE['font_size_normal']}px;
                spacing: 8px;
            }}

            QRadioButton::indicator {{
                width: 18px;
                height: 18px;
                border: 2px solid {cls.COLORS['border_medium']};
                border-radius: 9px;
                background-color: {cls.COLORS['background_primary']};
            }}

            QRadioButton::indicator:checked {{
                background-color: {cls.COLORS['button_primary']};
                border-color: {cls.COLORS['button_primary']};
            }}
        """

    @classmethod
    def get_card_style(cls, color_accent=None):
        """Obtener estilo para tarjetas/cards"""
        accent = color_accent or cls.COLORS['button_primary']
        return f"""
            QFrame {{
                background-color: {cls.COLORS['card_bg']};
                border: 1px solid {cls.COLORS['card_border']};
                border-radius: {cls.APPEARANCE['border_radius_large']}px;
                padding: 0px;
            }}
            QFrame:hover {{
                border-color: {accent}40;
                background-color: {cls.COLORS['background_secondary']};
            }}
        """

    @classmethod
    def get_sidebar_style(cls):
        """Obtener estilo para la barra lateral"""
        return f"""
            QTreeWidget {{
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 {cls.COLORS['sidebar_bg']},
                    stop: 0.5 #f1f5f9,
                    stop: 1 #e2e8f0
                );
                border: none;
                border-right: 1px solid {cls.COLORS['border_light']};
                font-family: {cls.APPEARANCE['font_family_primary']};
                outline: none;
            }}

            QTreeWidget::item {{
                padding: 16px 20px;
                border: none;
                margin: 6px 12px;
                border-radius: {cls.APPEARANCE['border_radius_medium']}px;
                background-color: transparent;
                font-weight: 500;
                font-size: {cls.APPEARANCE['font_size_medium']}px;
                color: {cls.COLORS['sidebar_item']};
                min-height: 20px;
            }}

            QTreeWidget::item:selected {{
                background: {cls.COLORS['gradient_blue']};
                color: {cls.COLORS['sidebar_item_active']};
                border: none;
                font-weight: 600;
            }}

            QTreeWidget::item:hover:!selected {{
                background-color: {cls.COLORS['sidebar_item_hover']}15;
                color: {cls.COLORS['sidebar_item_hover']};
                border: 1px solid {cls.COLORS['sidebar_item_hover']}30;
            }}
        """

    @classmethod
    def get_button_style(cls, color=None, style_type="primary"):
        """Obtener estilo para botones personalizados"""
        if style_type == "primary":
            bg_color = color or cls.COLORS['button_primary']
            text_color = cls.COLORS['button_primary_text']
            hover_color = f"{bg_color}CC"
        else:  # secondary
            bg_color = cls.COLORS['button_secondary']
            text_color = cls.COLORS['button_secondary_text']
            hover_color = cls.COLORS['button_secondary_hover']

        return f"""
            QPushButton {{
                background-color: {bg_color};
                color: {text_color};
                border: {'none' if style_type == 'primary' else f'2px solid {cls.COLORS["border_medium"]}'};
                border-radius: {cls.APPEARANCE['border_radius_medium']}px;
                padding: 12px 20px;
                font-size: {cls.APPEARANCE['font_size_medium']}px;
                font-weight: 600;
                font-family: {cls.APPEARANCE['font_family_primary']};
            }}
            QPushButton:hover {{
                background-color: {hover_color};
                {'border-color: ' + (color or cls.COLORS['button_primary']) if style_type == 'secondary' else ''};
            }}
            QPushButton:pressed {{
                background-color: {hover_color};
            }}
            QPushButton:disabled {{
                background-color: {cls.COLORS['text_muted']};
                color: {cls.COLORS['background_primary']};
                border-color: {cls.COLORS['text_muted']};
            }}
        """

    # =============================================================================
    # MÉTODOS DE UTILIDAD
    # =============================================================================

    @classmethod
    def get_theme_color(cls, section, element="primary"):
        """Obtener color temático de una sección específica"""
        if section in cls.SECTION_THEMES:
            return cls.SECTION_THEMES[section].get(element, cls.COLORS['button_primary'])
        return cls.COLORS['button_primary']

    @classmethod
    def create_gradient(cls, color1, color2, direction="horizontal"):
        """Crear gradiente CSS"""
        if direction == "horizontal":
            return f"qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 {color1}, stop: 1 {color2})"
        else:  # vertical
            return f"qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 {color1}, stop: 1 {color2})"

    @classmethod
    def get_status_color(cls, status):
        """Obtener color según estado"""
        status_colors = {
            'success': cls.COLORS['success'],
            'warning': cls.COLORS['warning'],
            'error': cls.COLORS['error'],
            'info': cls.COLORS['info'],
            'default': cls.COLORS['button_primary']
        }
        return status_colors.get(status, status_colors['default'])

    @classmethod
    def validate_color(cls, color):
        """Validar formato de color"""
        if isinstance(color, str):
            if color.startswith('#') and len(color) in [4, 7]:
                return True
            if color.startswith('rgb') or color.startswith('rgba'):
                return True
            if color in cls.COLORS.values():
                return True
        return False

    @classmethod
    def get_contrast_color(cls, background_color):
        """Obtener color de texto contrastante"""
        # Colores claros usan texto oscuro, colores oscuros usan texto claro
        light_backgrounds = [
            cls.COLORS['background_primary'],
            cls.COLORS['background_secondary'],
            cls.COLORS['blue_light'],
            cls.COLORS['green_light'],
            cls.COLORS['orange_light'],
            cls.COLORS['purple_light']
        ]

        if background_color in light_backgrounds:
            return cls.COLORS['text_primary']
        else:
            return cls.COLORS['background_primary']

    # =============================================================================
    # CONFIGURACIÓN DE DESARROLLO Y DEBUG
    # =============================================================================

    DEBUG = {
        "enable_logging": True,
        "log_level": "INFO",  # DEBUG, INFO, WARNING, ERROR, CRITICAL
        "show_tooltips": True,
        "enable_animations": True,
        "performance_monitoring": False,
        "ui_debug_mode": False
    }

    # Configuración específica para entorno de desarrollo
    DEVELOPMENT = {
        "auto_reload_styles": False,
        "show_component_borders": False,
        "enable_test_data": True,
        "mock_nlp_responses": False,
        "bypass_database": False
    }


# =============================================================================
# FUNCIONES DE UTILIDAD GLOBAL
# =============================================================================

def get_app_settings():
    """Obtener instancia global de configuración"""
    return Settings()


def apply_global_theme(app):
    """Aplicar tema global a la aplicación"""
    settings = Settings()
    app.setStyleSheet(settings.get_global_stylesheet())


# =============================================================================
# TESTING DE CONFIGURACIÓN
# =============================================================================

if __name__ == "__main__":
    print("🧪 Probando configuración de AlfaIA...")

    settings = Settings()

    # Probar colores
    print(f"Color principal: {settings.COLORS['blue_educational']}")
    print(f"Color de texto: {settings.COLORS['text_primary']}")
    print(f"Color de fondo: {settings.COLORS['background_primary']}")

    # Probar tema de sección
    dashboard_theme = settings.get_theme_color('dashboard', 'primary')
    print(f"Color del dashboard: {dashboard_theme}")

    # Probar validación
    is_valid = settings.validate_color('#4A90E2')
    print(f"Color válido: {is_valid}")

    # Probar contraste
    contrast = settings.get_contrast_color(settings.COLORS['background_primary'])
    print(f"Color de contraste: {contrast}")

    print("✅ Configuración probada exitosamente")
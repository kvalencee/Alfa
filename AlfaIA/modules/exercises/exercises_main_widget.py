# =============================================================================
# AlfaIA/modules/exercises/exercises_main_widget.py - Widget Principal de Ejercicios
# =============================================================================

from typing import Dict, Any, Optional
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget,
    QLabel, QPushButton, QFrame, QMessageBox, QScrollArea,
    QGridLayout, QSizePolicy, QSpacerItem
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap
import sys
from pathlib import Path

# Agregar path para imports
sys.path.append(str(Path(__file__).parent.parent.parent))
sys.path.append(str(Path(__file__).parent))

try:
    from config.settings import Settings

    print("✅ Settings importado en exercises_main_widget")
except ImportError:
    class Settings:
        COLORS = {
            'blue_educational': '#4A90E2',
            'green_success': '#7ED321',
            'orange_energetic': '#F5A623',
            'purple_creative': '#9013FE',
            'text_primary': '#2C3E50',
            'white_pure': '#FFFFFF'
        }

try:
    from exercises_manager import ExercisesManager, TipoEjercicio
    from exercise_widget import CompletarPalabraWidget
    from encontrar_error_widget import EncontrarErrorWidget
    from clasificar_palabra_widget import ClasificarPalabraWidget
    from comprension_widget import ComprensionWidget
    from ordenar_frase_widget import OrdenarFraseWidget

    print("✅ Todos los widgets de ejercicios importados")
except ImportError as e:
    print(f"⚠️ Error importando widgets: {e}")
    ExercisesManager = None


class ExerciseTypeCard(QFrame):
    """Tarjeta para seleccionar tipo de ejercicio"""

    clicked = pyqtSignal(str)  # Emite el tipo de ejercicio

    def __init__(self, exercise_type: str, title: str, description: str,
                 icon: str, color: str, count: int = 0, parent=None):
        super().__init__(parent)
        self.exercise_type = exercise_type
        self.title = title
        self.description = description
        self.icon = icon
        self.color = color
        self.count = count

        self.setup_ui()
        self.setup_hover_effects()

    def setup_ui(self):
        """Configurar interfaz de la tarjeta"""
        self.setFixedSize(280, 200)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        # Layout principal
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Header con icono y contador
        header_layout = QHBoxLayout()

        # Icono
        icon_label = QLabel(self.icon)
        icon_label.setStyleSheet(f"""
            QLabel {{
                font-size: 48px;
                color: {self.color};
                background-color: {self.color}15;
                border-radius: 25px;
                padding: 15px;
                min-width: 50px;
                max-width: 50px;
                min-height: 50px;
                max-height: 50px;
            }}
        """)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(icon_label)

        header_layout.addStretch()

        # Contador de ejercicios
        count_label = QLabel(f"{self.count} ejercicios")
        count_label.setStyleSheet(f"""
            QLabel {{
                font-size: 12px;
                color: {self.color};
                background-color: {self.color}20;
                border-radius: 12px;
                padding: 6px 12px;
                font-weight: 600;
            }}
        """)
        header_layout.addWidget(count_label)

        layout.addLayout(header_layout)

        # Título
        title_label = QLabel(self.title)
        title_label.setStyleSheet(f"""
            QLabel {{
                font-size: 20px;
                font-weight: bold;
                color: #2C3E50;
                margin: 5px 0;
            }}
        """)
        title_label.setWordWrap(True)
        layout.addWidget(title_label)

        # Descripción
        desc_label = QLabel(self.description)
        desc_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #7F8C8D;
                line-height: 1.4;
            }
        """)
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)

        # Espaciador
        layout.addStretch()

        # Estilo base de la tarjeta
        self.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 2px solid {self.color}20;
                border-radius: 16px;
            }}
        """)

    def setup_hover_effects(self):
        """Configurar efectos de hover"""
        self.original_style = self.styleSheet()

    def enterEvent(self, event):
        """Efecto al pasar el mouse"""
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {self.color}05;
                border: 2px solid {self.color}60;
                border-radius: 16px;
            }}
        """)
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Efecto al quitar el mouse"""
        self.setStyleSheet(self.original_style)
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        """Manejar clic en la tarjeta"""
        if event.button() == Qt.MouseButton.LeftButton:
            print(f"🎯 Seleccionado ejercicio: {self.exercise_type}")
            self.clicked.emit(self.exercise_type)
        super().mousePressEvent(event)


class ExerciseSelectionWidget(QWidget):
    """Widget para seleccionar tipo de ejercicio"""

    exercise_type_selected = pyqtSignal(str)

    def __init__(self, user_level: int = 1, parent=None):
        super().__init__(parent)
        self.user_level = user_level
        self.settings = Settings()
        self.exercises_manager = ExercisesManager() if ExercisesManager else None

        self.setup_ui()
        self.load_exercise_counts()

    def setup_ui(self):
        """Configurar interfaz de selección"""
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(30)

        # Header
        header_layout = QVBoxLayout()
        header_layout.setSpacing(15)

        # Título principal
        title = QLabel("🎯 Selecciona un Tipo de Ejercicio")
        title.setStyleSheet(f"""
            QLabel {{
                font-size: 32px;
                font-weight: bold;
                color: {self.settings.COLORS['text_primary']};
                text-align: center;
            }}
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(title)

        # Subtítulo
        subtitle = QLabel(f"Ejercicios adaptados a tu nivel: Nivel {self.user_level}")
        subtitle.setStyleSheet(f"""
            QLabel {{
                font-size: 18px;
                color: {self.settings.COLORS['blue_educational']};
                text-align: center;
            }}
        """)
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(subtitle)

        main_layout.addLayout(header_layout)

        # Área de tarjetas con scroll
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")

        # Widget contenedor de tarjetas
        cards_widget = QWidget()
        cards_layout = QGridLayout(cards_widget)
        cards_layout.setSpacing(25)
        cards_layout.setContentsMargins(20, 20, 20, 20)

        # Definir tipos de ejercicios
        exercise_types = [
            {
                'type': 'Completar_Palabra',
                'title': 'Completar Palabras',
                'description': 'Completa las palabras que faltan en oraciones y textos',
                'icon': '📝',
                'color': self.settings.COLORS['blue_educational']
            },
            {
                'type': 'Encontrar_Error',
                'title': 'Encontrar Errores',
                'description': 'Identifica y corrige errores ortográficos y gramaticales',
                'icon': '🔍',
                'color': self.settings.COLORS['orange_energetic']
            },
            {
                'type': 'Clasificar_Palabra',
                'title': 'Clasificar Palabras',
                'description': 'Clasifica palabras según su categoría gramatical',
                'icon': '📚',
                'color': self.settings.COLORS['purple_creative']
            },
            {
                'type': 'Comprension',
                'title': 'Comprensión Lectora',
                'description': 'Lee textos y responde preguntas de comprensión',
                'icon': '📖',
                'color': self.settings.COLORS['green_success']
            },
            {
                'type': 'Ordenar_Frase',
                'title': 'Ordenar Frases',
                'description': 'Ordena palabras para formar frases correctas',
                'icon': '🔤',
                'color': '#e74c3c'
            },
            {
                'type': 'Aleatorio',
                'title': 'Ejercicio Aleatorio',
                'description': 'Ejercicio sorpresa adaptado a tu nivel',
                'icon': '🎲',
                'color': '#f39c12'
            }
        ]

        # Crear tarjetas
        self.exercise_cards = {}
        for i, exercise_info in enumerate(exercise_types):
            card = ExerciseTypeCard(
                exercise_type=exercise_info['type'],
                title=exercise_info['title'],
                description=exercise_info['description'],
                icon=exercise_info['icon'],
                color=exercise_info['color'],
                count=0  # Se actualizará después
            )
            card.clicked.connect(self.exercise_type_selected.emit)

            row = i // 3  # 3 tarjetas por fila
            col = i % 3
            cards_layout.addWidget(card, row, col)

            self.exercise_cards[exercise_info['type']] = card

        scroll_area.setWidget(cards_widget)
        main_layout.addWidget(scroll_area)

        # Botón de ejercicio rápido
        quick_exercise_btn = QPushButton("⚡ Ejercicio Rápido")
        quick_exercise_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 {self.settings.COLORS['blue_educational']},
                    stop: 1 {self.settings.COLORS['purple_creative']}
                );
                color: white;
                border: none;
                border-radius: 15px;
                padding: 18px 30px;
                font-size: 18px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                transform: translateY(-2px);
            }}
        """)
        quick_exercise_btn.clicked.connect(lambda: self.exercise_type_selected.emit('Aleatorio'))
        main_layout.addWidget(quick_exercise_btn)

    def load_exercise_counts(self):
        """Cargar contadores de ejercicios"""
        if not self.exercises_manager:
            return

        try:
            # Contar ejercicios implementados
            implemented_types = ['Completar_Palabra', 'Encontrar_Error', 'Clasificar_Palabra', 'Comprension',
                                 'Ordenar_Frase']

            for exercise_type in implemented_types:
                if exercise_type in self.exercise_cards:
                    try:
                        # Obtener ejercicios de este tipo
                        tipo_enum = TipoEjercicio(exercise_type)
                        exercises = self.exercises_manager.get_exercises_by_type(tipo_enum, 50)
                        count = len(exercises)

                        # Actualizar contador en la tarjeta
                        card = self.exercise_cards[exercise_type]
                        # Encontrar el label del contador y actualizarlo
                        for child in card.findChildren(QLabel):
                            if 'ejercicios' in child.text():
                                child.setText(f"{count} ejercicios")
                                break
                    except Exception as e:
                        print(f"⚠️ Error contando {exercise_type}: {e}")
                        # Usar demo count
                        card = self.exercise_cards[exercise_type]
                        for child in card.findChildren(QLabel):
                            if 'ejercicios' in child.text():
                                child.setText("Demo disponible")
                                break
        except Exception as e:
            print(f"⚠️ Error cargando contadores: {e}")


class ExercisesMainWidget(QWidget):
    """Widget principal que maneja todos los ejercicios"""

    exercise_completed = pyqtSignal(dict)  # Resultado del ejercicio
    back_to_dashboard = pyqtSignal()

    def __init__(self, user_data=None, parent=None):
        super().__init__(parent)
        self.user_data = user_data
        self.settings = Settings()
        self.exercises_manager = ExercisesManager() if ExercisesManager else None
        self.current_exercise_widget = None

        print(f"🎯 ExercisesMainWidget creado para usuario: {user_data.get_display_name() if user_data else 'Demo'}")

        self.setup_ui()

    def setup_ui(self):
        """Configurar interfaz principal"""
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Stack para alternar entre selección y ejercicio
        self.stack = QStackedWidget()

        # Widget de selección
        user_level = 1
        if self.user_data:
            try:
                user_level = int(self.user_data.get_level() or 1)
            except:
                user_level = 1

        self.selection_widget = ExerciseSelectionWidget(user_level)
        self.selection_widget.exercise_type_selected.connect(self.start_exercise)
        self.stack.addWidget(self.selection_widget)

        # Widget de ejercicio (se añadirá dinámicamente)
        self.exercise_container = QWidget()
        self.exercise_layout = QVBoxLayout(self.exercise_container)
        self.exercise_layout.setContentsMargins(0, 0, 0, 0)
        self.stack.addWidget(self.exercise_container)

        main_layout.addWidget(self.stack)

        # Mostrar selección por defecto
        self.stack.setCurrentWidget(self.selection_widget)

    def start_exercise(self, exercise_type: str):
        """Iniciar ejercicio del tipo especificado"""
        print(f"🚀 Iniciando ejercicio: {exercise_type}")

        try:
            # Obtener ejercicio
            if exercise_type == 'Aleatorio':
                exercise_data = self.get_random_exercise()
            else:
                exercise_data = self.get_exercise_by_type(exercise_type)

            if not exercise_data:
                QMessageBox.warning(
                    self,
                    "⚠️ Sin Ejercicios",
                    f"No hay ejercicios disponibles de tipo '{exercise_type}' para tu nivel."
                )
                return

            # Crear widget del ejercicio
            exercise_widget = self.create_exercise_widget(exercise_data)

            if exercise_widget:
                # Limpiar container anterior
                self.clear_exercise_container()

                # Añadir nuevo widget
                self.exercise_layout.addWidget(exercise_widget)
                self.current_exercise_widget = exercise_widget

                # Conectar señales
                exercise_widget.exercise_completed.connect(self.on_exercise_completed)
                exercise_widget.exercise_cancelled.connect(self.back_to_selection)

                # Cambiar a vista de ejercicio
                self.stack.setCurrentWidget(self.exercise_container)
            else:
                QMessageBox.critical(
                    self,
                    "❌ Error",
                    f"No se pudo crear el widget para el ejercicio '{exercise_type}'"
                )

        except Exception as e:
            print(f"❌ Error iniciando ejercicio: {e}")
            QMessageBox.critical(
                self,
                "❌ Error",
                f"Error inesperado al iniciar ejercicio:\n{str(e)}"
            )

    def get_exercise_by_type(self, exercise_type: str) -> Optional[Dict[str, Any]]:
        """Obtener ejercicio por tipo"""
        if not self.exercises_manager:
            return self.get_demo_exercise(exercise_type)

        try:
            tipo_enum = TipoEjercicio(exercise_type)
            exercises = self.exercises_manager.get_exercises_by_type(tipo_enum, 1)

            if exercises:
                return exercises[0]
            else:
                return self.get_demo_exercise(exercise_type)

        except Exception as e:
            print(f"❌ Error obteniendo ejercicio: {e}")
            return self.get_demo_exercise(exercise_type)

    def get_random_exercise(self) -> Optional[Dict[str, Any]]:
        """Obtener ejercicio aleatorio"""
        if not self.exercises_manager:
            return self.get_demo_exercise('Aleatorio')

        try:
            user_level = 1
            if self.user_data:
                try:
                    user_level = int(self.user_data.get_level() or 1)
                except:
                    user_level = 1

            exercise = self.exercises_manager.get_random_exercise(user_level)
            return exercise or self.get_demo_exercise('Aleatorio')

        except Exception as e:
            print(f"❌ Error obteniendo ejercicio aleatorio: {e}")
            return self.get_demo_exercise('Aleatorio')

    def get_demo_exercise(self, exercise_type: str) -> Dict[str, Any]:
        """Obtener ejercicio demo"""
        import random

        if exercise_type == 'Aleatorio':
            types = ['Completar_Palabra', 'Encontrar_Error', 'Clasificar_Palabra', 'Comprension', 'Ordenar_Frase']
            exercise_type = random.choice(types)

        demos = {
            'Completar_Palabra': {
                'id': 1,
                'tipo': 'Completar_Palabra',
                'titulo': 'Completa las Palabras (Demo)',
                'instrucciones': 'Completa las palabras que faltan en cada oración',
                'contenido': {
                    'oraciones': [
                        'El _ato juega en el jardín',
                        'La _asa está muy limpia',
                        'Mi _adre cocina muy bien'
                    ]
                },
                'respuestas_correctas': [['gato'], ['casa'], ['madre']],
                'nivel_dificultad': 2,
                'puntos_maximos': 30,
                'tiempo_limite': 120
            },
            'Encontrar_Error': {
                'id': 2,
                'tipo': 'Encontrar_Error',
                'titulo': 'Encuentra los Errores (Demo)',
                'instrucciones': 'Haz clic en las palabras que tengan errores y corrígelas',
                'contenido': {
                    'oraciones': [
                        'Los niña juegan en el parque',
                        'Ayer fuí al cine',
                        'El agua esta muy fria'
                    ]
                },
                'nivel_dificultad': 4,
                'puntos_maximos': 40,
                'tiempo_limite': 180
            },
            'Clasificar_Palabra': {
                'id': 3,
                'tipo': 'Clasificar_Palabra',
                'titulo': 'Clasifica las Palabras (Demo)',
                'instrucciones': 'Arrastra cada palabra a su categoría correcta',
                'contenido': {
                    'palabras': ['correr', 'casa', 'bonito', 'rápidamente'],
                    'categorias': ['Verbo', 'Sustantivo', 'Adjetivo', 'Adverbio']
                },
                'nivel_dificultad': 3,
                'puntos_maximos': 40,
                'tiempo_limite': 150
            },
            'Comprension': {
                'id': 4,
                'tipo': 'Comprension',
                'titulo': 'Comprensión Lectora (Demo)',
                'instrucciones': 'Lee el texto y responde las preguntas',
                'nivel_dificultad': 4,
                'puntos_maximos': 25,
                'tiempo_limite': 600
            },
            'Ordenar_Frase': {
                'id': 5,
                'tipo': 'Ordenar_Frase',
                'titulo': 'Ordena las Frases (Demo)',
                'instrucciones': 'Arrastra las palabras para formar oraciones correctas',
                'contenido': {
                    'frases': [
                        'El gato juega en el jardín',
                        'María lee un libro'
                    ]
                },
                'nivel_dificultad': 4,
                'puntos_maximos': 40,
                'tiempo_limite': 240
            }
        }

        return demos.get(exercise_type, demos['Completar_Palabra'])

    def create_exercise_widget(self, exercise_data: Dict[str, Any]) -> Optional[QWidget]:
        """Crear widget específico para el ejercicio"""
        exercise_type = exercise_data.get('tipo', '')

        try:
            if exercise_type == 'Completar_Palabra':
                return CompletarPalabraWidget(exercise_data)
            elif exercise_type == 'Encontrar_Error':
                return EncontrarErrorWidget(exercise_data)
            elif exercise_type == 'Clasificar_Palabra':
                return ClasificarPalabraWidget(exercise_data)
            elif exercise_type == 'Comprension':
                return ComprensionWidget(exercise_data)
            elif exercise_type == 'Ordenar_Frase':
                return OrdenarFraseWidget(exercise_data)
            else:
                print(f"⚠️ Tipo de ejercicio no implementado: {exercise_type}")
                return None

        except Exception as e:
            print(f"❌ Error creando widget de ejercicio: {e}")
            return None

    def clear_exercise_container(self):
        """Limpiar contenedor de ejercicio"""
        while self.exercise_layout.count():
            child = self.exercise_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        self.current_exercise_widget = None

    def on_exercise_completed(self, result: Dict[str, Any]):
        """Manejar ejercicio completado"""
        print(f"✅ Ejercicio completado: {result['score']}/{result['max_score']} puntos")

        # Guardar resultado si hay manager y usuario
        if self.exercises_manager and self.user_data and hasattr(self.user_data, 'id'):
            try:
                success = self.exercises_manager.save_exercise_result(
                    user_id=self.user_data.id,
                    exercise_id=result['exercise_id'],
                    respuestas=result['answers'],
                    puntos=result['score'],
                    precision=result['precision'],
                    tiempo=result['time_seconds']
                )

                if success:
                    print("💾 Resultado guardado en BD")
                else:
                    print("⚠️ No se pudo guardar resultado en BD")

            except Exception as e:
                print(f"❌ Error guardando resultado: {e}")

        # Emitir señal para el dashboard
        self.exercise_completed.emit(result)

        # Volver a selección después de un delay
        QTimer.singleShot(2000, self.back_to_selection)

    def back_to_selection(self):
        """Volver a la selección de ejercicios"""
        print("🔙 Volviendo a selección de ejercicios")

        # Limpiar ejercicio actual
        self.clear_exercise_container()

        # Volver a vista de selección
        self.stack.setCurrentWidget(self.selection_widget)

        # Actualizar contadores
        self.selection_widget.load_exercise_counts()


# =============================================================================
# TESTING
# =============================================================================
if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)


    # Datos de usuario demo
    class DemoUserData:
        def get_display_name(self):
            return "Usuario Demo"

        def get_level(self):
            return "3"

        @property
        def id(self):
            return 1


    user_data = DemoUserData()

    # Crear widget principal
    widget = ExercisesMainWidget(user_data)
    widget.setMinimumSize(1200, 800)
    widget.show()


    # Conectar señales para testing
    def on_exercise_completed(result):
        print(f"🎉 Ejercicio completado en main: {result}")


    widget.exercise_completed.connect(on_exercise_completed)

    sys.exit(app.exec())
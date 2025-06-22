# =============================================================================
# AlfaIA/modules/exercises/comprension_widget.py - Widget de Comprensión Lectora
# =============================================================================

from typing import Dict, Any, List
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QRadioButton, QButtonGroup, QTextEdit, QScrollArea,
    QCheckBox, QLineEdit, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QTextCharFormat, QColor
import sys
from pathlib import Path

# Importar widget base
sys.path.append(str(Path(__file__).parent))
from exercise_widget import ExerciseWidget

try:
    from config.settings import Settings
except ImportError:
    class Settings:
        COLORS = {
            'blue_educational': '#4A90E2',
            'green_success': '#7ED321',
            'orange_energetic': '#F5A623',
            'text_primary': '#2C3E50',
            'white_pure': '#FFFFFF'
        }


class ReadingTextWidget(QTextEdit):
    """Widget de texto para lectura"""

    def __init__(self, text: str, parent=None):
        super().__init__(parent)
        self.original_text = text

        self.setReadOnly(True)
        self.setMinimumHeight(200)
        self.setMaximumHeight(400)

        # Configurar estilo
        self.setStyleSheet("""
            QTextEdit {
                border: 2px solid #e2e8f0;
                border-radius: 12px;
                padding: 20px;
                font-size: 16px;
                line-height: 1.6;
                background-color: #f8fafc;
                color: #2C3E50;
                font-family: 'Georgia', 'Times New Roman', serif;
            }
            QScrollBar:vertical {
                background-color: #f1f5f9;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #cbd5e1;
                border-radius: 6px;
                min-height: 20px;
            }
        """)

        self.setPlainText(text)


class QuestionWidget(QFrame):
    """Widget para una pregunta individual"""

    answer_changed = pyqtSignal(int, str)  # question_index, answer

    def __init__(self, question_data: Dict[str, Any], question_index: int, parent=None):
        super().__init__(parent)
        self.question_data = question_data
        self.question_index = question_index
        self.question_type = question_data.get('tipo', 'multiple_choice')
        self.answer_value = ""

        self.setup_ui()

    def setup_ui(self):
        """Configurar interfaz de la pregunta"""
        settings = Settings()

        self.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 2px solid {settings.COLORS['blue_educational']}20;
                border-radius: 12px;
                padding: 15px;
                margin: 8px 0;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Número de pregunta y puntuación
        header_layout = QHBoxLayout()

        question_num = QLabel(f"Pregunta {self.question_index + 1}")
        question_num.setStyleSheet(f"""
            QLabel {{
                font-size: 16px;
                font-weight: bold;
                color: {settings.COLORS['blue_educational']};
                background-color: {settings.COLORS['blue_educational']}15;
                padding: 6px 12px;
                border-radius: 8px;
            }}
        """)
        header_layout.addWidget(question_num)

        header_layout.addStretch()

        points_label = QLabel(f"{self.question_data.get('puntos', 5)} puntos")
        points_label.setStyleSheet(f"""
            QLabel {{
                font-size: 14px;
                color: {settings.COLORS['green_success']};
                background-color: {settings.COLORS['green_success']}15;
                padding: 4px 8px;
                border-radius: 6px;
                font-weight: 600;
            }}
        """)
        header_layout.addWidget(points_label)

        layout.addLayout(header_layout)

        # Texto de la pregunta
        question_text = QLabel(self.question_data.get('pregunta', ''))
        question_text.setStyleSheet(f"""
            QLabel {{
                font-size: 16px;
                color: {settings.COLORS['text_primary']};
                padding: 10px 0;
                line-height: 1.4;
            }}
        """)
        question_text.setWordWrap(True)
        layout.addWidget(question_text)

        # Área de respuesta según el tipo
        if self.question_type == 'multiple_choice':
            self.create_multiple_choice()
        elif self.question_type == 'true_false':
            self.create_true_false()
        elif self.question_type == 'short_answer':
            self.create_short_answer()
        elif self.question_type == 'multiple_select':
            self.create_multiple_select()

        layout.addWidget(self.answer_area)

    def create_multiple_choice(self):
        """Crear opciones múltiples"""
        self.answer_area = QFrame()
        layout = QVBoxLayout(self.answer_area)
        layout.setSpacing(10)

        self.button_group = QButtonGroup()
        opciones = self.question_data.get('opciones', [])

        for i, opcion in enumerate(opciones):
            radio = QRadioButton(opcion)
            radio.setStyleSheet("""
                QRadioButton {
                    font-size: 15px;
                    color: #2C3E50;
                    padding: 8px 12px;
                    spacing: 10px;
                }
                QRadioButton::indicator {
                    width: 18px;
                    height: 18px;
                }
                QRadioButton::indicator:unchecked {
                    border: 2px solid #cbd5e1;
                    border-radius: 9px;
                    background-color: white;
                }
                QRadioButton::indicator:checked {
                    border: 2px solid #4A90E2;
                    border-radius: 9px;
                    background-color: #4A90E2;
                }
            """)
            radio.toggled.connect(lambda checked, idx=i: self.on_option_selected(idx) if checked else None)
            self.button_group.addButton(radio, i)
            layout.addWidget(radio)

    def create_true_false(self):
        """Crear verdadero/falso"""
        self.answer_area = QFrame()
        layout = QHBoxLayout(self.answer_area)
        layout.setSpacing(20)

        self.button_group = QButtonGroup()

        # Verdadero
        true_radio = QRadioButton("✅ Verdadero")
        true_radio.setStyleSheet("""
            QRadioButton {
                font-size: 16px;
                color: #22c55e;
                padding: 12px 20px;
                font-weight: 600;
                spacing: 12px;
            }
        """)
        true_radio.toggled.connect(lambda checked: self.on_tf_selected(True) if checked else None)
        self.button_group.addButton(true_radio, 0)
        layout.addWidget(true_radio)

        # Falso
        false_radio = QRadioButton("❌ Falso")
        false_radio.setStyleSheet("""
            QRadioButton {
                font-size: 16px;
                color: #ef4444;
                padding: 12px 20px;
                font-weight: 600;
                spacing: 12px;
            }
        """)
        false_radio.toggled.connect(lambda checked: self.on_tf_selected(False) if checked else None)
        self.button_group.addButton(false_radio, 1)
        layout.addWidget(false_radio)

        layout.addStretch()

    def create_short_answer(self):
        """Crear respuesta corta"""
        self.answer_area = QFrame()
        layout = QVBoxLayout(self.answer_area)

        instruction = QLabel("💭 Escribe tu respuesta:")
        instruction.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #6b7280;
                margin-bottom: 5px;
            }
        """)
        layout.addWidget(instruction)

        self.answer_input = QLineEdit()
        self.answer_input.setPlaceholderText("Escribe tu respuesta aquí...")
        self.answer_input.setStyleSheet("""
            QLineEdit {
                font-size: 15px;
                padding: 12px 15px;
                border: 2px solid #d1d5db;
                border-radius: 8px;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #4A90E2;
                background-color: #f0f7ff;
            }
        """)
        self.answer_input.textChanged.connect(self.on_text_changed)
        layout.addWidget(self.answer_input)

    def create_multiple_select(self):
        """Crear selección múltiple"""
        self.answer_area = QFrame()
        layout = QVBoxLayout(self.answer_area)
        layout.setSpacing(10)

        instruction = QLabel("☑️ Selecciona todas las opciones correctas:")
        instruction.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #6b7280;
                margin-bottom: 8px;
                font-weight: 600;
            }
        """)
        layout.addWidget(instruction)

        self.checkboxes = []
        opciones = self.question_data.get('opciones', [])

        for i, opcion in enumerate(opciones):
            checkbox = QCheckBox(opcion)
            checkbox.setStyleSheet("""
                QCheckBox {
                    font-size: 15px;
                    color: #2C3E50;
                    padding: 8px 12px;
                    spacing: 10px;
                }
                QCheckBox::indicator {
                    width: 18px;
                    height: 18px;
                }
                QCheckBox::indicator:unchecked {
                    border: 2px solid #cbd5e1;
                    border-radius: 4px;
                    background-color: white;
                }
                QCheckBox::indicator:checked {
                    border: 2px solid #4A90E2;
                    border-radius: 4px;
                    background-color: #4A90E2;
                }
            """)
            checkbox.stateChanged.connect(self.on_checkbox_changed)
            self.checkboxes.append(checkbox)
            layout.addWidget(checkbox)

    def on_option_selected(self, option_index: int):
        """Manejar selección de opción múltiple"""
        self.answer_value = str(option_index)
        self.answer_changed.emit(self.question_index, self.answer_value)

    def on_tf_selected(self, is_true: bool):
        """Manejar selección verdadero/falso"""
        self.answer_value = str(is_true)
        self.answer_changed.emit(self.question_index, self.answer_value)

    def on_text_changed(self, text: str):
        """Manejar cambio de texto"""
        self.answer_value = text.strip()
        self.answer_changed.emit(self.question_index, self.answer_value)

    def on_checkbox_changed(self):
        """Manejar cambio en checkboxes"""
        selected = []
        for i, checkbox in enumerate(self.checkboxes):
            if checkbox.isChecked():
                selected.append(str(i))

        self.answer_value = ','.join(selected)
        self.answer_changed.emit(self.question_index, self.answer_value)

    def get_answer(self) -> str:
        """Obtener respuesta actual"""
        return self.answer_value

    def has_answer(self) -> bool:
        """Verificar si tiene respuesta"""
        return bool(self.answer_value.strip())


class ComprensionWidget(ExerciseWidget):
    """Widget para ejercicios de comprensión lectora"""

    def __init__(self, exercise_data: Dict[str, Any], parent=None):
        super().__init__(exercise_data, parent)
        self.question_widgets = []
        print(f"📖 ComprensionWidget creado")

    def load_exercise_content(self):
        """Cargar contenido de comprensión lectora"""
        contenido = self.exercise_data.get('contenido', {})
        texto = contenido.get('texto', '')
        preguntas = contenido.get('preguntas', [])

        if not texto or not preguntas:
            self.load_demo_content()
            return

        # Limpiar layout
        self.clear_content_layout()

        # Instrucciones específicas
        instruction_label = QLabel("📚 Lee el texto cuidadosamente y responde las preguntas")
        instruction_label.setStyleSheet(f"""
            QLabel {{
                font-size: 16px;
                color: {self.settings.COLORS['blue_educational']};
                background-color: {self.settings.COLORS['blue_educational']}10;
                border-radius: 8px;
                padding: 12px 15px;
                border: 1px solid {self.settings.COLORS['blue_educational']}30;
                margin-bottom: 20px;
            }}
        """)
        instruction_label.setWordWrap(True)
        self.content_layout.addWidget(instruction_label)

        # Título del texto si existe
        titulo = contenido.get('titulo', '')
        if titulo:
            title_label = QLabel(titulo)
            title_label.setStyleSheet(f"""
                QLabel {{
                    font-size: 22px;
                    font-weight: bold;
                    color: {self.settings.COLORS['text_primary']};
                    text-align: center;
                    margin: 15px 0;
                }}
            """)
            title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            title_label.setWordWrap(True)
            self.content_layout.addWidget(title_label)

        # Widget de texto para lectura
        reading_widget = ReadingTextWidget(texto)
        self.content_layout.addWidget(reading_widget)

        # Separador
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet(f"""
            QFrame {{
                color: {self.settings.COLORS['blue_educational']}30;
                background-color: {self.settings.COLORS['blue_educational']}30;
                height: 2px;
                margin: 20px 0;
            }}
        """)
        self.content_layout.addWidget(separator)

        # Título de preguntas
        questions_title = QLabel("❓ Preguntas de Comprensión")
        questions_title.setStyleSheet(f"""
            QLabel {{
                font-size: 20px;
                font-weight: bold;
                color: {self.settings.COLORS['text_primary']};
                margin: 15px 0 10px 0;
            }}
        """)
        self.content_layout.addWidget(questions_title)

        # Crear widgets de preguntas
        self.question_widgets = []
        for i, pregunta_data in enumerate(preguntas):
            question_widget = QuestionWidget(pregunta_data, i)
            question_widget.answer_changed.connect(self.on_answer_changed)
            self.question_widgets.append(question_widget)
            self.content_layout.addWidget(question_widget)

        # Espaciador al final
        self.content_layout.addStretch()

        # Iniciar ejercicio
        QTimer.singleShot(100, self.start_exercise)

    def load_demo_content(self):
        """Cargar contenido demo"""
        demo_content = {
            'titulo': 'El Jardín de María',
            'texto': '''María tiene un jardín muy hermoso detrás de su casa. En él cultiva diferentes tipos de flores: rosas rojas, tulipanes amarillos y margaritas blancas. Cada mañana, antes de ir al trabajo, María riega todas sus plantas con mucho cariño.

El jardín no solo tiene flores. También hay un pequeño huerto donde María planta tomates, lechugas y zanahorias. A ella le gusta mucho comer verduras frescas que ella misma cultiva.

En el centro del jardín hay un árbol muy grande que da sombra en los días calurosos. Bajo este árbol, María ha puesto una mesa pequeña donde le gusta leer libros por las tardes.

María está muy orgullosa de su jardín y siempre invita a sus amigos a visitarlo. Todos dicen que es el jardín más bonito del barrio.''',

            'preguntas': [
                {
                    'tipo': 'multiple_choice',
                    'pregunta': '¿Qué tipos de flores cultiva María en su jardín?',
                    'opciones': [
                        'Rosas rojas, tulipanes amarillos y margaritas blancas',
                        'Solo rosas rojas',
                        'Girasoles y violetas',
                        'Todas las flores que existen'
                    ],
                    'respuesta_correcta': 0,
                    'puntos': 5
                },
                {
                    'tipo': 'true_false',
                    'pregunta': 'María riega sus plantas por la noche después del trabajo.',
                    'respuesta_correcta': False,
                    'puntos': 5
                },
                {
                    'tipo': 'short_answer',
                    'pregunta': '¿Qué verduras planta María en su huerto?',
                    'respuestas_correctas': ['tomates, lechugas y zanahorias', 'tomates lechugas zanahorias'],
                    'puntos': 5
                },
                {
                    'tipo': 'multiple_choice',
                    'pregunta': '¿Para qué usa María la mesa bajo el árbol?',
                    'opciones': [
                        'Para comer verduras',
                        'Para leer libros por las tardes',
                        'Para regar las plantas',
                        'Para recibir a sus amigos'
                    ],
                    'respuesta_correcta': 1,
                    'puntos': 5
                },
                {
                    'tipo': 'true_false',
                    'pregunta': 'Los amigos de María piensan que su jardín es el más bonito del barrio.',
                    'respuesta_correcta': True,
                    'puntos': 5
                }
            ]
        }

        # Actualizar datos del ejercicio
        if 'contenido' not in self.exercise_data:
            self.exercise_data['contenido'] = {}
        self.exercise_data['contenido'].update(demo_content)

        # Establecer respuestas correctas
        self.exercise_data['respuestas_correctas'] = [
            pregunta.get('respuesta_correcta', pregunta.get('respuestas_correctas', ''))
            for pregunta in demo_content['preguntas']
        ]

        # Cargar contenido
        self.load_exercise_content()

    def clear_content_layout(self):
        """Limpiar layout de contenido"""
        while self.content_layout.count():
            child = self.content_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def on_answer_changed(self, question_index: int, answer: str):
        """Manejar cambio en respuesta"""
        # Actualizar respuestas actuales
        self.current_answers[f'pregunta_{question_index}'] = answer

        # Contar preguntas respondidas
        answered_count = sum(1 for widget in self.question_widgets if widget.has_answer())
        total_questions = len(self.question_widgets)

        # Actualizar progreso
        self.update_progress(answered_count, total_questions)

    def validate_answers(self) -> Dict[str, Any]:
        """Validar respuestas de comprensión lectora"""
        respuestas_correctas = self.exercise_data.get('respuestas_correctas', [])
        preguntas = self.exercise_data.get('contenido', {}).get('preguntas', [])
        puntos_maximos = self.exercise_data.get('puntos_maximos', 25)

        if not respuestas_correctas or not preguntas:
            # Modo demo básico
            answered_count = sum(1 for widget in self.question_widgets if widget.has_answer())
            if answered_count == len(self.question_widgets):
                return {
                    'is_valid': True,
                    'score': puntos_maximos,
                    'max_score': puntos_maximos,
                    'precision': 100.0,
                    'feedback': f"¡Respondiste todas las {answered_count} preguntas! (modo demo)",
                    'details': {'answered': answered_count}
                }
            else:
                return {
                    'is_valid': False,
                    'score': 0,
                    'max_score': puntos_maximos,
                    'precision': 0.0,
                    'feedback': f"Responde las {len(self.question_widgets) - answered_count} preguntas restantes",
                    'details': {}
                }

        # Validación real
        score = 0
        correct_answers = 0
        total_questions = len(self.question_widgets)
        details = {}

        for i, (question_widget, correct_answer, question_data) in enumerate(
                zip(self.question_widgets, respuestas_correctas, preguntas)):
            user_answer = question_widget.get_answer()
            question_type = question_data.get('tipo', 'multiple_choice')
            points_for_question = question_data.get('puntos', 5)

            is_correct = False

            if question_type == 'multiple_choice':
                try:
                    is_correct = int(user_answer) == correct_answer
                except:
                    is_correct = False

            elif question_type == 'true_false':
                try:
                    user_bool = user_answer.lower() == 'true'
                    is_correct = user_bool == correct_answer
                except:
                    is_correct = False

            elif question_type == 'short_answer':
                if isinstance(correct_answer, list):
                    # Múltiples respuestas válidas
                    user_lower = user_answer.lower().strip()
                    is_correct = any(user_lower in correct.lower() for correct in correct_answer)
                else:
                    is_correct = user_answer.lower().strip() in str(correct_answer).lower()

            elif question_type == 'multiple_select':
                try:
                    user_selections = set(user_answer.split(',')) if user_answer else set()
                    correct_selections = set(str(x) for x in correct_answer) if isinstance(correct_answer, list) else {
                        str(correct_answer)}
                    is_correct = user_selections == correct_selections
                except:
                    is_correct = False

            if is_correct:
                correct_answers += 1
                score += points_for_question

            details[f'pregunta_{i + 1}'] = {
                'user_answer': user_answer,
                'correct_answer': correct_answer,
                'is_correct': is_correct,
                'points_earned': points_for_question if is_correct else 0,
                'question_type': question_type
            }

        # Verificar que todas estén respondidas
        all_answered = all(widget.has_answer() for widget in self.question_widgets)

        # Calcular precisión
        precision = (correct_answers / total_questions * 100) if total_questions > 0 else 0

        # Generar feedback
        feedback_messages = []
        if correct_answers == total_questions:
            feedback_messages.append("¡Excelente comprensión! Todas las respuestas son correctas.")
        elif correct_answers >= total_questions * 0.8:
            feedback_messages.append(
                f"¡Muy buena comprensión! {correct_answers} de {total_questions} respuestas correctas.")
        elif correct_answers >= total_questions * 0.6:
            feedback_messages.append(f"Buena comprensión. {correct_answers} de {total_questions} respuestas correctas.")
        else:
            feedback_messages.append(
                f"Necesitas mejorar la comprensión. {correct_answers} de {total_questions} respuestas correctas.")

        if not all_answered:
            unanswered = sum(1 for widget in self.question_widgets if not widget.has_answer())
            feedback_messages.append(f"Faltan {unanswered} preguntas por responder.")

        return {
            'is_valid': all_answered,
            'score': score,
            'max_score': sum(q.get('puntos', 5) for q in preguntas),
            'precision': precision,
            'feedback': ' '.join(feedback_messages),
            'details': {
                'total_questions': total_questions,
                'correct_answers': correct_answers,
                'all_answered': all_answered,
                'questions': details
            }
        }


# =============================================================================
# TESTING
# =============================================================================
if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)

    # Datos de ejercicio demo
    exercise_data = {
        'id': 4,
        'tipo': 'Comprension',
        'titulo': 'Comprensión Lectora - El Jardín de María',
        'instrucciones': 'Lee el texto con atención y responde todas las preguntas',
        'nivel_dificultad': 3,
        'puntos_maximos': 25,
        'tiempo_limite': 600  # 10 minutos
    }

    # Crear widget
    widget = ComprensionWidget(exercise_data)
    widget.setMinimumSize(1000, 800)
    widget.show()


    # Conectar señales para testing
    def on_completed(result):
        print(f"✅ Ejercicio completado: {result}")


    def on_cancelled():
        print("❌ Ejercicio cancelado")
        app.quit()


    widget.exercise_completed.connect(on_completed)
    widget.exercise_cancelled.connect(on_cancelled)

    sys.exit(app.exec())
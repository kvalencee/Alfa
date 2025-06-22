# =============================================================================
# AlfaIA/modules/exercises/exercise_widget.py - Widget Base para Ejercicios
# =============================================================================

import json
import time
from typing import Dict, Any, List, Optional
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QFrame, QProgressBar, QScrollArea,
    QMessageBox, QSpacerItem, QSizePolicy, QTextEdit, QLineEdit
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QColor, QPalette, QPixmap
import sys
from pathlib import Path

# Agregar path para imports
sys.path.append(str(Path(__file__).parent.parent.parent))

try:
    from config.settings import Settings

    print("✅ Settings importado en exercise_widget")
except ImportError:
    class Settings:
        COLORS = {
            'blue_educational': '#4A90E2',
            'green_success': '#7ED321',
            'orange_energetic': '#F5A623',
            'text_primary': '#2C3E50',
            'white_pure': '#FFFFFF'
        }


class ExerciseWidget(QWidget):
    """Widget base para todos los ejercicios"""

    # Señales
    exercise_completed = pyqtSignal(dict)  # Emite resultado del ejercicio
    exercise_cancelled = pyqtSignal()
    time_updated = pyqtSignal(int)  # Tiempo en segundos

    def __init__(self, exercise_data: Dict[str, Any], parent=None):
        super().__init__(parent)
        self.settings = Settings()
        self.exercise_data = exercise_data

        # Estado del ejercicio
        self.start_time = None
        self.is_completed = False
        self.current_answers = {}
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_timer)
        self.elapsed_seconds = 0

        print(f"🎯 Creando ExerciseWidget: {exercise_data.get('titulo', 'Sin título')}")

        self.setup_ui()
        self.load_exercise_content()

    def setup_ui(self):
        """Configurar interfaz base del ejercicio"""
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # Header del ejercicio
        header_frame = self.create_header()
        main_layout.addWidget(header_frame)

        # Área de contenido scrolleable
        self.content_scroll = QScrollArea()
        self.content_scroll.setWidgetResizable(True)
        self.content_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.content_scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)

        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(10, 10, 10, 10)
        self.content_layout.setSpacing(15)

        self.content_scroll.setWidget(self.content_widget)
        main_layout.addWidget(self.content_scroll)

        # Footer con controles
        footer_frame = self.create_footer()
        main_layout.addWidget(footer_frame)

        # Aplicar estilos
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {self.settings.COLORS['white_pure']};
                color: {self.settings.COLORS['text_primary']};
                font-family: 'Segoe UI', Arial, sans-serif;
            }}
        """)

    def create_header(self) -> QFrame:
        """Crear header con información del ejercicio"""
        header = QFrame()
        header.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 {self.settings.COLORS['blue_educational']},
                    stop: 1 #5ba3f5
                );
                border-radius: 15px;
                padding: 0px;
                margin: 0px;
            }}
        """)
        header.setFixedHeight(120)

        layout = QVBoxLayout(header)
        layout.setContentsMargins(25, 15, 25, 15)
        layout.setSpacing(8)

        # Primera fila: título y nivel
        top_layout = QHBoxLayout()

        # Título
        title = QLabel(self.exercise_data.get('titulo', 'Ejercicio'))
        title.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: white;
                background-color: transparent;
                border: none;
            }
        """)
        top_layout.addWidget(title)

        top_layout.addStretch()

        # Información del nivel
        nivel = self.exercise_data.get('nivel_dificultad', 1)
        puntos = self.exercise_data.get('puntos_maximos', 10)

        info_label = QLabel(f"Nivel {nivel} • {puntos} puntos")
        info_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                color: white;
                background-color: rgba(255,255,255,0.2);
                border-radius: 12px;
                padding: 6px 12px;
                border: none;
            }
        """)
        top_layout.addWidget(info_label)

        layout.addLayout(top_layout)

        # Segunda fila: instrucciones y timer
        bottom_layout = QHBoxLayout()

        # Instrucciones
        instructions = QLabel(self.exercise_data.get('instrucciones', ''))
        instructions.setStyleSheet("""
            QLabel {
                font-size: 16px;
                color: white;
                background-color: transparent;
                border: none;
            }
        """)
        instructions.setWordWrap(True)
        bottom_layout.addWidget(instructions, 3)

        bottom_layout.addStretch()

        # Timer
        self.timer_label = QLabel("⏱️ 00:00")
        self.timer_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: white;
                background-color: rgba(255,255,255,0.2);
                border-radius: 8px;
                padding: 4px 8px;
                border: none;
            }
        """)
        bottom_layout.addWidget(self.timer_label)

        layout.addLayout(bottom_layout)

        return header

    def create_footer(self) -> QFrame:
        """Crear footer con botones de acción"""
        footer = QFrame()
        footer.setStyleSheet("""
            QFrame {
                background-color: transparent;
                border: none;
            }
        """)
        footer.setFixedHeight(80)

        layout = QHBoxLayout(footer)
        layout.setContentsMargins(10, 15, 10, 15)
        layout.setSpacing(15)

        # Botón cancelar
        self.cancel_button = QPushButton("❌ Cancelar")
        self.cancel_button.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: #ff6b6b;
                border: 2px solid #ff6b6b;
                border-radius: 12px;
                padding: 12px 20px;
                font-size: 16px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: #ff6b6b;
                color: white;
            }}
        """)
        self.cancel_button.clicked.connect(self.cancel_exercise)
        layout.addWidget(self.cancel_button)

        layout.addStretch()

        # Progress indicator
        self.progress_label = QLabel("Completa el ejercicio")
        self.progress_label.setStyleSheet(f"""
            QLabel {{
                font-size: 14px;
                color: {self.settings.COLORS['text_primary']};
                background-color: transparent;
                border: none;
            }}
        """)
        layout.addWidget(self.progress_label)

        # Botón enviar
        self.submit_button = QPushButton("✅ Enviar Respuestas")
        self.submit_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.settings.COLORS['green_success']};
                color: white;
                border: none;
                border-radius: 12px;
                padding: 12px 25px;
                font-size: 16px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: #22c55e;
            }}
            QPushButton:disabled {{
                background-color: #94a3b8;
            }}
        """)
        self.submit_button.clicked.connect(self.submit_exercise)
        self.submit_button.setEnabled(False)  # Disabled por defecto
        layout.addWidget(self.submit_button)

        return footer

    def load_exercise_content(self):
        """Cargar contenido específico del ejercicio - OVERRIDE en subclases"""
        # Este método debe ser sobrescrito por las subclases
        placeholder = QLabel("⚠️ Contenido de ejercicio no implementado")
        placeholder.setStyleSheet(f"""
            QLabel {{
                font-size: 18px;
                color: {self.settings.COLORS['orange_energetic']};
                background-color: {self.settings.COLORS['orange_energetic']}15;
                border: 2px solid {self.settings.COLORS['orange_energetic']}30;
                border-radius: 12px;
                padding: 30px;
                text-align: center;
            }}
        """)
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.content_layout.addWidget(placeholder)

    def start_exercise(self):
        """Iniciar el ejercicio"""
        self.start_time = time.time()
        self.timer.start(1000)  # Actualizar cada segundo
        self.elapsed_seconds = 0
        print(f"🚀 Ejercicio iniciado: {self.exercise_data['titulo']}")

    def _update_timer(self):
        """Actualizar timer"""
        self.elapsed_seconds += 1
        minutes = self.elapsed_seconds // 60
        seconds = self.elapsed_seconds % 60
        self.timer_label.setText(f"⏱️ {minutes:02d}:{seconds:02d}")
        self.time_updated.emit(self.elapsed_seconds)

        # Verificar tiempo límite
        tiempo_limite = self.exercise_data.get('tiempo_limite', 300)
        if self.elapsed_seconds >= tiempo_limite:
            self.time_up()

    def time_up(self):
        """Tiempo agotado"""
        self.timer.stop()
        QMessageBox.warning(
            self,
            "⏰ Tiempo Agotado",
            "Se acabó el tiempo para este ejercicio.\nPuedes enviarlo ahora o cancelar."
        )
        # Permitir envío aunque el tiempo se agote
        self.submit_button.setEnabled(True)

    def validate_answers(self) -> Dict[str, Any]:
        """Validar respuestas - OVERRIDE en subclases"""
        # Este método debe ser sobrescrito por las subclases
        return {
            'is_valid': False,
            'score': 0,
            'max_score': self.exercise_data.get('puntos_maximos', 10),
            'precision': 0.0,
            'feedback': "Validación no implementada",
            'details': {}
        }

    def submit_exercise(self):
        """Enviar ejercicio completado"""
        if self.is_completed:
            return

        # Validar respuestas
        validation_result = self.validate_answers()

        if not validation_result['is_valid']:
            QMessageBox.warning(
                self,
                "⚠️ Respuestas Incompletas",
                "Por favor completa todas las respuestas antes de enviar."
            )
            return

        # Detener timer
        self.timer.stop()
        self.is_completed = True

        # Preparar resultado
        result = {
            'exercise_id': self.exercise_data.get('id', 0),
            'exercise_type': self.exercise_data.get('tipo', ''),
            'answers': self.current_answers,
            'score': validation_result['score'],
            'max_score': validation_result['max_score'],
            'precision': validation_result['precision'],
            'time_seconds': self.elapsed_seconds,
            'feedback': validation_result['feedback'],
            'details': validation_result['details'],
            'completed_at': time.time()
        }

        print(f"✅ Ejercicio completado: {result['score']}/{result['max_score']} puntos")

        # Mostrar resultado
        self.show_result_dialog(result)

        # Emitir señal
        self.exercise_completed.emit(result)

    def cancel_exercise(self):
        """Cancelar ejercicio"""
        reply = QMessageBox.question(
            self,
            "❓ Cancelar Ejercicio",
            "¿Estás seguro de que quieres cancelar este ejercicio?\nPerderás todo el progreso.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.timer.stop()
            print("❌ Ejercicio cancelado por el usuario")
            self.exercise_cancelled.emit()

    def show_result_dialog(self, result: Dict[str, Any]):
        """Mostrar diálogo con resultado del ejercicio"""
        score = result['score']
        max_score = result['max_score']
        precision = result['precision']

        # Determinar emoji y color según resultado
        if precision >= 90:
            emoji = "🌟"
            color = self.settings.COLORS['green_success']
            message = "¡Excelente trabajo!"
        elif precision >= 75:
            emoji = "⭐"
            color = self.settings.COLORS['blue_educational']
            message = "¡Muy bien hecho!"
        elif precision >= 50:
            emoji = "👍"
            color = self.settings.COLORS['orange_energetic']
            message = "Buen intento, sigue practicando"
        else:
            emoji = "💪"
            color = "#ff6b6b"
            message = "No te desanimes, ¡inténtalo de nuevo!"

        # Crear mensaje detallado
        tiempo_str = f"{self.elapsed_seconds // 60}:{self.elapsed_seconds % 60:02d}"

        msg_text = f"""
        <div style="text-align: center; font-family: 'Segoe UI', Arial;">
            <h2 style="color: {color}; margin-bottom: 10px;">
                {emoji} {message}
            </h2>

            <div style="background-color: {color}15; border-radius: 12px; padding: 20px; margin: 15px 0;">
                <h3 style="color: {color}; margin: 0 0 15px 0;">Resultados:</h3>
                <p style="font-size: 18px; margin: 5px 0;">
                    <b>Puntuación:</b> {score}/{max_score} puntos
                </p>
                <p style="font-size: 18px; margin: 5px 0;">
                    <b>Precisión:</b> {precision:.1f}%
                </p>
                <p style="font-size: 18px; margin: 5px 0;">
                    <b>Tiempo:</b> {tiempo_str}
                </p>
            </div>

            <p style="color: {self.settings.COLORS['text_primary']}; font-size: 14px;">
                {result.get('feedback', '')}
            </p>
        </div>
        """

        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Resultado del Ejercicio")
        msg_box.setTextFormat(Qt.TextFormat.RichText)
        msg_box.setText(msg_text)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()

    def update_progress(self, completed_items: int, total_items: int):
        """Actualizar indicador de progreso"""
        if total_items > 0:
            progress_text = f"Progreso: {completed_items}/{total_items}"
            self.progress_label.setText(progress_text)

            # Habilitar botón enviar si está completo
            if completed_items >= total_items:
                self.submit_button.setEnabled(True)
                self.submit_button.setText("✅ Enviar Respuestas")
            else:
                self.submit_button.setEnabled(False)
                self.submit_button.setText(f"Completa {total_items - completed_items} más")

    def get_exercise_data(self) -> Dict[str, Any]:
        """Obtener datos del ejercicio"""
        return self.exercise_data

    def get_current_answers(self) -> Dict[str, Any]:
        """Obtener respuestas actuales"""
        return self.current_answers

    def get_elapsed_time(self) -> int:
        """Obtener tiempo transcurrido en segundos"""
        return self.elapsed_seconds


class CompletarPalabraWidget(ExerciseWidget):
    """Widget específico para ejercicios de completar palabra"""

    def __init__(self, exercise_data: Dict[str, Any], parent=None):
        super().__init__(exercise_data, parent)
        print(f"📝 CompletarPalabraWidget creado")

    def load_exercise_content(self):
        """Cargar contenido de completar palabra"""
        contenido = self.exercise_data.get('contenido', {})
        oraciones = contenido.get('oraciones', [])
        opciones = contenido.get('opciones', [])

        if not oraciones:
            self.load_demo_content()
            return

        # Limpiar layout
        self.clear_content_layout()

        # Crear campos para cada oración
        self.word_inputs = []

        for i, oracion in enumerate(oraciones):
            # Frame para cada oración
            sentence_frame = QFrame()
            sentence_frame.setStyleSheet(f"""
                QFrame {{
                    background-color: {self.settings.COLORS['blue_educational']}10;
                    border: 2px solid {self.settings.COLORS['blue_educational']}30;
                    border-radius: 12px;
                    padding: 15px;
                    margin: 5px 0;
                }}
            """)

            sentence_layout = QVBoxLayout(sentence_frame)
            sentence_layout.setSpacing(10)

            # Número de pregunta
            question_num = QLabel(f"Pregunta {i + 1}")
            question_num.setStyleSheet(f"""
                QLabel {{
                    font-size: 16px;
                    font-weight: bold;
                    color: {self.settings.COLORS['blue_educational']};
                    background-color: transparent;
                    border: none;
                }}
            """)
            sentence_layout.addWidget(question_num)

            # Oración con espacio para completar
            sentence_label = QLabel(oracion)
            sentence_label.setStyleSheet(f"""
                QLabel {{
                    font-size: 18px;
                    color: {self.settings.COLORS['text_primary']};
                    background-color: transparent;
                    border: none;
                    padding: 10px 0;
                }}
            """)
            sentence_layout.addWidget(sentence_label)

            # Campo de entrada
            word_input = QLineEdit()
            word_input.setPlaceholderText("Escribe la palabra que falta...")
            word_input.setStyleSheet(f"""
                QLineEdit {{
                    font-size: 16px;
                    padding: 12px 15px;
                    border: 2px solid {self.settings.COLORS['blue_educational']}40;
                    border-radius: 8px;
                    background-color: white;
                    color: {self.settings.COLORS['text_primary']};
                }}
                QLineEdit:focus {{
                    border-color: {self.settings.COLORS['blue_educational']};
                    background-color: #f0f7ff;
                }}
            """)
            word_input.textChanged.connect(self.on_answer_changed)
            self.word_inputs.append(word_input)
            sentence_layout.addWidget(word_input)

            # Mostrar opciones si las hay
            if i < len(opciones) and opciones[i]:
                options_label = QLabel(f"Opciones: {', '.join(opciones[i])}")
                options_label.setStyleSheet(f"""
                    QLabel {{
                        font-size: 14px;
                        color: {self.settings.COLORS['text_primary']};
                        background-color: {self.settings.COLORS['orange_energetic']}15;
                        border-radius: 6px;
                        padding: 8px 12px;
                        border: none;
                    }}
                """)
                sentence_layout.addWidget(options_label)

            self.content_layout.addWidget(sentence_frame)

        # Espaciador al final
        self.content_layout.addStretch()

        # Iniciar ejercicio
        QTimer.singleShot(100, self.start_exercise)

    def load_demo_content(self):
        """Cargar contenido demo para completar palabra"""
        demo_content = {
            'oraciones': [
                'El _ato juega en el jardín',
                'La _asa está muy limpia',
                'Mi _adre cocina muy bien'
            ],
            'opciones': [
                ['gato', 'pato', 'rato'],
                ['casa', 'masa', 'tasa'],
                ['madre', 'padre']
            ]
        }

        # Actualizar datos del ejercicio
        if 'contenido' not in self.exercise_data:
            self.exercise_data['contenido'] = {}
        self.exercise_data['contenido'].update(demo_content)

        # Cargar contenido
        self.load_exercise_content()

    def clear_content_layout(self):
        """Limpiar layout de contenido"""
        while self.content_layout.count():
            child = self.content_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def on_answer_changed(self):
        """Manejar cambio en respuestas"""
        # Actualizar respuestas actuales
        self.current_answers = {}
        completed_count = 0

        for i, input_field in enumerate(self.word_inputs):
            answer = input_field.text().strip()
            self.current_answers[f'palabra_{i}'] = answer
            if answer:
                completed_count += 1

        # Actualizar progreso
        total_words = len(self.word_inputs)
        self.update_progress(completed_count, total_words)

    def validate_answers(self) -> Dict[str, Any]:
        """Validar respuestas de completar palabra"""
        respuestas_correctas = self.exercise_data.get('respuestas_correctas', [])
        puntos_maximos = self.exercise_data.get('puntos_maximos', 30)

        if not respuestas_correctas:
            return {
                'is_valid': True,
                'score': puntos_maximos,
                'max_score': puntos_maximos,
                'precision': 100.0,
                'feedback': "Ejercicio completado (modo demo)",
                'details': {}
            }

        score = 0
        total_questions = len(self.word_inputs)
        correct_answers = 0
        details = {}

        for i, input_field in enumerate(self.word_inputs):
            user_answer = input_field.text().strip().lower()

            if i < len(respuestas_correctas):
                correct_options = [opt.lower() for opt in respuestas_correctas[i]]
                is_correct = user_answer in correct_options

                if is_correct:
                    correct_answers += 1
                    points_for_question = puntos_maximos // total_questions
                    score += points_for_question

                details[f'pregunta_{i + 1}'] = {
                    'user_answer': user_answer,
                    'correct_options': correct_options,
                    'is_correct': is_correct
                }

        precision = (correct_answers / total_questions * 100) if total_questions > 0 else 0

        # Verificar que todas las respuestas estén completas
        all_completed = all(input_field.text().strip() for input_field in self.word_inputs)

        feedback_messages = []
        if correct_answers == total_questions:
            feedback_messages.append("¡Perfecto! Todas las respuestas son correctas.")
        elif correct_answers >= total_questions * 0.7:
            feedback_messages.append("¡Muy bien! La mayoría de respuestas son correctas.")
        else:
            feedback_messages.append("Algunas respuestas necesitan revisión. ¡Sigue practicando!")

        return {
            'is_valid': all_completed,
            'score': score,
            'max_score': puntos_maximos,
            'precision': precision,
            'feedback': ' '.join(feedback_messages),
            'details': details
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
        'id': 1,
        'tipo': 'Completar_Palabra',
        'titulo': 'Completa las Palabras',
        'instrucciones': 'Completa las palabras que faltan en cada oración',
        'contenido': {
            'oraciones': [
                'El _ato juega en el jardín',
                'La _asa está muy limpia',
                'Mi _adre cocina muy bien'
            ],
            'opciones': [
                ['gato', 'pato', 'rato'],
                ['casa', 'masa', 'tasa'],
                ['madre', 'padre']
            ]
        },
        'respuestas_correctas': [['gato'], ['casa'], ['madre']],
        'nivel_dificultad': 2,
        'puntos_maximos': 30,
        'tiempo_limite': 120
    }

    # Crear widget
    widget = CompletarPalabraWidget(exercise_data)
    widget.setMinimumSize(800, 600)
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
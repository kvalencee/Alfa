# =============================================================================
# AlfaIA/modules/exercises/encontrar_error_widget.py - Widget para Encontrar Errores
# =============================================================================

import re
from typing import Dict, Any, List, Tuple
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QLineEdit, QTextEdit, QScrollArea, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QTextCharFormat, QTextCursor
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


class ClickableTextWidget(QTextEdit):
    """Widget de texto clickeable para marcar errores"""

    word_clicked = pyqtSignal(str, int, int)  # palabra, inicio, fin

    def __init__(self, text: str, parent=None):
        super().__init__(parent)
        self.original_text = text
        self.marked_words = {}  # {word_index: {'word': str, 'start': int, 'end': int, 'corrected': str}}
        self.word_positions = []  # Lista de (palabra, inicio, fin)

        self.setReadOnly(True)
        self.setFixedHeight(80)

        # Configurar estilo
        self.setStyleSheet("""
            QTextEdit {
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                padding: 10px;
                font-size: 16px;
                background-color: #f8fafc;
                selection-background-color: #fef3c7;
            }
        """)

        self.setup_text()

    def setup_text(self):
        """Configurar texto y posiciones de palabras"""
        self.setPlainText(self.original_text)

        # Encontrar posiciones de palabras
        words = re.finditer(r'\b\w+\b', self.original_text)
        self.word_positions = []

        for match in words:
            word = match.group()
            start = match.start()
            end = match.end()
            self.word_positions.append((word, start, end))

    def mousePressEvent(self, event):
        """Manejar clic en texto"""
        if event.button() == Qt.MouseButton.LeftButton:
            cursor = self.cursorForPosition(event.pos())
            position = cursor.position()

            # Encontrar palabra clickeada
            for i, (word, start, end) in enumerate(self.word_positions):
                if start <= position <= end:
                    self.toggle_word_selection(i, word, start, end)
                    break

        super().mousePressEvent(event)

    def toggle_word_selection(self, word_index: int, word: str, start: int, end: int):
        """Alternar selección de palabra"""
        if word_index in self.marked_words:
            # Desmarcar palabra
            del self.marked_words[word_index]
            self.update_text_formatting()
        else:
            # Marcar palabra como error
            self.marked_words[word_index] = {
                'word': word,
                'start': start,
                'end': end,
                'corrected': ''
            }
            self.update_text_formatting()
            self.word_clicked.emit(word, start, end)

    def update_text_formatting(self):
        """Actualizar formato del texto"""
        cursor = self.textCursor()
        cursor.select(QTextCursor.SelectionType.Document)

        # Formato normal
        normal_format = QTextCharFormat()
        normal_format.setBackground(QColor("transparent"))
        normal_format.setForeground(QColor("#2C3E50"))
        cursor.setCharFormat(normal_format)

        # Aplicar formato a palabras marcadas
        for word_data in self.marked_words.values():
            cursor.setPosition(word_data['start'])
            cursor.setPosition(word_data['end'], QTextCursor.MoveMode.KeepAnchor)

            error_format = QTextCharFormat()
            error_format.setBackground(QColor("#fee2e2"))
            error_format.setForeground(QColor("#dc2626"))
            error_format.setFontWeight(QFont.Weight.Bold)
            cursor.setCharFormat(error_format)

        # Resetear cursor
        cursor.clearSelection()
        self.setTextCursor(cursor)

    def get_marked_words(self) -> Dict[int, Dict[str, Any]]:
        """Obtener palabras marcadas"""
        return self.marked_words.copy()

    def set_correction(self, word_index: int, correction: str):
        """Establecer corrección para una palabra"""
        if word_index in self.marked_words:
            self.marked_words[word_index]['corrected'] = correction


class ErrorCorrectionDialog(QMessageBox):
    """Diálogo para corregir errores"""

    def __init__(self, word: str, parent=None):
        super().__init__(parent)
        self.word = word
        self.correction = ""

        self.setWindowTitle("Corregir Error")
        self.setIcon(QMessageBox.Icon.Question)
        self.setText(f"Has marcado la palabra: <b>'{word}'</b>")
        self.setInformativeText("¿Cuál es la corrección?")

        # Campo de entrada personalizado
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText(f"Corrección para '{word}'")
        self.input_field.setStyleSheet("""
            QLineEdit {
                padding: 8px 12px;
                font-size: 14px;
                border: 2px solid #d1d5db;
                border-radius: 6px;
            }
            QLineEdit:focus {
                border-color: #4A90E2;
            }
        """)

        # No usar layout automático del QMessageBox
        self.layout().addWidget(self.input_field, 1, 1)

        # Botones personalizados
        self.addButton("Corregir", QMessageBox.ButtonRole.AcceptRole)
        self.addButton("Cancelar", QMessageBox.ButtonRole.RejectRole)

    def get_correction(self) -> str:
        """Obtener corrección ingresada"""
        return self.input_field.text().strip()


class EncontrarErrorWidget(ExerciseWidget):
    """Widget para ejercicios de encontrar errores"""

    def __init__(self, exercise_data: Dict[str, Any], parent=None):
        super().__init__(exercise_data, parent)
        self.sentence_widgets = []
        self.correction_inputs = {}  # {sentence_index: {word_index: correction}}
        print(f"🔍 EncontrarErrorWidget creado")

    def load_exercise_content(self):
        """Cargar contenido de encontrar errores"""
        contenido = self.exercise_data.get('contenido', {})
        oraciones = contenido.get('oraciones', [])

        if not oraciones:
            self.load_demo_content()
            return

        # Limpiar layout
        self.clear_content_layout()

        # Instrucciones específicas
        instruction_label = QLabel("📝 Haz clic en las palabras que tengan errores para marcarlas y corregirlas")
        instruction_label.setStyleSheet(f"""
            QLabel {{
                font-size: 16px;
                color: {self.settings.COLORS['blue_educational']};
                background-color: {self.settings.COLORS['blue_educational']}10;
                border-radius: 8px;
                padding: 12px 15px;
                border: 1px solid {self.settings.COLORS['blue_educational']}30;
                margin-bottom: 10px;
            }}
        """)
        instruction_label.setWordWrap(True)
        self.content_layout.addWidget(instruction_label)

        # Crear widgets para cada oración
        self.sentence_widgets = []
        self.correction_inputs = {}

        for i, oracion in enumerate(oraciones):
            sentence_frame = self.create_sentence_frame(i, oracion)
            self.content_layout.addWidget(sentence_frame)
            self.correction_inputs[i] = {}

        # Espaciador al final
        self.content_layout.addStretch()

        # Iniciar ejercicio
        QTimer.singleShot(100, self.start_exercise)

    def create_sentence_frame(self, index: int, oracion: str) -> QFrame:
        """Crear frame para una oración"""
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {self.settings.COLORS['white_pure']};
                border: 2px solid {self.settings.COLORS['blue_educational']}20;
                border-radius: 12px;
                padding: 15px;
                margin: 10px 0;
            }}
        """)

        layout = QVBoxLayout(frame)
        layout.setSpacing(12)

        # Número de oración
        sentence_num = QLabel(f"Oración {index + 1}")
        sentence_num.setStyleSheet(f"""
            QLabel {{
                font-size: 16px;
                font-weight: bold;
                color: {self.settings.COLORS['blue_educational']};
                background-color: transparent;
            }}
        """)
        layout.addWidget(sentence_num)

        # Widget de texto clickeable
        text_widget = ClickableTextWidget(oracion)
        text_widget.word_clicked.connect(
            lambda word, start, end, idx=index: self.on_word_clicked(idx, word, start, end))
        self.sentence_widgets.append(text_widget)
        layout.addWidget(text_widget)

        # Área para mostrar correcciones
        corrections_frame = QFrame()
        corrections_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {self.settings.COLORS['green_success']}05;
                border: 1px solid {self.settings.COLORS['green_success']}20;
                border-radius: 8px;
                padding: 10px;
            }}
        """)
        corrections_layout = QVBoxLayout(corrections_frame)

        corrections_title = QLabel("Correcciones:")
        corrections_title.setStyleSheet(f"""
            QLabel {{
                font-size: 14px;
                font-weight: bold;
                color: {self.settings.COLORS['green_success']};
            }}
        """)
        corrections_layout.addWidget(corrections_title)

        # Label para mostrar correcciones dinámicamente
        corrections_display = QLabel("Ninguna corrección aún")
        corrections_display.setStyleSheet(f"""
            QLabel {{
                font-size: 14px;
                color: {self.settings.COLORS['text_primary']};
                padding: 5px;
            }}
        """)
        corrections_display.setObjectName(f"corrections_{index}")
        corrections_layout.addWidget(corrections_display)

        layout.addWidget(corrections_frame)

        return frame

    def on_word_clicked(self, sentence_index: int, word: str, start: int, end: int):
        """Manejar clic en palabra"""
        print(f"🖱️ Palabra clickeada: '{word}' en oración {sentence_index}")

        # Mostrar diálogo de corrección
        dialog = ErrorCorrectionDialog(word, self)

        if dialog.exec() == QMessageBox.StandardButton.Ok:
            correction = dialog.get_correction()

            if correction:
                # Guardar corrección
                text_widget = self.sentence_widgets[sentence_index]
                word_positions = text_widget.word_positions

                # Encontrar índice de la palabra
                word_index = None
                for i, (w, s, e) in enumerate(word_positions):
                    if s == start and e == end:
                        word_index = i
                        break

                if word_index is not None:
                    text_widget.set_correction(word_index, correction)
                    self.correction_inputs[sentence_index][word_index] = {
                        'original': word,
                        'corrected': correction,
                        'start': start,
                        'end': end
                    }

                    # Actualizar display de correcciones
                    self.update_corrections_display(sentence_index)
                    self.update_overall_progress()
        else:
            # Si cancela, desmarcar la palabra
            text_widget = self.sentence_widgets[sentence_index]
            marked_words = text_widget.get_marked_words()

            # Encontrar y eliminar la palabra marcada
            word_index_to_remove = None
            for word_idx, word_data in marked_words.items():
                if word_data['start'] == start and word_data['end'] == end:
                    word_index_to_remove = word_idx
                    break

            if word_index_to_remove is not None:
                del text_widget.marked_words[word_index_to_remove]
                text_widget.update_text_formatting()

    def update_corrections_display(self, sentence_index: int):
        """Actualizar display de correcciones para una oración"""
        corrections = self.correction_inputs[sentence_index]

        # Encontrar el label de correcciones
        corrections_label = self.findChild(QLabel, f"corrections_{sentence_index}")

        if not corrections:
            corrections_label.setText("Ninguna corrección aún")
            return

        # Crear texto de correcciones
        corrections_text = []
        for word_data in corrections.values():
            corrections_text.append(f"'{word_data['original']}' → '{word_data['corrected']}'")

        corrections_label.setText(" | ".join(corrections_text))
        corrections_label.setStyleSheet(f"""
            QLabel {{
                font-size: 14px;
                color: {self.settings.COLORS['green_success']};
                padding: 5px;
                font-weight: 500;
            }}
        """)

    def update_overall_progress(self):
        """Actualizar progreso general"""
        total_corrections = sum(len(corrections) for corrections in self.correction_inputs.values())

        # Actualizar respuestas actuales
        self.current_answers = {}
        for sentence_idx, corrections in self.correction_inputs.items():
            self.current_answers[f'sentence_{sentence_idx}'] = corrections

        # Actualizar indicador de progreso
        if total_corrections > 0:
            self.update_progress(total_corrections, total_corrections)  # Asumimos que cualquier corrección es válida
        else:
            self.update_progress(0, 1)  # Necesita al menos una corrección

    def load_demo_content(self):
        """Cargar contenido demo"""
        demo_content = {
            'oraciones': [
                'Los niña juegan en el parque',
                'Ayer fuí al cine con mis amigos',
                'El agua esta muy fria',
                'Me gusta mucho la musica clasica'
            ]
        }

        # Actualizar datos del ejercicio
        if 'contenido' not in self.exercise_data:
            self.exercise_data['contenido'] = {}
        self.exercise_data['contenido'].update(demo_content)

        # Establecer respuestas correctas demo
        self.exercise_data['respuestas_correctas'] = [
            {'posicion': 0, 'error': 'niña', 'correccion': 'niñas'},
            {'posicion': 1, 'error': 'fuí', 'correccion': 'fui'},
            {'posicion': 2, 'error': 'esta', 'correccion': 'está'},
            {'posicion': 2, 'error': 'fria', 'correccion': 'fría'},
            {'posicion': 3, 'error': 'musica', 'correccion': 'música'},
            {'posicion': 3, 'error': 'clasica', 'correccion': 'clásica'}
        ]

        # Cargar contenido
        self.load_exercise_content()

    def clear_content_layout(self):
        """Limpiar layout de contenido"""
        while self.content_layout.count():
            child = self.content_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def validate_answers(self) -> Dict[str, Any]:
        """Validar respuestas de encontrar errores"""
        respuestas_correctas = self.exercise_data.get('respuestas_correctas', [])
        puntos_maximos = self.exercise_data.get('puntos_maximos', 40)

        if not respuestas_correctas:
            # Modo demo - considerar cualquier corrección como válida
            total_corrections = sum(len(corrections) for corrections in self.correction_inputs.values())
            if total_corrections > 0:
                return {
                    'is_valid': True,
                    'score': puntos_maximos,
                    'max_score': puntos_maximos,
                    'precision': 100.0,
                    'feedback': f"¡Bien hecho! Encontraste {total_corrections} errores (modo demo)",
                    'details': {'total_corrections': total_corrections}
                }
            else:
                return {
                    'is_valid': False,
                    'score': 0,
                    'max_score': puntos_maximos,
                    'precision': 0.0,
                    'feedback': "Necesitas encontrar al menos un error",
                    'details': {}
                }

        # Validación real contra respuestas correctas
        score = 0
        total_errors = len(respuestas_correctas)
        found_errors = 0
        correct_corrections = 0
        details = {}

        # Crear diccionario de errores por oración
        errors_by_sentence = {}
        for error in respuestas_correctas:
            sentence_idx = error['posicion']
            if sentence_idx not in errors_by_sentence:
                errors_by_sentence[sentence_idx] = []
            errors_by_sentence[sentence_idx].append(error)

        # Verificar correcciones del usuario
        for sentence_idx, user_corrections in self.correction_inputs.items():
            sentence_details = {}

            if sentence_idx in errors_by_sentence:
                expected_errors = errors_by_sentence[sentence_idx]

                for word_idx, correction_data in user_corrections.items():
                    original_word = correction_data['original'].lower()
                    corrected_word = correction_data['corrected'].lower()

                    # Buscar si este error está en las respuestas correctas
                    error_found = False
                    for expected_error in expected_errors:
                        if (expected_error['error'].lower() == original_word and
                                expected_error['correccion'].lower() == corrected_word):
                            error_found = True
                            found_errors += 1
                            correct_corrections += 1
                            points_per_error = puntos_maximos // total_errors
                            score += points_per_error
                            break

                    sentence_details[f'correction_{word_idx}'] = {
                        'original': original_word,
                        'corrected': corrected_word,
                        'is_correct': error_found
                    }

            details[f'sentence_{sentence_idx}'] = sentence_details

        # Calcular precisión
        total_user_corrections = sum(len(corrections) for corrections in self.correction_inputs.values())
        if total_user_corrections > 0:
            precision = (correct_corrections / total_user_corrections) * 100
        else:
            precision = 0.0

        # Verificar que se haya encontrado al menos un error
        has_corrections = total_user_corrections > 0

        # Generar feedback
        feedback_messages = []
        if correct_corrections == total_errors:
            feedback_messages.append("¡Perfecto! Encontraste todos los errores correctamente.")
        elif correct_corrections >= total_errors * 0.7:
            feedback_messages.append(f"¡Muy bien! Encontraste {correct_corrections} de {total_errors} errores.")
        elif correct_corrections > 0:
            feedback_messages.append(f"Buen intento. Encontraste {correct_corrections} de {total_errors} errores.")
        else:
            feedback_messages.append("No encontraste los errores correctos. ¡Sigue practicando!")

        if total_user_corrections > correct_corrections:
            extra_corrections = total_user_corrections - correct_corrections
            feedback_messages.append(f"Marcaste {extra_corrections} palabras que no tenían errores.")

        return {
            'is_valid': has_corrections,
            'score': score,
            'max_score': puntos_maximos,
            'precision': precision,
            'feedback': ' '.join(feedback_messages),
            'details': {
                'total_errors': total_errors,
                'found_errors': found_errors,
                'correct_corrections': correct_corrections,
                'user_corrections': total_user_corrections,
                'sentences': details
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
        'id': 2,
        'tipo': 'Encontrar_Error',
        'titulo': 'Encuentra los Errores',
        'instrucciones': 'Haz clic en las palabras que tengan errores ortográficos o gramaticales',
        'contenido': {
            'oraciones': [
                'Los niña juegan en el parque',
                'Ayer fuí al cine con mis amigos',
                'El agua esta muy fria',
                'Me gusta mucho la musica clasica'
            ]
        },
        'respuestas_correctas': [
            {'posicion': 0, 'error': 'niña', 'correccion': 'niñas'},
            {'posicion': 1, 'error': 'fuí', 'correccion': 'fui'},
            {'posicion': 2, 'error': 'esta', 'correccion': 'está'},
            {'posicion': 2, 'error': 'fria', 'correccion': 'fría'},
            {'posicion': 3, 'error': 'musica', 'correccion': 'música'},
            {'posicion': 3, 'error': 'clasica', 'correccion': 'clásica'}
        ],
        'nivel_dificultad': 4,
        'puntos_maximos': 60,
        'tiempo_limite': 300
    }

    # Crear widget
    widget = EncontrarErrorWidget(exercise_data)
    widget.setMinimumSize(900, 700)
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
# =============================================================================
# AlfaIA/modules/exercises/clasificar_palabra_widget.py - Widget para Clasificar Palabras
# =============================================================================

from typing import Dict, Any, List
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QPushButton, QFrame, QScrollArea, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QMimeData, QPoint
from PyQt6.QtGui import QDrag, QPainter, QPixmap, QFont
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
            'purple_creative': '#9013FE',
            'text_primary': '#2C3E50',
            'white_pure': '#FFFFFF'
        }


class DraggableWordLabel(QLabel):
    """Label de palabra que se puede arrastrar"""

    def __init__(self, word: str, word_index: int, parent=None):
        super().__init__(word, parent)
        self.word = word
        self.word_index = word_index
        self.original_parent = None
        self.is_placed = False

        self.setFixedSize(120, 50)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Estilo inicial
        self.setStyleSheet("""
            QLabel {
                background-color: #f0f7ff;
                border: 2px solid #4A90E2;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 600;
                color: #4A90E2;
                padding: 5px;
            }
            QLabel:hover {
                background-color: #e0f0ff;
                border-color: #3a7bd5;
            }
        """)

    def mousePressEvent(self, event):
        """Iniciar arrastre"""
        if event.button() == Qt.MouseButton.LeftButton:
            # Crear datos de arrastre
            drag = QDrag(self)
            mime_data = QMimeData()
            mime_data.setText(f"{self.word_index}:{self.word}")
            drag.setMimeData(mime_data)

            # Crear pixmap para el arrastre
            pixmap = QPixmap(self.size())
            self.render(pixmap)
            drag.setPixmap(pixmap)
            drag.setHotSpot(event.pos())

            # Ejecutar arrastre
            result = drag.exec(Qt.DropAction.MoveAction)

            if result == Qt.DropAction.MoveAction:
                # Si se movió exitosamente, ocultar el original
                self.hide()

    def set_placed_style(self):
        """Aplicar estilo cuando está colocado"""
        self.is_placed = True
        self.setStyleSheet("""
            QLabel {
                background-color: #f0fdf4;
                border: 2px solid #22c55e;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 600;
                color: #22c55e;
                padding: 5px;
            }
        """)

    def set_original_style(self):
        """Restaurar estilo original"""
        self.is_placed = False
        self.setStyleSheet("""
            QLabel {
                background-color: #f0f7ff;
                border: 2px solid #4A90E2;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 600;
                color: #4A90E2;
                padding: 5px;
            }
            QLabel:hover {
                background-color: #e0f0ff;
                border-color: #3a7bd5;
            }
        """)


class DropCategoryFrame(QFrame):
    """Frame donde se pueden soltar las palabras"""

    word_dropped = pyqtSignal(str, int, str)  # categoria, word_index, word
    word_removed = pyqtSignal(str, int)  # categoria, word_index

    def __init__(self, category: str, color: str, parent=None):
        super().__init__(parent)
        self.category = category
        self.color = color
        self.dropped_words = {}  # {word_index: DraggableWordLabel}

        self.setAcceptDrops(True)
        self.setMinimumSize(200, 300)

        # Layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(15, 15, 15, 15)
        self.layout.setSpacing(10)

        # Título de categoría
        self.title_label = QLabel(category)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet(f"""
            QLabel {{
                background-color: {color};
                color: white;
                border-radius: 8px;
                padding: 12px;
                font-size: 16px;
                font-weight: bold;
                margin-bottom: 10px;
            }}
        """)
        self.layout.addWidget(self.title_label)

        # Área de contenido
        self.content_area = QFrame()
        self.content_area.setStyleSheet(f"""
            QFrame {{
                border: 2px dashed {color}40;
                border-radius: 8px;
                background-color: {color}05;
                min-height: 220px;
            }}
        """)

        self.content_layout = QVBoxLayout(self.content_area)
        self.content_layout.setSpacing(8)

        # Label de instrucción
        self.instruction_label = QLabel("Arrastra palabras aquí")
        self.instruction_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.instruction_label.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-size: 14px;
                font-style: italic;
                background-color: transparent;
                border: none;
                padding: 20px;
            }}
        """)
        self.content_layout.addWidget(self.instruction_label)

        self.content_layout.addStretch()
        self.layout.addWidget(self.content_area)

        # Estilo del frame principal
        self.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 1px solid {color}20;
                border-radius: 12px;
            }}
        """)

    def dragEnterEvent(self, event):
        """Manejar entrada de arrastre"""
        if event.mimeData().hasText():
            event.acceptProposedAction()
            # Resaltar área de drop
            self.content_area.setStyleSheet(f"""
                QFrame {{
                    border: 3px dashed {self.color};
                    border-radius: 8px;
                    background-color: {self.color}15;
                    min-height: 220px;
                }}
            """)

    def dragLeaveEvent(self, event):
        """Manejar salida de arrastre"""
        # Restaurar estilo normal
        self.content_area.setStyleSheet(f"""
            QFrame {{
                border: 2px dashed {self.color}40;
                border-radius: 8px;
                background-color: {self.color}05;
                min-height: 220px;
            }}
        """)

    def dropEvent(self, event):
        """Manejar soltar palabra"""
        if event.mimeData().hasText():
            data = event.mimeData().text()
            word_index, word = data.split(':', 1)
            word_index = int(word_index)

            # Crear nueva etiqueta para la palabra
            word_label = DraggableWordLabel(word, word_index)
            word_label.set_placed_style()

            # Agregar evento de doble clic para quitar
            word_label.mouseDoubleClickEvent = lambda e: self.remove_word(word_index)

            # Agregar al layout
            if self.instruction_label.isVisible():
                self.instruction_label.hide()

            self.content_layout.insertWidget(0, word_label)
            self.dropped_words[word_index] = word_label

            # Restaurar estilo del área
            self.dragLeaveEvent(None)

            # Emitir señal
            self.word_dropped.emit(self.category, word_index, word)

            event.acceptProposedAction()

    def remove_word(self, word_index: int):
        """Quitar palabra de la categoría"""
        if word_index in self.dropped_words:
            word_label = self.dropped_words[word_index]
            word_label.deleteLater()
            del self.dropped_words[word_index]

            # Mostrar instrucción si no hay palabras
            if not self.dropped_words:
                self.instruction_label.show()

            # Emitir señal
            self.word_removed.emit(self.category, word_index)

    def get_dropped_words(self) -> Dict[int, str]:
        """Obtener palabras soltadas en esta categoría"""
        return {idx: label.word for idx, label in self.dropped_words.items()}

    def clear_words(self):
        """Limpiar todas las palabras"""
        for word_index in list(self.dropped_words.keys()):
            self.remove_word(word_index)


class ClasificarPalabraWidget(ExerciseWidget):
    """Widget para ejercicios de clasificar palabras"""

    def __init__(self, exercise_data: Dict[str, Any], parent=None):
        super().__init__(exercise_data, parent)
        self.word_labels = []
        self.category_frames = []
        self.category_assignments = {}  # {word_index: category}
        print(f"📚 ClasificarPalabraWidget creado")

    def load_exercise_content(self):
        """Cargar contenido de clasificar palabras"""
        contenido = self.exercise_data.get('contenido', {})
        palabras = contenido.get('palabras', [])
        categorias = contenido.get('categorias', [])

        if not palabras or not categorias:
            self.load_demo_content()
            return

        # Limpiar layout
        self.clear_content_layout()

        # Instrucciones específicas
        instruction_label = QLabel("🎯 Arrastra cada palabra a su categoría gramatical correcta")
        instruction_label.setStyleSheet(f"""
            QLabel {{
                font-size: 16px;
                color: {self.settings.COLORS['blue_educational']};
                background-color: {self.settings.COLORS['blue_educational']}10;
                border-radius: 8px;
                padding: 12px 15px;
                border: 1px solid {self.settings.COLORS['blue_educational']}30;
                margin-bottom: 15px;
            }}
        """)
        instruction_label.setWordWrap(True)
        self.content_layout.addWidget(instruction_label)

        # Área de palabras para arrastrar
        words_frame = self.create_words_area(palabras)
        self.content_layout.addWidget(words_frame)

        # Área de categorías
        categories_frame = self.create_categories_area(categorias)
        self.content_layout.addWidget(categories_frame)

        # Botón para resetear
        reset_button = QPushButton("🔄 Resetear Todas")
        reset_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.settings.COLORS['orange_energetic']};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: 600;
                margin: 10px 0;
            }}
            QPushButton:hover {{
                background-color: #e59400;
            }}
        """)
        reset_button.clicked.connect(self.reset_all_words)
        self.content_layout.addWidget(reset_button)

        # Espaciador al final
        self.content_layout.addStretch()

        # Inicializar estado
        self.category_assignments = {}

        # Iniciar ejercicio
        QTimer.singleShot(100, self.start_exercise)

    def create_words_area(self, palabras: List[str]) -> QFrame:
        """Crear área con palabras para arrastrar"""
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {self.settings.COLORS['blue_educational']}08;
                border: 2px solid {self.settings.COLORS['blue_educational']}20;
                border-radius: 12px;
                padding: 15px;
            }}
        """)

        layout = QVBoxLayout(frame)
        layout.setSpacing(15)

        # Título
        title = QLabel("📝 Palabras para clasificar:")
        title.setStyleSheet(f"""
            QLabel {{
                font-size: 18px;
                font-weight: bold;
                color: {self.settings.COLORS['blue_educational']};
                background-color: transparent;
                margin-bottom: 10px;
            }}
        """)
        layout.addWidget(title)

        # Grid de palabras
        words_grid = QGridLayout()
        words_grid.setSpacing(10)

        self.word_labels = []
        for i, palabra in enumerate(palabras):
            word_label = DraggableWordLabel(palabra, i)
            self.word_labels.append(word_label)

            row = i // 4  # 4 palabras por fila
            col = i % 4
            words_grid.addWidget(word_label, row, col)

        # Widget contenedor para el grid
        words_widget = QWidget()
        words_widget.setLayout(words_grid)
        layout.addWidget(words_widget)

        return frame

    def create_categories_area(self, categorias: List[str]) -> QFrame:
        """Crear área de categorías"""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: transparent;
                border: none;
            }
        """)

        layout = QVBoxLayout(frame)
        layout.setSpacing(15)

        # Título
        title = QLabel("📚 Categorías gramaticales:")
        title.setStyleSheet(f"""
            QLabel {{
                font-size: 18px;
                font-weight: bold;
                color: {self.settings.COLORS['text_primary']};
                margin-bottom: 10px;
            }}
        """)
        layout.addWidget(title)

        # Grid de categorías
        categories_grid = QGridLayout()
        categories_grid.setSpacing(15)

        # Colores para categorías
        category_colors = [
            self.settings.COLORS['blue_educational'],
            self.settings.COLORS['green_success'],
            self.settings.COLORS['orange_energetic'],
            self.settings.COLORS['purple_creative'],
            '#e74c3c',  # Rojo
            '#f39c12'  # Naranja oscuro
        ]

        self.category_frames = []
        for i, categoria in enumerate(categorias):
            color = category_colors[i % len(category_colors)]

            category_frame = DropCategoryFrame(categoria, color)
            category_frame.word_dropped.connect(self.on_word_dropped)
            category_frame.word_removed.connect(self.on_word_removed)
            self.category_frames.append(category_frame)

            row = i // 3  # 3 categorías por fila
            col = i % 3
            categories_grid.addWidget(category_frame, row, col)

        # Widget contenedor para el grid
        categories_widget = QWidget()
        categories_widget.setLayout(categories_grid)
        layout.addWidget(categories_widget)

        return frame

    def on_word_dropped(self, category: str, word_index: int, word: str):
        """Manejar palabra soltada en categoría"""
        print(f"📍 Palabra '{word}' soltada en '{category}'")

        # Actualizar asignaciones
        self.category_assignments[word_index] = category

        # Actualizar progreso
        self.update_classification_progress()

    def on_word_removed(self, category: str, word_index: int):
        """Manejar palabra removida de categoría"""
        print(f"🗑️ Palabra removida de '{category}'")

        # Remover de asignaciones
        if word_index in self.category_assignments:
            del self.category_assignments[word_index]

        # Mostrar palabra original de nuevo
        if word_index < len(self.word_labels):
            self.word_labels[word_index].show()
            self.word_labels[word_index].set_original_style()

        # Actualizar progreso
        self.update_classification_progress()

    def update_classification_progress(self):
        """Actualizar progreso de clasificación"""
        total_words = len(self.word_labels)
        classified_words = len(self.category_assignments)

        # Actualizar respuestas actuales
        self.current_answers = self.category_assignments.copy()

        # Actualizar indicador de progreso
        self.update_progress(classified_words, total_words)

    def reset_all_words(self):
        """Resetear todas las palabras"""
        reply = QMessageBox.question(
            self,
            "🔄 Resetear",
            "¿Estás seguro de que quieres resetear todas las clasificaciones?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Limpiar todas las categorías
            for category_frame in self.category_frames:
                category_frame.clear_words()

            # Mostrar todas las palabras originales
            for word_label in self.word_labels:
                word_label.show()
                word_label.set_original_style()

            # Limpiar asignaciones
            self.category_assignments = {}

            # Actualizar progreso
            self.update_classification_progress()

    def load_demo_content(self):
        """Cargar contenido demo"""
        demo_content = {
            'palabras': ['correr', 'casa', 'bonito', 'rápidamente', 'con', 'y'],
            'categorias': ['Verbo', 'Sustantivo', 'Adjetivo', 'Adverbio', 'Preposición', 'Conjunción']
        }

        # Actualizar datos del ejercicio
        if 'contenido' not in self.exercise_data:
            self.exercise_data['contenido'] = {}
        self.exercise_data['contenido'].update(demo_content)

        # Establecer respuestas correctas demo
        self.exercise_data['respuestas_correctas'] = {
            'correr': 'Verbo',
            'casa': 'Sustantivo',
            'bonito': 'Adjetivo',
            'rápidamente': 'Adverbio',
            'con': 'Preposición',
            'y': 'Conjunción'
        }

        # Cargar contenido
        self.load_exercise_content()

    def clear_content_layout(self):
        """Limpiar layout de contenido"""
        while self.content_layout.count():
            child = self.content_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def validate_answers(self) -> Dict[str, Any]:
        """Validar respuestas de clasificar palabras"""
        respuestas_correctas = self.exercise_data.get('respuestas_correctas', {})
        puntos_maximos = self.exercise_data.get('puntos_maximos', 60)

        if not respuestas_correctas:
            # Modo demo - considerar cualquier clasificación como válida
            total_classified = len(self.category_assignments)
            total_words = len(self.word_labels)

            if total_classified == total_words:
                return {
                    'is_valid': True,
                    'score': puntos_maximos,
                    'max_score': puntos_maximos,
                    'precision': 100.0,
                    'feedback': f"¡Bien hecho! Clasificaste todas las {total_words} palabras (modo demo)",
                    'details': {'total_classified': total_classified}
                }
            else:
                return {
                    'is_valid': False,
                    'score': 0,
                    'max_score': puntos_maximos,
                    'precision': 0.0,
                    'feedback': f"Clasifica las {total_words - total_classified} palabras restantes",
                    'details': {}
                }

        # Validación real contra respuestas correctas
        score = 0
        total_words = len(respuestas_correctas)
        correct_classifications = 0
        details = {}

        # Obtener palabras del contenido
        palabras = self.exercise_data.get('contenido', {}).get('palabras', [])

        for word_index, assigned_category in self.category_assignments.items():
            if word_index < len(palabras):
                word = palabras[word_index]
                correct_category = respuestas_correctas.get(word, '')

                is_correct = assigned_category == correct_category
                if is_correct:
                    correct_classifications += 1
                    points_per_word = puntos_maximos // total_words
                    score += points_per_word

                details[word] = {
                    'assigned': assigned_category,
                    'correct': correct_category,
                    'is_correct': is_correct
                }

        # Verificar palabras no clasificadas
        unclassified_words = []
        for i, word in enumerate(palabras):
            if i not in self.category_assignments:
                unclassified_words.append(word)
                details[word] = {
                    'assigned': 'Sin clasificar',
                    'correct': respuestas_correctas.get(word, ''),
                    'is_correct': False
                }

        # Calcular precisión
        total_classified = len(self.category_assignments)
        if total_classified > 0:
            precision = (correct_classifications / total_classified) * 100
        else:
            precision = 0.0

        # Verificar que todas las palabras estén clasificadas
        all_classified = len(self.category_assignments) == len(palabras)

        # Generar feedback
        feedback_messages = []
        if correct_classifications == total_words:
            feedback_messages.append("¡Perfecto! Todas las clasificaciones son correctas.")
        elif correct_classifications >= total_words * 0.8:
            feedback_messages.append(
                f"¡Muy bien! {correct_classifications} de {total_words} clasificaciones correctas.")
        elif correct_classifications > 0:
            feedback_messages.append(
                f"Buen intento. {correct_classifications} de {total_words} clasificaciones correctas.")
        else:
            feedback_messages.append("Las clasificaciones necesitan revisión. ¡Sigue practicando!")

        if unclassified_words:
            feedback_messages.append(f"Faltan por clasificar: {', '.join(unclassified_words)}")

        incorrect_count = total_classified - correct_classifications
        if incorrect_count > 0:
            feedback_messages.append(f"{incorrect_count} palabras están en categorías incorrectas.")

        return {
            'is_valid': all_classified,
            'score': score,
            'max_score': puntos_maximos,
            'precision': precision,
            'feedback': ' '.join(feedback_messages),
            'details': {
                'total_words': total_words,
                'correct_classifications': correct_classifications,
                'total_classified': total_classified,
                'unclassified_words': unclassified_words,
                'classifications': details
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
        'id': 3,
        'tipo': 'Clasificar_Palabra',
        'titulo': 'Clasifica las Palabras',
        'instrucciones': 'Arrastra cada palabra a su categoría gramatical correcta',
        'contenido': {
            'palabras': ['correr', 'casa', 'bonito', 'rápidamente', 'con', 'y'],
            'categorias': ['Verbo', 'Sustantivo', 'Adjetivo', 'Adverbio', 'Preposición', 'Conjunción']
        },
        'respuestas_correctas': {
            'correr': 'Verbo',
            'casa': 'Sustantivo',
            'bonito': 'Adjetivo',
            'rápidamente': 'Adverbio',
            'con': 'Preposición',
            'y': 'Conjunción'
        },
        'nivel_dificultad': 3,
        'puntos_maximos': 60,
        'tiempo_limite': 150
    }

    # Crear widget
    widget = ClasificarPalabraWidget(exercise_data)
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
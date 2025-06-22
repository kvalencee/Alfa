# =============================================================================
# AlfaIA/modules/exercises/ordenar_frase_widget.py - Widget para Ordenar Frases (NUEVO)
# =============================================================================

import random
from typing import Dict, Any, List
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QMessageBox, QGridLayout, QSpacerItem, QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QMimeData, QPoint
from PyQt6.QtGui import QDrag, QPixmap, QFont
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


class WordCard(QLabel):
    """Tarjeta simple de palabra"""

    def __init__(self, word: str, word_id: str, parent=None):
        super().__init__(word, parent)
        self.word = word
        self.word_id = word_id
        self.is_placed = False

        # Tamaño dinámico basado en la longitud de la palabra
        min_width = max(80, len(word) * 12 + 20)
        self.setFixedSize(min_width, 45)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        # Estilo mejorado
        self.setStyleSheet("""
            QLabel {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, 
                           stop: 0 #fff7ed, stop: 1 #fed7aa);
                border: 2px solid #f59e0b;
                border-radius: 12px;
                font-size: 15px;
                font-weight: 600;
                color: #ea580c;
                padding: 8px 12px;
                margin: 3px;
            }
            QLabel:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, 
                           stop: 0 #fed7aa, stop: 1 #fdba74);
                border-color: #ea580c;
                transform: translateY(-2px);
                box-shadow: 0 4px 8px rgba(245, 158, 11, 0.3);
            }
        """)

    def mousePressEvent(self, event):
        """Iniciar arrastre"""
        if event.button() == Qt.MouseButton.LeftButton and not self.is_placed:
            drag = QDrag(self)
            mime_data = QMimeData()
            mime_data.setText(f"{self.word_id}|{self.word}")
            drag.setMimeData(mime_data)

            # Crear imagen del arrastre con sombra
            pixmap = QPixmap(self.size())
            pixmap.fill(Qt.GlobalColor.transparent)
            self.render(pixmap)
            drag.setPixmap(pixmap)
            drag.setHotSpot(event.pos())

            # Ejecutar arrastre
            result = drag.exec(Qt.DropAction.MoveAction)

            if result == Qt.DropAction.MoveAction:
                self.hide()

    def set_placed_style(self):
        """Estilo cuando está colocada"""
        self.is_placed = True
        self.setStyleSheet("""
            QLabel {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, 
                           stop: 0 #f0fdf4, stop: 1 #dcfce7);
                border: 2px solid #22c55e;
                border-radius: 12px;
                font-size: 15px;
                font-weight: 600;
                color: #16a34a;
                padding: 8px 12px;
                margin: 3px;
            }
        """)

    def set_original_style(self):
        """Restaurar estilo original"""
        self.is_placed = False
        self.setStyleSheet("""
            QLabel {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, 
                           stop: 0 #fff7ed, stop: 1 #fed7aa);
                border: 2px solid #f59e0b;
                border-radius: 12px;
                font-size: 15px;
                font-weight: 600;
                color: #ea580c;
                padding: 8px 12px;
                margin: 3px;
            }
            QLabel:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, 
                           stop: 0 #fed7aa, stop: 1 #fdba74);
                border-color: #ea580c;
                transform: translateY(-2px);
                box-shadow: 0 4px 8px rgba(245, 158, 11, 0.3);
            }
        """)


class SentenceSlot(QFrame):
    """Slot para una palabra en la oración"""

    word_dropped = pyqtSignal(str, str)  # word_id, word
    word_removed = pyqtSignal()

    def __init__(self, position: int, parent=None):
        super().__init__(parent)
        self.position = position
        self.word_card = None
        self.setAcceptDrops(True)

        # Tamaño más grande y mejor proporcionado
        self.setFixedSize(140, 70)
        self.setup_ui()

    def setup_ui(self):
        """Configurar interfaz mejorada"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)

        # Número de posición más elegante
        self.position_label = QLabel(str(self.position + 1))
        self.position_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.position_label.setStyleSheet("""
            QLabel {
                font-size: 11px;
                color: #6b7280;
                font-weight: bold;
                background-color: #f3f4f6;
                border-radius: 10px;
                padding: 2px 8px;
                margin-bottom: 2px;
            }
        """)
        layout.addWidget(self.position_label)

        # Área de drop mejorada
        self.drop_area = QFrame()
        self.drop_area.setStyleSheet("""
            QFrame {
                background-color: #fafafa;
                border: 3px dashed #d1d5db;
                border-radius: 12px;
                min-height: 45px;
            }
        """)
        layout.addWidget(self.drop_area)

        # Layout para la palabra
        self.word_layout = QVBoxLayout(self.drop_area)
        self.word_layout.setContentsMargins(4, 4, 4, 4)
        self.word_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Placeholder icon
        self.placeholder = QLabel("📝")
        self.placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.placeholder.setStyleSheet("""
            QLabel {
                font-size: 20px;
                color: #d1d5db;
                background-color: transparent;
                border: none;
            }
        """)
        self.word_layout.addWidget(self.placeholder)

    def dragEnterEvent(self, event):
        """Entrada de arrastre mejorada"""
        if event.mimeData().hasText():
            event.acceptProposedAction()
            self.drop_area.setStyleSheet("""
                QFrame {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, 
                               stop: 0 #f0f9ff, stop: 1 #e0f2fe);
                    border: 3px dashed #3b82f6;
                    border-radius: 12px;
                    min-height: 45px;
                }
            """)

    def dragLeaveEvent(self, event):
        """Salida de arrastre"""
        if not self.word_card:
            self.drop_area.setStyleSheet("""
                QFrame {
                    background-color: #fafafa;
                    border: 3px dashed #d1d5db;
                    border-radius: 12px;
                    min-height: 45px;
                }
            """)

    def dropEvent(self, event):
        """Soltar palabra"""
        if event.mimeData().hasText():
            data = event.mimeData().text()
            word_id, word = data.split('|', 1)

            # Si ya hay una palabra, quitarla
            if self.word_card:
                self.remove_word()

            # Crear nueva palabra
            self.place_word(word_id, word)

            # Emitir señal
            self.word_dropped.emit(word_id, word)

            event.acceptProposedAction()

    def place_word(self, word_id: str, word: str):
        """Colocar palabra en el slot"""
        # Ocultar placeholder
        self.placeholder.hide()

        # Crear palabra con tamaño ajustado
        self.word_card = WordCard(word, word_id)
        self.word_card.set_placed_style()

        # Doble clic para quitar
        self.word_card.mouseDoubleClickEvent = self.on_double_click

        self.word_layout.addWidget(self.word_card)

        # Cambiar estilo del slot
        self.drop_area.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, 
                           stop: 0 #f0fdf4, stop: 1 #dcfce7);
                border: 3px solid #22c55e;
                border-radius: 12px;
                min-height: 45px;
            }
        """)

    def remove_word(self):
        """Quitar palabra del slot"""
        if self.word_card:
            word_id = self.word_card.word_id
            self.word_card.deleteLater()
            self.word_card = None

            # Mostrar placeholder de nuevo
            self.placeholder.show()

            # Restaurar estilo
            self.drop_area.setStyleSheet("""
                QFrame {
                    background-color: #fafafa;
                    border: 3px dashed #d1d5db;
                    border-radius: 12px;
                    min-height: 45px;
                }
            """)

            # Emitir señal
            self.word_removed.emit()

            return word_id
        return None

    def on_double_click(self, event):
        """Manejar doble clic para quitar palabra"""
        if self.word_card:
            # Quitar palabra y devolverla al área original
            self.remove_word()

    def get_word(self) -> str:
        """Obtener palabra actual"""
        return self.word_card.word if self.word_card else ""

    def is_empty(self) -> bool:
        """Verificar si está vacío"""
        return self.word_card is None


class SentenceBuilder(QFrame):
    """Constructor de una oración mejorado"""

    sentence_completed = pyqtSignal()
    word_placed = pyqtSignal(int, str, str)  # position, word_id, word
    word_removed_from_sentence = pyqtSignal(int, str)  # position, word_id

    def __init__(self, sentence_index: int, correct_sentence: str, parent=None):
        super().__init__(parent)
        self.sentence_index = sentence_index
        self.correct_words = correct_sentence.split()
        self.slots = []

        self.setup_ui()

    def setup_ui(self):
        """Configurar interfaz mejorada"""
        settings = Settings()

        # Estilo más elegante para el frame
        self.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, 
                           stop: 0 #ffffff, stop: 1 #f8fafc);
                border: 2px solid {settings.COLORS['blue_educational']}40;
                border-radius: 16px;
                padding: 20px;
                margin: 12px 0;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(16)

        # Header más elegante
        header_layout = QHBoxLayout()

        # Título con mejor diseño
        title = QLabel(f"📝 Oración {self.sentence_index + 1}")
        title.setStyleSheet(f"""
            QLabel {{
                font-size: 18px;
                font-weight: bold;
                color: {settings.COLORS['blue_educational']};
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, 
                           stop: 0 {settings.COLORS['blue_educational']}15, 
                           stop: 1 {settings.COLORS['blue_educational']}05);
                padding: 10px 16px;
                border-radius: 12px;
                border: 1px solid {settings.COLORS['blue_educational']}30;
            }}
        """)
        header_layout.addWidget(title)

        header_layout.addStretch()

        # Progreso más visible
        self.progress_label = QLabel(f"0 / {len(self.correct_words)} palabras")
        self.progress_label.setStyleSheet(f"""
            QLabel {{
                font-size: 14px;
                font-weight: 600;
                color: {settings.COLORS['text_primary']};
                background-color: #f1f5f9;
                padding: 8px 12px;
                border-radius: 10px;
                border: 1px solid #e2e8f0;
            }}
        """)
        header_layout.addWidget(self.progress_label)

        layout.addLayout(header_layout)

        # Pista más elegante
        hint = self.generate_hint()
        hint_label = QLabel(f"💡 Pista: {hint}")
        hint_label.setStyleSheet(f"""
            QLabel {{
                font-size: 15px;
                color: {settings.COLORS['purple_creative']};
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, 
                           stop: 0 {settings.COLORS['purple_creative']}08, 
                           stop: 1 {settings.COLORS['purple_creative']}03);
                padding: 12px 16px;
                border-radius: 10px;
                border: 1px solid {settings.COLORS['purple_creative']}20;
                font-style: italic;
                font-weight: 500;
            }}
        """)
        layout.addWidget(hint_label)

        # Contenedor para slots con mejor espaciado
        slots_container = QFrame()
        slots_container.setStyleSheet("""
            QFrame {
                background-color: rgba(248, 250, 252, 0.8);
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                padding: 15px;
            }
        """)

        slots_layout = QHBoxLayout(slots_container)
        slots_layout.setSpacing(12)
        slots_layout.setContentsMargins(10, 10, 10, 10)

        # Añadir slots con mejor distribución
        for i in range(len(self.correct_words)):
            slot = SentenceSlot(i)
            slot.word_dropped.connect(lambda word_id, word, pos=i: self.on_word_placed(pos, word_id, word))
            slot.word_removed.connect(lambda pos=i: self.on_word_removed(pos))
            self.slots.append(slot)
            slots_layout.addWidget(slot)

        # Añadir stretch para centrar si hay pocas palabras
        if len(self.correct_words) < 6:
            slots_layout.addStretch()

        layout.addWidget(slots_container)

    def generate_hint(self) -> str:
        """Generar pista mejorada"""
        hints = []
        for word in self.correct_words:
            if len(word) <= 2:
                hints.append(word)  # Palabras muy cortas completas
            elif len(word) <= 4:
                hints.append(word[0] + "•" * (len(word) - 1))  # Primera letra
            else:
                hints.append(word[:2] + "•" * (len(word) - 2))  # Primeras dos letras
        return " ".join(hints)

    def on_word_placed(self, position: int, word_id: str, word: str):
        """Palabra colocada en posición"""
        self.update_progress()
        self.word_placed.emit(position, word_id, word)

        if self.is_complete():
            self.sentence_completed.emit()

    def on_word_removed(self, position: int):
        """Palabra removida de posición"""
        self.update_progress()

    def update_progress(self):
        """Actualizar progreso con mejor estilo"""
        placed = sum(1 for slot in self.slots if not slot.is_empty())
        total = len(self.slots)

        self.progress_label.setText(f"{placed} / {total} palabras")

        if placed == total:
            settings = Settings()
            self.progress_label.setStyleSheet(f"""
                QLabel {{
                    font-size: 14px;
                    font-weight: bold;
                    color: {settings.COLORS['green_success']};
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, 
                               stop: 0 {settings.COLORS['green_success']}20, 
                               stop: 1 {settings.COLORS['green_success']}10);
                    padding: 8px 12px;
                    border-radius: 10px;
                    border: 2px solid {settings.COLORS['green_success']}40;
                }}
            """)

    def is_complete(self) -> bool:
        """Verificar si está completa"""
        return all(not slot.is_empty() for slot in self.slots)

    def get_sentence(self) -> List[str]:
        """Obtener oración formada"""
        return [slot.get_word() for slot in self.slots]

    def is_correct(self) -> bool:
        """Verificar si es correcta"""
        return self.get_sentence() == self.correct_words

    def clear_all(self):
        """Limpiar todos los slots"""
        for slot in self.slots:
            slot.remove_word()
            dWidget(slot)

        layout.addLayout(slots_layout)

    def generate_hint(self) -> str:
        """Generar pista"""
        hints = []
        for word in self.correct_words:
            if len(word) <= 2:
                hints.append(word)
            elif len(word) <= 4:
                hints.append(word[0] + "_" * (len(word) - 1))
            else:
                hints.append(word[:2] + "_" * (len(word) - 2))
        return " ".join(hints)

    def on_word_placed(self, position: int, word_id: str, word: str):
        """Palabra colocada en posición"""
        self.update_progress()
        self.word_placed.emit(position, word_id, word)

        if self.is_complete():
            self.sentence_completed.emit()

    def on_word_removed(self, position: int):
        """Palabra removida de posición"""
        self.update_progress()
        # La señal específica se maneja en el widget principal

    def update_progress(self):
        """Actualizar progreso"""
        placed = sum(1 for slot in self.slots if not slot.is_empty())
        total = len(self.slots)

        self.progress_label.setText(f"{placed} / {total} palabras")

        if placed == total:
            settings = Settings()
            self.progress_label.setStyleSheet(f"""
                QLabel {{
                    font-size: 14px;
                    color: {settings.COLORS['green_success']};
                    background-color: {settings.COLORS['green_success']}15;
                    padding: 4px 8px;
                    border-radius: 6px;
                    font-weight: bold;
                }}
            """)

    def is_complete(self) -> bool:
        """Verificar si está completa"""
        return all(not slot.is_empty() for slot in self.slots)

    def get_sentence(self) -> List[str]:
        """Obtener oración formada"""
        return [slot.get_word() for slot in self.slots]

    def is_correct(self) -> bool:
        """Verificar si es correcta"""
        return self.get_sentence() == self.correct_words

    def clear_all(self):
        """Limpiar todos los slots"""
        for slot in self.slots:
            slot.remove_word()


class OrdenarFraseWidget(ExerciseWidget):
    """Widget para ejercicios de ordenar frases - NUEVO Y LIMPIO"""

    def __init__(self, exercise_data: Dict[str, Any], parent=None):
        super().__init__(exercise_data, parent)
        self.sentence_builders = []
        self.word_cards = []
        self.available_words = {}  # word_id -> WordCard
        print(f"🔤 OrdenarFraseWidget creado (nuevo)")

    def load_exercise_content(self):
        """Cargar contenido"""
        contenido = self.exercise_data.get('contenido', {})
        frases = contenido.get('frases', [])

        if not frases:
            self.load_demo_content()
            return

        # Limpiar layout
        self.clear_content_layout()

        # Instrucciones
        instruction_label = QLabel("🔤 Arrastra las palabras a sus posiciones correctas para formar las oraciones")
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

        # Crear constructores de oraciones
        self.sentence_builders = []
        for i, frase in enumerate(frases):
            builder = SentenceBuilder(i, frase)
            builder.word_placed.connect(self.on_word_placed)
            builder.sentence_completed.connect(self.check_overall_progress)
            self.sentence_builders.append(builder)
            self.content_layout.addWidget(builder)

        # Crear área de palabras
        words_area = self.create_words_area(frases)
        self.content_layout.addWidget(words_area)

        # Botón reset
        reset_btn = QPushButton("🔄 Reiniciar Todo")
        reset_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.settings.COLORS['orange_energetic']};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #e59400;
            }}
        """)
        reset_btn.clicked.connect(self.reset_all)
        self.content_layout.addWidget(reset_btn)

        # Espaciador
        self.content_layout.addStretch()

        # Iniciar
        QTimer.singleShot(100, self.start_exercise)

    def create_words_area(self, frases: List[str]) -> QFrame:
        """Crear área con palabras desordenadas - MEJORADA"""
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, 
                           stop: 0 #fff7ed, stop: 1 #fed7aa);
                border: 2px solid {self.settings.COLORS['orange_energetic']}60;
                border-radius: 16px;
                padding: 20px;
                margin: 20px 0;
            }}
        """)

        layout = QVBoxLayout(frame)
        layout.setSpacing(16)

        # Título más atractivo
        title_layout = QHBoxLayout()

        title = QLabel("📦 Banco de Palabras")
        title.setStyleSheet(f"""
            QLabel {{
                font-size: 22px;
                font-weight: bold;
                color: {self.settings.COLORS['orange_energetic']};
                margin-bottom: 5px;
            }}
        """)
        title_layout.addWidget(title)

        title_layout.addStretch()

        # Contador de palabras
        total_words = sum(len(frase.split()) for frase in frases)
        counter_label = QLabel(f"{total_words} palabras disponibles")
        counter_label.setStyleSheet(f"""
            QLabel {{
                font-size: 14px;
                color: {self.settings.COLORS['orange_energetic']};
                background-color: white;
                padding: 6px 12px;
                border-radius: 12px;
                border: 1px solid {self.settings.COLORS['orange_energetic']}40;
            }}
        """)
        title_layout.addWidget(counter_label)

        layout.addLayout(title_layout)

        # Instrucción
        instruction = QLabel("Arrastra las palabras desde aquí hacia las posiciones correctas en las oraciones")
        instruction.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #92400e;
                font-style: italic;
                margin-bottom: 10px;
                padding: 8px 12px;
                background-color: rgba(255, 255, 255, 0.7);
                border-radius: 8px;
            }
        """)
        layout.addWidget(instruction)

        # Recopilar todas las palabras
        all_words = []
        for i, frase in enumerate(frases):
            words = frase.split()
            for j, word in enumerate(words):
                word_id = f"{i}_{j}"
                all_words.append((word_id, word))

        # Desordenar
        random.shuffle(all_words)

        # Contenedor con scroll para muchas palabras
        from PyQt6.QtWidgets import QScrollArea
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setMaximumHeight(200)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background-color: #f3f4f6;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background-color: #d1d5db;
                border-radius: 4px;
                min-height: 20px;
            }
        """)

        # Widget contenedor para las palabras
        words_widget = QWidget()
        words_widget.setStyleSheet("background-color: transparent;")

        # Layout flex para las palabras
        words_layout = QVBoxLayout(words_widget)
        words_layout.setSpacing(12)
        words_layout.setContentsMargins(10, 10, 10, 10)

        # Crear filas de palabras
        current_row = QHBoxLayout()
        current_row.setSpacing(10)
        current_width = 0
        max_width_per_row = 800  # Ancho máximo por fila

        self.available_words = {}
        for word_id, word in all_words:
            card = WordCard(word, word_id)
            self.available_words[word_id] = card

            # Estimar ancho de la palabra
            estimated_width = max(80, len(word) * 12 + 40)

            # Si la fila actual está muy llena, crear nueva fila
            if current_width + estimated_width > max_width_per_row and current_row.count() > 0:
                current_row.addStretch()
                row_widget = QWidget()
                row_widget.setLayout(current_row)
                words_layout.addWidget(row_widget)

                # Crear nueva fila
                current_row = QHBoxLayout()
                current_row.setSpacing(10)
                current_width = 0

            current_row.addWidget(card)
            current_width += estimated_width

        # Añadir la última fila
        if current_row.count() > 0:
            current_row.addStretch()
            row_widget = QWidget()
            row_widget.setLayout(current_row)
            words_layout.addWidget(row_widget)

        # Espaciador final
        words_layout.addStretch()

        scroll_area.setWidget(words_widget)
        layout.addWidget(scroll_area)

        return frame

    def on_word_placed(self, position: int, word_id: str, word: str):
        """Palabra colocada"""
        # Marcar palabra como usada
        if word_id in self.available_words:
            self.available_words[word_id].hide()

        # Actualizar respuestas
        if 'placed_words' not in self.current_answers:
            self.current_answers['placed_words'] = {}
        self.current_answers['placed_words'][word_id] = word

        self.check_overall_progress()

    def check_overall_progress(self):
        """Verificar progreso general"""
        completed = sum(1 for builder in self.sentence_builders if builder.is_complete())
        total = len(self.sentence_builders)

        self.update_progress(completed, total)

    def reset_all(self):
        """Reiniciar todo con mejor UX"""
        reply = QMessageBox.question(
            self, "🔄 Reiniciar Ejercicio",
            "¿Estás seguro de que quieres reiniciar todas las oraciones?\n\nEsto devolverá todas las palabras al banco de palabras.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Limpiar constructores con animación visual
            for builder in self.sentence_builders:
                builder.clear_all()

            # Mostrar todas las palabras con estilo original
            for card in self.available_words.values():
                card.show()
                card.set_original_style()

            # Limpiar respuestas
            self.current_answers = {}

            # Actualizar progreso
            self.check_overall_progress()

            # Feedback visual
            self.progress_label.setText("Ejercicio reiniciado - Comienza de nuevo")

    def load_demo_content(self):
        """Cargar demo con oraciones más interesantes"""
        demo_content = {
            'frases': [
                'El gato negro duerme en la cama cómoda',
                'María estudia español con mucho entusiasmo',
                'Los niños juegan alegremente en el parque grande'
            ]
        }

        if 'contenido' not in self.exercise_data:
            self.exercise_data['contenido'] = {}
        self.exercise_data['contenido'].update(demo_content)

        self.exercise_data['respuestas_correctas'] = demo_content['frases']

        self.load_exercise_content()

    def clear_content_layout(self):
        """Limpiar layout"""
        while self.content_layout.count():
            child = self.content_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def validate_answers(self) -> Dict[str, Any]:
        """Validar respuestas con feedback detallado"""
        respuestas_correctas = self.exercise_data.get('respuestas_correctas', [])
        puntos_maximos = self.exercise_data.get('puntos_maximos', 50)

        # Verificar que todas estén completas
        all_complete = all(builder.is_complete() for builder in self.sentence_builders)

        if not all_complete:
            incomplete = sum(1 for builder in self.sentence_builders if not builder.is_complete())
            incomplete_sentences = []
            for i, builder in enumerate(self.sentence_builders):
                if not builder.is_complete():
                    missing = len(builder.correct_words) - sum(1 for slot in builder.slots if not slot.is_empty())
                    incomplete_sentences.append(f"Oración {i + 1} (faltan {missing} palabras)")

            return {
                'is_valid': False,
                'score': 0,
                'max_score': puntos_maximos,
                'precision': 0.0,
                'feedback': f"Completa las oraciones pendientes: {', '.join(incomplete_sentences)}",
                'details': {'incomplete_sentences': incomplete_sentences}
            }

        # Validar corrección
        score = 0
        correct_count = 0
        total_sentences = len(self.sentence_builders)
        details = {}

        for i, builder in enumerate(self.sentence_builders):
            formed_words = builder.get_sentence()
            formed_sentence = " ".join(formed_words)
            expected_sentence = respuestas_correctas[i] if i < len(respuestas_correctas) else ''
            is_correct = builder.is_correct()

            if is_correct:
                correct_count += 1
                points_per_sentence = puntos_maximos // total_sentences
                score += points_per_sentence

            details[f'sentence_{i + 1}'] = {
                'formed': formed_sentence,
                'expected': expected_sentence,
                'is_correct': is_correct,
                'formed_words': formed_words,
                'expected_words': expected_sentence.split()
            }

        precision = (correct_count / total_sentences * 100) if total_sentences > 0 else 0

        # Feedback detallado y motivacional
        if correct_count == total_sentences:
            if precision == 100:
                feedback = "🌟 ¡Perfecto! Todas las oraciones están correctamente ordenadas. ¡Excelente trabajo!"
            else:
                feedback = "⭐ ¡Muy bien! Todas las oraciones están completas y correctas."
        elif correct_count >= total_sentences * 0.8:
            feedback = f"👍 ¡Buen trabajo! {correct_count} de {total_sentences} oraciones correctas. Solo faltan algunos ajustes."
        elif correct_count >= total_sentences * 0.5:
            feedback = f"📚 Buen intento. {correct_count} de {total_sentences} oraciones correctas. Revisa el orden de las palabras."
        else:
            feedback = f"💪 Sigue practicando. {correct_count} de {total_sentences} oraciones correctas. ¡No te rindas!"

        # Añadir consejos específicos
        if correct_count < total_sentences:
            feedback += f" Consejo: Presta atención a las pistas y al orden lógico de las palabras."

        return {
            'is_valid': True,
            'score': score,
            'max_score': puntos_maximos,
            'precision': precision,
            'feedback': feedback,
            'details': {
                'total_sentences': total_sentences,
                'correct_sentences': correct_count,
                'sentences': details,
                'tips': "Recuerda: sujeto + verbo + complemento es el orden básico en español."
            }
        }


# =============================================================================
# TESTING
# =============================================================================
if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)

    exercise_data = {
        'id': 5,
        'tipo': 'Ordenar_Frase',
        'titulo': 'Ordena las Frases',
        'instrucciones': 'Arrastra las palabras para formar oraciones correctas',
        'contenido': {
            'frases': [
                'El gato duerme en la cama',
                'María estudia español todos los días'
            ]
        },
        'respuestas_correctas': [
            'El gato duerme en la cama',
            'María estudia español todos los días'
        ],
        'nivel_dificultad': 4,
        'puntos_maximos': 50,
        'tiempo_limite': 300
    }

    widget = OrdenarFraseWidget(exercise_data)
    widget.setMinimumSize(1000, 700)
    widget.show()


    def on_completed(result):
        print(f"✅ Ejercicio completado: {result}")


    def on_cancelled():
        print("❌ Ejercicio cancelado")
        app.quit()


    widget.exercise_completed.connect(on_completed)
    widget.exercise_cancelled.connect(on_cancelled)

    sys.exit(app.exec())
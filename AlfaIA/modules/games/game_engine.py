# =============================================================================
# AlfaIA/modules/games/game_engine.py - Motor de Juegos Educativos
# Motor completo y sin errores de sintaxis para juegos educativos
# =============================================================================

import random
import time
import logging
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import sys
from pathlib import Path
from datetime import datetime
import json

# Agregar el directorio raíz al path para imports
sys.path.append(str(Path(__file__).parent.parent.parent))

# Imports de módulos NLP para contenido inteligente
try:
    from modules.nlp.text_analyzer import TextAnalyzer
    from modules.nlp.difficulty_calculator import DifficultyCalculator, EducationLevel

    NLP_AVAILABLE = True
except ImportError:
    print("⚠️ Módulos NLP no disponibles para juegos")
    NLP_AVAILABLE = False


    class EducationLevel(Enum):
        PRIMARIA_INICIAL = "primaria_inicial"
        PRIMARIA_MEDIA = "primaria_media"
        SECUNDARIA = "secundaria"

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print("🔧 Inicializando motor de juegos educativos...")


# =============================================================================
# ENUMS Y DATACLASSES
# =============================================================================

class GameType(Enum):
    """Tipos de juegos educativos"""
    WORD_SEARCH = "word_search"
    WORD_SCRAMBLE = "word_scramble"
    CROSSWORD = "crossword"
    FILL_BLANKS = "fill_blanks"


class GameDifficulty(Enum):
    """Niveles de dificultad para juegos"""
    PRINCIPIANTE = "principiante"
    INTERMEDIO = "intermedio"
    AVANZADO = "avanzado"
    EXPERTO = "experto"


class GameStatus(Enum):
    """Estados del juego"""
    NOT_STARTED = "not_started"
    PLAYING = "playing"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class GameScore:
    """Puntuación del juego"""
    points: int = 0
    bonus_points: int = 0
    total_score: int = 0
    accuracy: float = 0.0
    time_bonus: int = 0

    def calculate_total(self):
        """Calcular puntuación total"""
        self.total_score = self.points + self.bonus_points + self.time_bonus


@dataclass
class GameSession:
    """Sesión de juego"""
    game_id: str
    game_type: str
    difficulty: str
    start_time: datetime
    end_time: Optional[datetime] = None
    status: GameStatus = GameStatus.NOT_STARTED
    score: GameScore = field(default_factory=GameScore)
    hints_used: int = 0
    mistakes_made: int = 0
    time_limit: Optional[int] = None


# =============================================================================
# CLASE BASE PARA JUEGOS
# =============================================================================

class BaseGame:
    """Clase base para todos los juegos educativos"""

    def __init__(self, game_type: str, difficulty: str):
        self.game_type = game_type
        self.difficulty = difficulty
        self.session = GameSession(
            game_id=f"{game_type}_{int(time.time())}",
            game_type=game_type,
            difficulty=difficulty,
            start_time=datetime.now()
        )
        self.game_data = {}
        self.is_initialized = False

    def initialize_game(self) -> bool:
        """Inicializar el juego"""
        try:
            self._setup_game_content()
            self.is_initialized = True
            self.session.status = GameStatus.NOT_STARTED
            return True
        except Exception as e:
            logger.error(f"Error inicializando juego: {e}")
            return False

    def start_game(self) -> bool:
        """Iniciar el juego"""
        if not self.is_initialized:
            if not self.initialize_game():
                return False

        self.session.status = GameStatus.PLAYING
        self.session.start_time = datetime.now()
        return True

    def _setup_game_content(self):
        """Configurar contenido del juego - implementar en subclases"""
        pass

    def get_game_state(self) -> Dict[str, Any]:
        """Obtener estado actual del juego"""
        return {
            'game_id': self.session.game_id,
            'game_type': self.session.game_type,
            'difficulty': self.session.difficulty,
            'status': self.session.status.value,
            'score': self.session.score.total_score,
            'hints_used': self.session.hints_used,
            'game_data': self.game_data
        }

    def use_hint(self) -> Tuple[bool, str]:
        """Usar una pista"""
        max_hints = self._get_max_hints()
        if self.session.hints_used >= max_hints:
            return False, "No hay más pistas disponibles"

        hint = self._generate_hint()
        self.session.hints_used += 1
        return True, hint

    def _get_max_hints(self) -> int:
        """Obtener número máximo de pistas"""
        return 3

    def _generate_hint(self) -> str:
        """Generar pista - implementar en subclases"""
        return "Pista genérica disponible"

    def make_move(self, action: str, data: Any) -> Tuple[bool, str, int]:
        """Hacer un movimiento en el juego - implementar en subclases"""
        return False, "Movimiento no implementado", 0


# =============================================================================
# JUEGO: SOPA DE LETRAS
# =============================================================================

class WordSearchGame(BaseGame):
    """Juego de sopa de letras"""

    def __init__(self, difficulty: str):
        super().__init__("word_search", difficulty)
        self.grid_size = self._get_grid_size()
        self.words_to_find = []
        self.found_words = []
        self.grid = []

    def _get_grid_size(self) -> int:
        """Obtener tamaño de cuadrícula según dificultad"""
        sizes = {
            "principiante": 10,
            "intermedio": 12,
            "avanzado": 15,
            "experto": 18
        }
        return sizes.get(self.difficulty, 10)

    def _setup_game_content(self):
        """Configurar contenido de sopa de letras"""
        # Obtener palabras según dificultad
        self.words_to_find = self._get_words_for_difficulty()

        # Crear cuadrícula vacía
        self.grid = [['' for _ in range(self.grid_size)] for _ in range(self.grid_size)]

        # Colocar palabras en la cuadrícula
        self._place_words_in_grid()

        # Llenar espacios vacíos con letras aleatorias
        self._fill_empty_spaces()

        # Guardar datos del juego
        self.game_data = {
            'grid': self.grid,
            'grid_size': self.grid_size,
            'words_to_find': self.words_to_find,
            'found_words': self.found_words,
            'word_positions': getattr(self, 'word_positions', {})
        }

    def _get_words_for_difficulty(self) -> List[str]:
        """Obtener palabras según nivel de dificultad"""
        word_sets = {
            "principiante": [
                "CASA", "PERRO", "GATO", "SOL", "LUNA", "AGUA", "FUEGO", "AMOR", "PAZ", "VIDA"
            ],
            "intermedio": [
                "ESCUELA", "FAMILIA", "TRABAJO", "AMISTAD", "FELICIDAD", "CONOCIMIENTO",
                "RESPETO", "LIBERTAD", "JUSTICIA", "VERDAD"
            ],
            "avanzado": [
                "RESPONSABILIDAD", "CREATIVIDAD", "PERSEVERANCIA", "SOLIDARIDAD",
                "COMPRENSION", "TOLERANCIA", "DEMOCRACIA", "DIVERSIDAD", "INNOVACION", "EXCELENCIA"
            ],
            "experto": [
                "INTERDISCIPLINARIO", "MULTICULTURALISMO", "SUSTENTABILIDAD", "GLOBALIZACION",
                "COMPETITIVIDAD", "TRANSFORMACION", "PARADIGMA", "EPISTEMOLOGIA", "FENOMENOLOGIA", "HERMENEUTICA"
            ]
        }

        words = word_sets.get(self.difficulty, word_sets["principiante"])
        # Seleccionar un subconjunto de palabras
        num_words = min(8, len(words))
        return random.sample(words, num_words)

    def _place_words_in_grid(self):
        """Colocar palabras en la cuadrícula"""
        self.word_positions = {}
        directions = [
            (0, 1),  # Horizontal derecha
            (1, 0),  # Vertical abajo
            (1, 1),  # Diagonal abajo-derecha
            (0, -1),  # Horizontal izquierda
            (-1, 0),  # Vertical arriba
            (-1, -1),  # Diagonal arriba-izquierda
            (1, -1),  # Diagonal abajo-izquierda
            (-1, 1)  # Diagonal arriba-derecha
        ]

        for word in self.words_to_find:
            placed = False
            attempts = 0
            max_attempts = 100

            while not placed and attempts < max_attempts:
                attempts += 1

                # Elegir dirección aleatoria
                direction = random.choice(directions)
                dx, dy = direction

                # Calcular posición inicial válida
                if dx == 0:
                    start_row = random.randint(0, self.grid_size - 1)
                elif dx > 0:
                    start_row = random.randint(0, self.grid_size - len(word))
                else:
                    start_row = random.randint(len(word) - 1, self.grid_size - 1)

                if dy == 0:
                    start_col = random.randint(0, self.grid_size - 1)
                elif dy > 0:
                    start_col = random.randint(0, self.grid_size - len(word))
                else:
                    start_col = random.randint(len(word) - 1, self.grid_size - 1)

                # Verificar si la palabra cabe
                if self._can_place_word(word, start_row, start_col, dx, dy):
                    self._place_word(word, start_row, start_col, dx, dy)
                    placed = True

    def _can_place_word(self, word: str, start_row: int, start_col: int, dx: int, dy: int) -> bool:
        """Verificar si una palabra se puede colocar en la posición dada"""
        for i, letter in enumerate(word):
            row = start_row + i * dx
            col = start_col + i * dy

            # Verificar límites
            if row < 0 or row >= self.grid_size or col < 0 or col >= self.grid_size:
                return False

            # Verificar si la celda está vacía o tiene la misma letra
            if self.grid[row][col] != '' and self.grid[row][col] != letter:
                return False

        return True

    def _place_word(self, word: str, start_row: int, start_col: int, dx: int, dy: int):
        """Colocar una palabra en la cuadrícula"""
        positions = []
        for i, letter in enumerate(word):
            row = start_row + i * dx
            col = start_col + i * dy
            self.grid[row][col] = letter
            positions.append((row, col))

        self.word_positions[word] = {
            'positions': positions,
            'start': (start_row, start_col),
            'end': (start_row + (len(word) - 1) * dx, start_col + (len(word) - 1) * dy),
            'direction': (dx, dy)
        }

    def _fill_empty_spaces(self):
        """Llenar espacios vacíos con letras aleatorias"""
        letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                if self.grid[row][col] == '':
                    self.grid[row][col] = random.choice(letters)

    def make_move(self, action: str, data: Any) -> Tuple[bool, str, int]:
        """Hacer un movimiento en sopa de letras"""
        if action == "select_word":
            return self._check_word_selection(data)
        return False, "Acción no válida", 0

    def _check_word_selection(self, selection_data: Dict) -> Tuple[bool, str, int]:
        """Verificar selección de palabra"""
        start_pos = selection_data.get('start', (0, 0))
        end_pos = selection_data.get('end', (0, 0))

        # Obtener palabra seleccionada
        selected_word = self._get_word_from_selection(start_pos, end_pos)

        if selected_word in self.words_to_find and selected_word not in self.found_words:
            self.found_words.append(selected_word)
            points = len(selected_word) * 10
            self.session.score.points += points

            message = f"¡Excelente! Encontraste '{selected_word}'"

            # Verificar si el juego está completo
            if len(self.found_words) == len(self.words_to_find):
                self.session.status = GameStatus.COMPLETED
                self.session.end_time = datetime.now()
                message += " ¡Juego completado!"

            return True, message, points
        else:
            self.session.mistakes_made += 1
            return False, "Palabra no encontrada o ya descubierta", 0

    def _get_word_from_selection(self, start_pos: Tuple[int, int], end_pos: Tuple[int, int]) -> str:
        """Obtener palabra de la selección"""
        row1, col1 = start_pos
        row2, col2 = end_pos

        # Calcular dirección
        if row1 == row2:  # Horizontal
            if col1 <= col2:
                return ''.join(self.grid[row1][col1:col2 + 1])
            else:
                return ''.join(self.grid[row1][col2:col1 + 1][::-1])
        elif col1 == col2:  # Vertical
            if row1 <= row2:
                return ''.join(self.grid[row][col1] for row in range(row1, row2 + 1))
            else:
                return ''.join(self.grid[row][col1] for row in range(row2, row1 + 1))[::-1]
        else:  # Diagonal
            # Implementación simplificada para diagonal
            return ""

    def _generate_hint(self) -> str:
        """Generar pista para sopa de letras"""
        if not self.found_words:
            return "Busca palabras en horizontal, vertical y diagonal"

        remaining_words = [w for w in self.words_to_find if w not in self.found_words]
        if remaining_words:
            hint_word = random.choice(remaining_words)
            return f"Busca una palabra que empiece con '{hint_word[0]}' y tenga {len(hint_word)} letras"

        return "¡Ya encontraste todas las palabras!"


# =============================================================================
# JUEGO: PALABRAS DESORDENADAS
# =============================================================================

class WordScrambleGame(BaseGame):
    """Juego de palabras desordenadas"""

    def __init__(self, difficulty: str):
        super().__init__("word_scramble", difficulty)
        self.scrambled_words = []
        self.original_words = []
        self.solved_words = []

    def _setup_game_content(self):
        """Configurar contenido de palabras desordenadas"""
        # Obtener palabras según dificultad
        self.original_words = self._get_words_for_difficulty()

        # Crear palabras desordenadas
        self.scrambled_words = []
        for word in self.original_words:
            scrambled = self._scramble_word(word)
            self.scrambled_words.append({
                'scrambled': scrambled,
                'original': word,
                'hint': self._get_word_hint(word),
                'solved': False
            })

        # Guardar datos del juego
        self.game_data = {
            'words': [w['scrambled'] for w in self.scrambled_words],
            'original_words': self.original_words,
            'scrambled_words': self.scrambled_words,
            'solved_count': 0,
            'total_words': len(self.original_words)
        }

    def _get_words_for_difficulty(self) -> List[str]:
        """Obtener palabras según nivel de dificultad"""
        word_sets = {
            "principiante": [
                "MESA", "SILLA", "LIBRO", "LAPIZ", "PAPEL", "AGUA", "CASA", "PUERTA"
            ],
            "intermedio": [
                "COMPUTADORA", "TELEFONO", "VENTANA", "COCINA", "JARDIN", "HOSPITAL", "ESCUELA", "BIBLIOTECA"
            ],
            "avanzado": [
                "REFRIGERADOR", "TELEVISION", "UNIVERSIDAD", "LABORATORIO", "SUPERMERCADO",
                "RESTAURANTE", "ARQUITECTURA", "INGENIERIA"
            ],
            "experto": [
                "RESPONSABILIDAD", "INVESTIGACION", "TRANSFORMACION", "COMUNICACION",
                "ADMINISTRACION", "COORDINACION", "ESPECIALIZACION", "CARACTERIZACION"
            ]
        }

        words = word_sets.get(self.difficulty, word_sets["principiante"])
        num_words = min(6, len(words))
        return random.sample(words, num_words)

    def _scramble_word(self, word: str) -> str:
        """Desordenar una palabra"""
        letters = list(word)
        scrambled = letters.copy()

        # Asegurar que la palabra esté realmente desordenada
        attempts = 0
        while ''.join(scrambled) == word and attempts < 10:
            random.shuffle(scrambled)
            attempts += 1

        return ''.join(scrambled)

    def _get_word_hint(self, word: str) -> str:
        """Obtener pista para una palabra"""
        hints = {
            # Principiante
            "MESA": "Mueble donde comes o estudias",
            "SILLA": "Te sientas en ella",
            "LIBRO": "Lo lees para aprender",
            "LAPIZ": "Escribes con él",
            "PAPEL": "Escribes sobre él",
            "AGUA": "Líquido esencial para la vida",
            "CASA": "Lugar donde vives",
            "PUERTA": "La abres para entrar",

            # Intermedio
            "COMPUTADORA": "Dispositivo electrónico para trabajar",
            "TELEFONO": "Dispositivo para comunicarte",
            "VENTANA": "Te permite ver hacia afuera",
            "COCINA": "Lugar donde preparas comida",
            "JARDIN": "Espacio con plantas y flores",
            "HOSPITAL": "Lugar donde curan enfermos",
            "ESCUELA": "Lugar donde estudian los niños",
            "BIBLIOTECA": "Lugar lleno de libros",

            # Avanzado
            "REFRIGERADOR": "Electrodoméstico que enfría alimentos",
            "TELEVISION": "Dispositivo para ver programas",
            "UNIVERSIDAD": "Institución de educación superior",
            "LABORATORIO": "Lugar donde se hacen experimentos",
            "SUPERMERCADO": "Tienda grande donde compras comida",
            "RESTAURANTE": "Lugar donde sirven comida preparada",
            "ARQUITECTURA": "Arte de diseñar edificios",
            "INGENIERIA": "Aplicación de ciencias para resolver problemas"
        }

        return hints.get(word, f"Palabra de {len(word)} letras")

    def make_move(self, action: str, data: Any) -> Tuple[bool, str, int]:
        """Hacer un movimiento en palabras desordenadas"""
        if action == "submit_word":
            return self._check_word_answer(data)
        return False, "Acción no válida", 0

    def _check_word_answer(self, answer_data: Dict) -> Tuple[bool, str, int]:
        """Verificar respuesta de palabra"""
        word_index = answer_data.get('word_index', 0)
        user_answer = answer_data.get('answer', '').upper().strip()

        if word_index >= len(self.scrambled_words):
            return False, "Índice de palabra inválido", 0

        word_data = self.scrambled_words[word_index]
        correct_word = word_data['original']

        if user_answer == correct_word and not word_data['solved']:
            word_data['solved'] = True
            self.solved_words.append(correct_word)

            points = len(correct_word) * 15
            self.session.score.points += points

            message = f"¡Correcto! '{correct_word}' es la respuesta"

            # Verificar si el juego está completo
            if len(self.solved_words) == len(self.original_words):
                self.session.status = GameStatus.COMPLETED
                self.session.end_time = datetime.now()
                message += " ¡Todas las palabras resueltas!"

            return True, message, points
        else:
            self.session.mistakes_made += 1
            if word_data['solved']:
                return False, "Esta palabra ya fue resuelta", 0
            else:
                return False, f"Incorrecto. Intenta de nuevo", 0

    def _generate_hint(self) -> str:
        """Generar pista para palabras desordenadas"""
        unsolved_words = [w for w in self.scrambled_words if not w['solved']]
        if unsolved_words:
            hint_word = random.choice(unsolved_words)
            return f"Pista: {hint_word['hint']}"
        return "¡Ya resolviste todas las palabras!"


# =============================================================================
# JUEGO: COMPLETAR FRASES
# =============================================================================

class FillBlanksGame(BaseGame):
    """Juego de completar frases"""

    def __init__(self, difficulty: str):
        super().__init__("fill_blanks", difficulty)
        self.sentences = []
        self.completed_sentences = []

    def _setup_game_content(self):
        """Configurar contenido de completar frases"""
        self.sentences = self._get_sentences_for_difficulty()

        # Guardar datos del juego
        self.game_data = {
            'sentences': self.sentences,
            'completed_count': 0,
            'total_sentences': len(self.sentences)
        }

    def _get_sentences_for_difficulty(self) -> List[Dict]:
        """Obtener frases según nivel de dificultad"""
        sentence_sets = {
            "principiante": [
                {
                    'text': 'El ___ brilla en el cielo.',
                    'options': ['sol', 'luna', 'agua', 'árbol'],
                    'correct': 'sol'
                },
                {
                    'text': 'Mi ___ es muy bonita.',
                    'options': ['casa', 'mesa', 'silla', 'libro'],
                    'correct': 'casa'
                },
                {
                    'text': 'El ___ ladra fuerte.',
                    'options': ['perro', 'gato', 'pájaro', 'pez'],
                    'correct': 'perro'
                }
            ],
            "intermedio": [
                {
                    'text': 'La ___ es muy importante para la salud.',
                    'options': ['educación', 'medicina', 'tecnología', 'música'],
                    'correct': 'educación'
                },
                {
                    'text': 'El ___ ayuda a las personas enfermas.',
                    'options': ['doctor', 'profesor', 'ingeniero', 'artista'],
                    'correct': 'doctor'
                }
            ],
            "avanzado": [
                {
                    'text': 'La ___ es fundamental para el desarrollo sostenible.',
                    'options': ['innovación', 'tradición', 'competencia', 'diversión'],
                    'correct': 'innovación'
                }
            ]
        }

        return sentence_sets.get(self.difficulty, sentence_sets["principiante"])

    def make_move(self, action: str, data: Any) -> Tuple[bool, str, int]:
        """Hacer un movimiento en completar frases"""
        if action == "submit_answer":
            return self._check_sentence_answer(data)
        return False, "Acción no válida", 0

    def _check_sentence_answer(self, answer_data: Dict) -> Tuple[bool, str, int]:
        """Verificar respuesta de frase"""
        sentence_index = answer_data.get('sentence_index', 0)
        user_answer = answer_data.get('answer', '').lower().strip()

        if sentence_index >= len(self.sentences):
            return False, "Índice de frase inválido", 0

        sentence = self.sentences[sentence_index]
        correct_answer = sentence['correct'].lower()

        if user_answer == correct_answer:
            if sentence_index not in self.completed_sentences:
                self.completed_sentences.append(sentence_index)
                points = 20
                self.session.score.points += points

                message = f"¡Correcto! '{sentence['correct']}' es la respuesta"

                # Verificar si el juego está completo
                if len(self.completed_sentences) == len(self.sentences):
                    self.session.status = GameStatus.COMPLETED
                    self.session.end_time = datetime.now()
                    message += " ¡Todas las frases completadas!"

                return True, message, points
            else:
                return False, "Esta frase ya fue completada", 0
        else:
            self.session.mistakes_made += 1
            return False, "Respuesta incorrecta. Intenta de nuevo", 0

    def _generate_hint(self) -> str:
        """Generar pista para completar frases"""
        return "Lee la frase completa para entender el contexto"


# =============================================================================
# MOTOR PRINCIPAL DE JUEGOS
# =============================================================================

class GameEngine:
    """Motor principal que gestiona todos los juegos"""

    def __init__(self):
        self.active_games: Dict[str, BaseGame] = {}
        self.game_classes = {
            "word_search": WordSearchGame,
            "word_scramble": WordScrambleGame,
            "fill_blanks": FillBlanksGame,
        }

        if NLP_AVAILABLE:
            self.text_analyzer = TextAnalyzer()
            self.difficulty_calculator = DifficultyCalculator()

        print("✅ GameEngine inicializado")

    def create_game(self, game_type: str, difficulty: str = "principiante") -> Optional[Dict[str, Any]]:
        """
        Crear nuevo juego y retornar los datos del juego

        Args:
            game_type (str): Tipo de juego ('word_search', 'word_scramble', 'fill_blanks')
            difficulty (str): Nivel de dificultad

        Returns:
            Dict con los datos del juego creado o None si hay error
        """
        try:
            game_class = self.game_classes.get(game_type)
            if not game_class:
                logger.error(f"Tipo de juego no soportado: {game_type}")
                return None

            game = game_class(difficulty)
            if game.initialize_game():
                game_id = game.session.game_id
                self.active_games[game_id] = game

                print(f"🎮 Juego creado: {game_id}")

                # Retornar datos del juego para uso en UI
                return {
                    'game_id': game_id,
                    'type': game_type,
                    'difficulty': difficulty,
                    'status': game.session.status.value,
                    'game_data': game.game_data
                }
            else:
                logger.error("Error inicializando juego")
                return None

        except Exception as e:
            logger.error(f"Error creando juego: {e}")
            return None

    def start_game(self, game_id: str) -> bool:
        """Iniciar juego"""
        game = self.active_games.get(game_id)
        if game:
            return game.start_game()
        return False

    def make_move(self, game_id: str, action: str, data: Any) -> Dict[str, Any]:
        """Hacer movimiento en juego"""
        game = self.active_games.get(game_id)
        if not game:
            return {'success': False, 'message': 'Juego no encontrado'}

        is_correct, message, points = game.make_move(action, data)

        return {
            'success': True,
            'correct': is_correct,
            'message': message,
            'points': points,
            'game_state': game.get_game_state()
        }

    def get_game_state(self, game_id: str) -> Optional[Dict[str, Any]]:
        """Obtener estado del juego"""
        game = self.active_games.get(game_id)
        if game:
            return game.get_game_state()
        return None

    def use_hint(self, game_id: str) -> Dict[str, Any]:
        """Usar pista en juego"""
        game = self.active_games.get(game_id)
        if not game:
            return {'success': False, 'message': 'Juego no encontrado'}

        success, hint = game.use_hint()
        return {
            'success': success,
            'hint': hint,
            'hints_remaining': game._get_max_hints() - game.session.hints_used
        }

    def pause_game(self, game_id: str) -> bool:
        """Pausar juego"""
        game = self.active_games.get(game_id)
        if game and game.session.status == GameStatus.PLAYING:
            game.session.status = GameStatus.PAUSED
            return True
        return False

    def resume_game(self, game_id: str) -> bool:
        """Reanudar juego"""
        game = self.active_games.get(game_id)
        if game and game.session.status == GameStatus.PAUSED:
            game.session.status = GameStatus.PLAYING
            return True
        return False

    def end_game(self, game_id: str) -> Dict[str, Any]:
        """Terminar juego y obtener resultados finales"""
        game = self.active_games.get(game_id)
        if not game:
            return {'success': False, 'message': 'Juego no encontrado'}

        game.session.status = GameStatus.COMPLETED
        game.session.end_time = datetime.now()

        # Calcular puntuación final
        game.session.score.calculate_total()

        # Calcular tiempo total
        if game.session.start_time and game.session.end_time:
            total_time = (game.session.end_time - game.session.start_time).total_seconds()
        else:
            total_time = 0

        # Calcular accuracy
        if hasattr(game, 'session') and hasattr(game.session, 'moves'):
            correct_moves = sum(1 for move in game.session.moves if move.is_correct)
            total_moves = len(game.session.moves)
            accuracy = (correct_moves / total_moves * 100) if total_moves > 0 else 0
        else:
            # Método alternativo para calcular accuracy
            if game.game_type == "word_search":
                accuracy = (len(game.found_words) / len(game.words_to_find) * 100) if game.words_to_find else 0
            elif game.game_type == "word_scramble":
                accuracy = (len(game.solved_words) / len(game.original_words) * 100) if game.original_words else 0
            elif game.game_type == "fill_blanks":
                accuracy = (len(game.completed_sentences) / len(game.sentences) * 100) if game.sentences else 0
            else:
                accuracy = 0

        game.session.score.accuracy = accuracy

        final_results = {
            'success': True,
            'game_id': game_id,
            'game_type': game.game_type,
            'difficulty': game.difficulty,
            'final_score': game.session.score.total_score,
            'accuracy': accuracy,
            'total_time': total_time,
            'hints_used': game.session.hints_used,
            'mistakes_made': game.session.mistakes_made,
            'status': game.session.status.value,
            'completion_date': game.session.end_time
        }

        # Remover juego de activos
        del self.active_games[game_id]

        return final_results

    def get_available_games(self) -> List[Dict[str, str]]:
        """Obtener lista de juegos disponibles"""
        return [
            {
                'type': 'word_search',
                'name': 'Sopa de Letras',
                'description': 'Encuentra palabras ocultas en una cuadrícula de letras'
            },
            {
                'type': 'word_scramble',
                'name': 'Palabras Desordenadas',
                'description': 'Ordena las letras para formar palabras correctas'
            },
            {
                'type': 'fill_blanks',
                'name': 'Completar Frases',
                'description': 'Completa las frases con las palabras correctas'
            }
        ]

    def get_game_statistics(self, game_id: str) -> Dict[str, Any]:
        """Obtener estadísticas del juego"""
        game = self.active_games.get(game_id)
        if not game:
            return {'success': False, 'message': 'Juego no encontrado'}

        stats = {
            'success': True,
            'game_type': game.game_type,
            'difficulty': game.difficulty,
            'current_score': game.session.score.total_score,
            'hints_used': game.session.hints_used,
            'mistakes_made': game.session.mistakes_made,
            'status': game.session.status.value
        }

        # Estadísticas específicas por tipo de juego
        if game.game_type == "word_search":
            stats.update({
                'words_found': len(game.found_words),
                'total_words': len(game.words_to_find),
                'progress': len(game.found_words) / len(game.words_to_find) * 100 if game.words_to_find else 0
            })
        elif game.game_type == "word_scramble":
            stats.update({
                'words_solved': len(game.solved_words),
                'total_words': len(game.original_words),
                'progress': len(game.solved_words) / len(game.original_words) * 100 if game.original_words else 0
            })
        elif game.game_type == "fill_blanks":
            stats.update({
                'sentences_completed': len(game.completed_sentences),
                'total_sentences': len(game.sentences),
                'progress': len(game.completed_sentences) / len(game.sentences) * 100 if game.sentences else 0
            })

        return stats

    def cleanup_inactive_games(self, max_inactive_time: int = 3600):
        """Limpiar juegos inactivos (más de 1 hora por defecto)"""
        current_time = datetime.now()
        inactive_games = []

        for game_id, game in self.active_games.items():
            if game.session.start_time:
                time_diff = (current_time - game.session.start_time).total_seconds()
                if time_diff > max_inactive_time:
                    inactive_games.append(game_id)

        for game_id in inactive_games:
            del self.active_games[game_id]
            logger.info(f"Juego inactivo removido: {game_id}")

        return len(inactive_games)


# =============================================================================
# FUNCIONES AUXILIARES
# =============================================================================

def create_game_engine() -> GameEngine:
    """
    Función factory para crear una instancia del motor de juegos
    """
    return GameEngine()


def validate_game_data(game_data: Dict[str, Any]) -> bool:
    """
    Validar que los datos del juego estén completos
    """
    required_fields = ['game_id', 'type', 'difficulty', 'status']
    return all(field in game_data for field in required_fields)


def get_difficulty_settings(difficulty: str) -> Dict[str, Any]:
    """
    Obtener configuraciones según el nivel de dificultad
    """
    settings = {
        "principiante": {
            "max_hints": 5,
            "time_bonus_multiplier": 1.0,
            "point_multiplier": 1.0,
            "grid_size": 10,
            "word_count": 6
        },
        "intermedio": {
            "max_hints": 3,
            "time_bonus_multiplier": 1.2,
            "point_multiplier": 1.2,
            "grid_size": 12,
            "word_count": 8
        },
        "avanzado": {
            "max_hints": 2,
            "time_bonus_multiplier": 1.5,
            "point_multiplier": 1.5,
            "grid_size": 15,
            "word_count": 10
        },
        "experto": {
            "max_hints": 1,
            "time_bonus_multiplier": 2.0,
            "point_multiplier": 2.0,
            "grid_size": 18,
            "word_count": 12
        }
    }

    return settings.get(difficulty, settings["principiante"])


# =============================================================================
# CÓDIGO DE PRUEBA
# =============================================================================

def test_game_engine():
    """Función de prueba para el motor de juegos"""
    print("🧪 Probando motor de juegos educativos...")

    engine = GameEngine()

    print("\n🎮 JUEGOS DISPONIBLES:")
    print("=" * 50)
    available_games = engine.get_available_games()
    for game in available_games:
        print(f"• {game['name']}: {game['description']}")

    print("\n🎯 PRUEBA DE SOPA DE LETRAS:")
    print("=" * 50)

    # Crear juego de sopa de letras
    game_data = engine.create_game("word_search", "principiante")

    if game_data:
        game_id = game_data['game_id']
        print(f"✅ Juego creado: {game_id}")

        if engine.start_game(game_id):
            print("🚀 Juego iniciado")

            state = engine.get_game_state(game_id)
            if state:
                print(f"📊 Estado inicial:")
                print(f"  • Tamaño de cuadrícula: {state['game_data']['grid_size']}x{state['game_data']['grid_size']}")
                print(f"  • Palabras a encontrar: {len(state['game_data']['words_to_find'])}")
                print(f"  • Palabras: {', '.join(state['game_data']['words_to_find'])}")

                # Mostrar primeras filas de la cuadrícula
                grid = state['game_data']['grid']
                print(f"\n🔍 Cuadrícula (primeras 5 filas):")
                for i, row in enumerate(grid[:5]):
                    print(f"  {' '.join(row[:10])}")

                # Usar pista
                hint_result = engine.use_hint(game_id)
                if hint_result['success']:
                    print(f"\n💡 Pista: {hint_result['hint']}")
                    print(f"🎯 Pistas restantes: {hint_result['hints_remaining']}")

                # Simular movimiento
                words_to_find = state['game_data']['words_to_find']
                if words_to_find:
                    move_result = engine.make_move(game_id, "select_word", {
                        'start': (0, 0),
                        'end': (0, len(words_to_find[0]) - 1)
                    })

                    print(f"\n🎯 Resultado del movimiento:")
                    print(f"  • Correcto: {move_result['correct']}")
                    print(f"  • Mensaje: {move_result['message']}")
                    print(f"  • Puntos ganados: {move_result['points']}")

        # Terminar juego
        final_results = engine.end_game(game_id)
        print(f"\n🏁 Juego terminado:")
        print(f"  • Puntuación final: {final_results['final_score']}")
        print(f"  • Precisión: {final_results['accuracy']:.1f}%")

    print("\n🔤 PRUEBA DE PALABRAS DESORDENADAS:")
    print("=" * 50)

    # Crear juego de palabras desordenadas
    scramble_data = engine.create_game("word_scramble", "principiante")

    if scramble_data:
        game_id = scramble_data['game_id']
        print(f"✅ Juego creado: {game_id}")

        if engine.start_game(game_id):
            print("🚀 Juego iniciado")

            state = engine.get_game_state(game_id)
            if state:
                scrambled_words = state['game_data']['scrambled_words']

                print(f"📝 Palabras desordenadas:")
                for i, word_data in enumerate(scrambled_words[:3]):
                    print(f"  {i + 1}. {word_data['scrambled']} (Pista: {word_data['hint']})")

                # Simular respuesta correcta
                if scrambled_words:
                    correct_answer = scrambled_words[0]['original']
                    move_result = engine.make_move(game_id, "submit_word", {
                        'word_index': 0,
                        'answer': correct_answer
                    })
                    print(f"\n🎯 Respuesta: {correct_answer}")
                    print(f"  • Correcto: {move_result['correct']}")
                    print(f"  • Mensaje: {move_result['message']}")
                    print(f"  • Puntos: {move_result['points']}")

        # Obtener estadísticas
        stats = engine.get_game_statistics(game_id)
        if stats['success']:
            print(f"\n📊 Estadísticas:")
            print(f"  • Progreso: {stats['progress']:.1f}%")
            print(f"  • Palabras resueltas: {stats['words_solved']}/{stats['total_words']}")

        # Terminar juego
        final_results = engine.end_game(game_id)
        print(f"\n🏁 Juego terminado:")
        print(f"  • Puntuación final: {final_results['final_score']}")

    print(f"\n✅ Pruebas del motor de juegos completadas!")


if __name__ == "__main__":
    test_game_engine()
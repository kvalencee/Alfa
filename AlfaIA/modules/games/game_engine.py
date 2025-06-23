# =============================================================================
# AlfaIA/modules/games/game_engine.py - Motor de Juegos Educativos
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
    CROSSWORD = "crossword"
    WORD_SCRAMBLE = "word_scramble"
    MEMORY_CARDS = "memory_cards"
    TYPING_RACE = "typing_race"
    GRAMMAR_DUEL = "grammar_duel"
    VOCABULARY_BUILDER = "vocabulary_builder"
    STORY_BUILDER = "story_builder"


class GameDifficulty(Enum):
    """Niveles de dificultad para juegos"""
    VERY_EASY = "very_easy"
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EXPERT = "expert"


class GameStatus(Enum):
    """Estados del juego"""
    NOT_STARTED = "not_started"
    PLAYING = "playing"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"


class PlayerAction(Enum):
    """Acciones del jugador"""
    SELECT_WORD = "select_word"
    ENTER_TEXT = "enter_text"
    DRAG_DROP = "drag_drop"
    CLICK_TILE = "click_tile"
    SUBMIT_ANSWER = "submit_answer"


@dataclass
class GameScore:
    """Puntuación del juego"""
    points: int = 0
    bonus_points: int = 0
    time_bonus: int = 0
    accuracy_bonus: int = 0
    total_score: int = 0
    stars: int = 0

    def calculate_total(self):
        """Calcular puntuación total"""
        self.total_score = self.points + self.bonus_points + self.time_bonus + self.accuracy_bonus

        if self.total_score >= 90:
            self.stars = 3
        elif self.total_score >= 70:
            self.stars = 2
        elif self.total_score >= 50:
            self.stars = 1
        else:
            self.stars = 0


@dataclass
class GameMove:
    """Movimiento del jugador"""
    action: PlayerAction
    data: Any
    timestamp: float
    is_correct: bool = False
    points_earned: int = 0


@dataclass
class GameSession:
    """Sesión de juego"""
    game_id: str
    game_type: GameType
    difficulty: GameDifficulty
    player_level: EducationLevel
    start_time: datetime
    end_time: Optional[datetime] = None
    status: GameStatus = GameStatus.NOT_STARTED
    score: GameScore = field(default_factory=GameScore)
    moves: List[GameMove] = field(default_factory=list)
    time_limit: Optional[int] = None
    hints_used: int = 0
    mistakes_made: int = 0


# =============================================================================
# CLASE BASE PARA JUEGOS
# =============================================================================

class BaseGame:
    """Clase base para todos los juegos educativos"""

    def __init__(self, game_type: GameType, difficulty: GameDifficulty, player_level: EducationLevel):
        self.game_type = game_type
        self.difficulty = difficulty
        self.player_level = player_level
        self.session = GameSession(
            game_id=f"{game_type.value}_{int(time.time())}",
            game_type=game_type,
            difficulty=difficulty,
            player_level=player_level,
            start_time=datetime.now()
        )
        self.game_data = {}
        self.is_initialized = False

    def initialize_game(self) -> bool:
        """Inicializar el juego"""
        try:
            self._setup_game_content()
            self._setup_scoring_system()
            self._setup_time_limits()
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

    def make_move(self, action: PlayerAction, data: Any) -> Tuple[bool, str, int]:
        """Hacer un movimiento en el juego"""
        if self.session.status != GameStatus.PLAYING:
            return False, "El juego no está activo", 0

        if self._check_timeout():
            self.session.status = GameStatus.TIMEOUT
            return False, "Tiempo agotado", 0

        is_correct, message, points = self._process_move(action, data)

        move = GameMove(
            action=action,
            data=data,
            timestamp=time.time(),
            is_correct=is_correct,
            points_earned=points
        )
        self.session.moves.append(move)

        if is_correct:
            self.session.score.points += points
        else:
            self.session.mistakes_made += 1

        if self._check_game_completion():
            self._end_game()

        return is_correct, message, points

    def use_hint(self) -> Tuple[bool, str]:
        """Usar una pista"""
        if self.session.hints_used >= self._get_max_hints():
            return False, "No hay más pistas disponibles"

        hint = self._generate_hint()
        self.session.hints_used += 1

        return True, hint

    def pause_game(self):
        """Pausar el juego"""
        if self.session.status == GameStatus.PLAYING:
            self.session.status = GameStatus.PAUSED

    def resume_game(self):
        """Reanudar el juego"""
        if self.session.status == GameStatus.PAUSED:
            self.session.status = GameStatus.PLAYING

    def end_game(self, force: bool = False) -> GameScore:
        """Terminar el juego"""
        if force or self.session.status == GameStatus.PLAYING:
            self._end_game()
        return self.session.score

    def get_game_state(self) -> Dict[str, Any]:
        """Obtener estado actual del juego"""
        return {
            'game_id': self.session.game_id,
            'game_type': self.session.game_type.value,
            'status': self.session.status.value,
            'score': {
                'points': self.session.score.points,
                'total_score': self.session.score.total_score,
                'stars': self.session.score.stars
            },
            'time_elapsed': self._get_elapsed_time(),
            'moves_count': len(self.session.moves),
            'hints_used': self.session.hints_used,
            'mistakes_made': self.session.mistakes_made,
            'game_data': self.game_data
        }

    # Métodos abstractos
    def _setup_game_content(self):
        raise NotImplementedError

    def _process_move(self, action: PlayerAction, data: Any) -> Tuple[bool, str, int]:
        raise NotImplementedError

    def _check_game_completion(self) -> bool:
        raise NotImplementedError

    def _generate_hint(self) -> str:
        raise NotImplementedError

    # Métodos auxiliares
    def _setup_scoring_system(self):
        """Configurar sistema de puntuación"""
        difficulty_multipliers = {
            GameDifficulty.VERY_EASY: 1.0,
            GameDifficulty.EASY: 1.2,
            GameDifficulty.MEDIUM: 1.5,
            GameDifficulty.HARD: 2.0,
            GameDifficulty.EXPERT: 2.5
        }
        self.score_multiplier = difficulty_multipliers.get(self.difficulty, 1.0)

    def _setup_time_limits(self):
        """Configurar límites de tiempo"""
        time_limits = {
            GameDifficulty.VERY_EASY: 300,
            GameDifficulty.EASY: 240,
            GameDifficulty.MEDIUM: 180,
            GameDifficulty.HARD: 120,
            GameDifficulty.EXPERT: 90
        }
        self.session.time_limit = time_limits.get(self.difficulty, 180)

    def _get_max_hints(self) -> int:
        """Obtener número máximo de pistas"""
        hints_by_difficulty = {
            GameDifficulty.VERY_EASY: 5,
            GameDifficulty.EASY: 4,
            GameDifficulty.MEDIUM: 3,
            GameDifficulty.HARD: 2,
            GameDifficulty.EXPERT: 1
        }
        return hints_by_difficulty.get(self.difficulty, 3)

    def _check_timeout(self) -> bool:
        """Verificar si se agotó el tiempo"""
        if self.session.time_limit is None:
            return False

        elapsed = self._get_elapsed_time()
        return elapsed >= self.session.time_limit

    def _get_elapsed_time(self) -> float:
        """Obtener tiempo transcurrido en segundos"""
        if self.session.start_time:
            return (datetime.now() - self.session.start_time).total_seconds()
        return 0

    def _end_game(self):
        """Finalizar el juego y calcular puntuación final"""
        self.session.status = GameStatus.COMPLETED
        self.session.end_time = datetime.now()

        self._calculate_bonuses()
        self.session.score.calculate_total()

    def _calculate_bonuses(self):
        """Calcular bonos de tiempo y precisión"""
        if self.session.time_limit:
            time_remaining = self.session.time_limit - self._get_elapsed_time()
            if time_remaining > 0:
                self.session.score.time_bonus = int(time_remaining * 2)

        total_moves = len(self.session.moves)
        if total_moves > 0:
            correct_moves = sum(1 for move in self.session.moves if move.is_correct)
            accuracy = correct_moves / total_moves
            self.session.score.accuracy_bonus = int(accuracy * 50)

        hints_penalty = self.session.hints_used * 10
        self.session.score.bonus_points = max(0, 100 - hints_penalty)


# =============================================================================
# JUEGO: SOPA DE LETRAS
# =============================================================================

class WordSearchGame(BaseGame):
    """Juego de sopa de letras"""

    def __init__(self, difficulty: GameDifficulty, player_level: EducationLevel):
        super().__init__(GameType.WORD_SEARCH, difficulty, player_level)
        self.grid_size = self._get_grid_size()
        self.words_to_find = []
        self.found_words = set()
        self.grid = []

    def _get_grid_size(self) -> int:
        """Obtener tamaño de la cuadrícula según dificultad"""
        sizes = {
            GameDifficulty.VERY_EASY: 8,
            GameDifficulty.EASY: 10,
            GameDifficulty.MEDIUM: 12,
            GameDifficulty.HARD: 15,
            GameDifficulty.EXPERT: 18
        }
        return sizes.get(self.difficulty, 12)

    def _setup_game_content(self):
        """Configurar contenido de la sopa de letras"""
        self.words_to_find = self._generate_words()
        self.grid = self._create_grid()
        self._place_words_in_grid()
        self._fill_empty_spaces()

        self.game_data = {
            'grid': self.grid,
            'words_to_find': self.words_to_find,
            'found_words': list(self.found_words),
            'grid_size': self.grid_size
        }

    def _generate_words(self) -> List[str]:
        """Generar palabras para encontrar"""
        word_lists = {
            EducationLevel.PRIMARIA_INICIAL: [
                'CASA', 'PERRO', 'GATO', 'SOL', 'LUNA', 'AGUA', 'FUEGO', 'AMOR'
            ],
            EducationLevel.PRIMARIA_MEDIA: [
                'ESCUELA', 'MAESTRO', 'LIBRO', 'LAPIZ', 'PAPEL', 'AMIGO', 'FAMILIA', 'JARDIN'
            ],
            EducationLevel.SECUNDARIA: [
                'CONOCIMIENTO', 'CIENCIA', 'TECNOLOGIA', 'HISTORIA', 'GEOGRAFIA', 'LITERATURA', 'MATEMATICAS'
            ]
        }

        available_words = word_lists.get(self.player_level, word_lists[EducationLevel.PRIMARIA_MEDIA])

        num_words = {
            GameDifficulty.VERY_EASY: 4,
            GameDifficulty.EASY: 6,
            GameDifficulty.MEDIUM: 8,
            GameDifficulty.HARD: 10,
            GameDifficulty.EXPERT: 12
        }.get(self.difficulty, 6)

        return random.sample(available_words, min(num_words, len(available_words)))

    def _create_grid(self) -> List[List[str]]:
        """Crear cuadrícula vacía"""
        return [[' ' for _ in range(self.grid_size)] for _ in range(self.grid_size)]

    def _place_words_in_grid(self):
        """Colocar palabras en la cuadrícula"""
        directions = [
            (0, 1), (1, 0), (1, 1), (0, -1), (-1, 0), (-1, -1), (1, -1), (-1, 1)
        ]

        for word in self.words_to_find:
            placed = False
            attempts = 0

            while not placed and attempts < 100:
                row = random.randint(0, self.grid_size - 1)
                col = random.randint(0, self.grid_size - 1)
                direction = random.choice(directions)

                if self._can_place_word(word, row, col, direction):
                    self._place_word(word, row, col, direction)
                    placed = True

                attempts += 1

    def _can_place_word(self, word: str, start_row: int, start_col: int, direction: Tuple[int, int]) -> bool:
        """Verificar si se puede colocar una palabra"""
        dr, dc = direction

        for i, letter in enumerate(word):
            row = start_row + i * dr
            col = start_col + i * dc

            if row < 0 or row >= self.grid_size or col < 0 or col >= self.grid_size:
                return False

            if self.grid[row][col] != ' ' and self.grid[row][col] != letter:
                return False

        return True

    def _place_word(self, word: str, start_row: int, start_col: int, direction: Tuple[int, int]):
        """Colocar palabra en la cuadrícula"""
        dr, dc = direction

        for i, letter in enumerate(word):
            row = start_row + i * dr
            col = start_col + i * dc
            self.grid[row][col] = letter

    def _fill_empty_spaces(self):
        """Llenar espacios vacíos con letras aleatorias"""
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                if self.grid[row][col] == ' ':
                    self.grid[row][col] = random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')

    def _process_move(self, action: PlayerAction, data: Any) -> Tuple[bool, str, int]:
        """Procesar selección de palabra en sopa de letras"""
        if action != PlayerAction.SELECT_WORD:
            return False, "Acción no válida", 0

        if not isinstance(data, dict) or 'start' not in data or 'end' not in data:
            return False, "Datos de selección inválidos", 0

        start_pos = data['start']
        end_pos = data['end']

        selected_word = self._extract_word_from_selection(start_pos, end_pos)

        if selected_word in self.words_to_find and selected_word not in self.found_words:
            self.found_words.add(selected_word)
            points = len(selected_word) * 10 * self.score_multiplier
            message = f"¡Encontraste '{selected_word}'! +{int(points)} puntos"

            self.game_data['found_words'] = list(self.found_words)

            return True, message, int(points)
        else:
            return False, "Palabra no válida o ya encontrada", 0

    def _extract_word_from_selection(self, start_pos: Tuple[int, int], end_pos: Tuple[int, int]) -> str:
        """Extraer palabra de la selección"""
        start_row, start_col = start_pos
        end_row, end_col = end_pos

        dr = 0 if end_row == start_row else (1 if end_row > start_row else -1)
        dc = 0 if end_col == start_col else (1 if end_col > start_col else -1)

        word = ""
        row, col = start_row, start_col

        while True:
            if 0 <= row < self.grid_size and 0 <= col < self.grid_size:
                word += self.grid[row][col]

            if row == end_row and col == end_col:
                break

            row += dr
            col += dc

        return word

    def _check_game_completion(self) -> bool:
        """Verificar si se encontraron todas las palabras"""
        return len(self.found_words) == len(self.words_to_find)

    def _generate_hint(self) -> str:
        """Generar pista para palabra no encontrada"""
        remaining_words = [w for w in self.words_to_find if w not in self.found_words]
        if remaining_words:
            word = random.choice(remaining_words)
            return f"Busca una palabra que empiece con '{word[0]}' y tenga {len(word)} letras"
        return "¡Ya encontraste todas las palabras!"


# =============================================================================
# JUEGO: PALABRAS DESORDENADAS
# =============================================================================

class WordScrambleGame(BaseGame):
    """Juego de palabras desordenadas"""

    def __init__(self, difficulty: GameDifficulty, player_level: EducationLevel):
        super().__init__(GameType.WORD_SCRAMBLE, difficulty, player_level)
        self.words = []
        self.current_word_index = 0
        self.solved_words = set()

    def _setup_game_content(self):
        """Configurar palabras desordenadas"""
        self.words = self._generate_word_list()
        self.current_word_index = 0
        self.solved_words = set()

        self.game_data = {
            'words': [self._scramble_word(word) for word in self.words],
            'original_words': self.words,
            'current_index': self.current_word_index,
            'solved_count': len(self.solved_words),
            'total_words': len(self.words)
        }

    def _generate_word_list(self) -> List[str]:
        """Generar lista de palabras según nivel"""
        word_sets = {
            EducationLevel.PRIMARIA_INICIAL: [
                'CASA', 'MESA', 'SILLA', 'PUERTA', 'VENTANA', 'COCHE', 'BICICLETA', 'PELOTA'
            ],
            EducationLevel.PRIMARIA_MEDIA: [
                'ESCUELA', 'MAESTRO', 'ESTUDIANTE', 'BIBLIOTECA', 'CUADERNO', 'COMPUTADORA', 'TELEFONO'
            ],
            EducationLevel.SECUNDARIA: [
                'CONOCIMIENTO', 'INTELIGENCIA', 'CREATIVIDAD', 'RESPONSABILIDAD', 'PERSEVERANCIA'
            ]
        }

        available_words = word_sets.get(self.player_level, word_sets[EducationLevel.PRIMARIA_MEDIA])

        num_words = {
            GameDifficulty.VERY_EASY: 5,
            GameDifficulty.EASY: 7,
            GameDifficulty.MEDIUM: 10,
            GameDifficulty.HARD: 12,
            GameDifficulty.EXPERT: 15
        }.get(self.difficulty, 8)

        return random.sample(available_words, min(num_words, len(available_words)))

    def _scramble_word(self, word: str) -> str:
        """Desordenar una palabra"""
        letters = list(word)
        random.shuffle(letters)
        scrambled = ''.join(letters)

        attempts = 0
        while scrambled == word and attempts < 10:
            random.shuffle(letters)
            scrambled = ''.join(letters)
            attempts += 1

        return scrambled

    def _process_move(self, action: PlayerAction, data: Any) -> Tuple[bool, str, int]:
        """Procesar respuesta de palabra desordenada"""
        if action != PlayerAction.ENTER_TEXT:
            return False, "Acción no válida", 0

        user_answer = str(data).upper().strip()
        current_word = self.words[self.current_word_index]

        if user_answer == current_word:
            self.solved_words.add(self.current_word_index)
            points = len(current_word) * 15 * self.score_multiplier

            self.current_word_index += 1

            self.game_data['current_index'] = self.current_word_index
            self.game_data['solved_count'] = len(self.solved_words)

            message = f"¡Correcto! '{current_word}' +{int(points)} puntos"
            return True, message, int(points)
        else:
            return False, f"Incorrecto. La palabra era '{current_word}'", 0

    def _check_game_completion(self) -> bool:
        """Verificar si se resolvieron todas las palabras"""
        return len(self.solved_words) == len(self.words)

    def _generate_hint(self) -> str:
        """Generar pista para palabra actual"""
        if self.current_word_index < len(self.words):
            word = self.words[self.current_word_index]
            if len(word) > 2:
                return f"La palabra empieza con '{word[0]}' y termina con '{word[-1]}'"
            else:
                return f"La palabra tiene {len(word)} letras"
        return "¡Ya completaste todas las palabras!"


# =============================================================================
# MOTOR PRINCIPAL DE JUEGOS
# =============================================================================

class GameEngine:
    """Motor principal que gestiona todos los juegos"""

    def __init__(self):
        self.active_games: Dict[str, BaseGame] = {}
        self.game_classes = {
            GameType.WORD_SEARCH: WordSearchGame,
            GameType.WORD_SCRAMBLE: WordScrambleGame,
        }

        if NLP_AVAILABLE:
            self.text_analyzer = TextAnalyzer()
            self.difficulty_calculator = DifficultyCalculator()

        print("✅ GameEngine inicializado")

    def create_game(self, game_type: GameType, difficulty: GameDifficulty, player_level: EducationLevel) -> Optional[
        str]:
        """Crear nuevo juego y retornar su ID"""
        try:
            game_class = self.game_classes.get(game_type)
            if not game_class:
                logger.error(f"Tipo de juego no soportado: {game_type}")
                return None

            game = game_class(difficulty, player_level)
            if game.initialize_game():
                self.active_games[game.session.game_id] = game
                print(f"🎮 Juego creado: {game.session.game_id}")
                return game.session.game_id
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

    def make_move(self, game_id: str, action: PlayerAction, data: Any) -> Dict[str, Any]:
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

    def get_available_games(self) -> List[Dict[str, str]]:
        """Obtener lista de juegos disponibles"""
        return [
            {
                'type': game_type.value,
                'name': self._get_game_name(game_type),
                'description': self._get_game_description(game_type)
            }
            for game_type in self.game_classes.keys()
        ]

    def _get_game_name(self, game_type: GameType) -> str:
        """Obtener nombre legible del juego"""
        names = {
            GameType.WORD_SEARCH: "Sopa de Letras",
            GameType.WORD_SCRAMBLE: "Palabras Desordenadas",
        }
        return names.get(game_type, game_type.value)

    def _get_game_description(self, game_type: GameType) -> str:
        """Obtener descripción del juego"""
        descriptions = {
            GameType.WORD_SEARCH: "Encuentra palabras ocultas en una cuadrícula de letras",
            GameType.WORD_SCRAMBLE: "Ordena las letras para formar palabras correctas",
        }
        return descriptions.get(game_type, "Juego educativo interactivo")


# =============================================================================
# CÓDIGO DE PRUEBA
# =============================================================================

if __name__ == "__main__":
    print("🧪 Probando motor de juegos educativos...")

    engine = GameEngine()

    print("\n🎮 JUEGOS DISPONIBLES:")
    print("=" * 50)
    available_games = engine.get_available_games()
    for game in available_games:
        print(f"• {game['name']}: {game['description']}")

    print("\n🎯 PRUEBA DE SOPA DE LETRAS:")
    print("=" * 50)

    game_id = engine.create_game(
        GameType.WORD_SEARCH,
        GameDifficulty.EASY,
        EducationLevel.PRIMARIA_INICIAL
    )

    if game_id:
        print(f"✅ Juego creado: {game_id}")

        if engine.start_game(game_id):
            print("🚀 Juego iniciado")

            state = engine.get_game_state(game_id)
            if state:
                print(f"📊 Estado inicial:")
                print(f"  • Tamaño de cuadrícula: {state['game_data']['grid_size']}x{state['game_data']['grid_size']}")
                print(f"  • Palabras a encontrar: {len(state['game_data']['words_to_find'])}")
                print(f"  • Palabras: {', '.join(state['game_data']['words_to_find'])}")

                grid = state['game_data']['grid']
                print(f"\n🔍 Cuadrícula (primeras 5 filas):")
                for i, row in enumerate(grid[:5]):
                    print(f"  {' '.join(row[:10])}")

                hint_result = engine.use_hint(game_id)
                if hint_result['success']:
                    print(f"\n💡 Pista: {hint_result['hint']}")
                    print(f"🎯 Pistas restantes: {hint_result['hints_remaining']}")

                words_to_find = state['game_data']['words_to_find']
                if words_to_find:
                    move_result = engine.make_move(game_id, PlayerAction.SELECT_WORD, {
                        'start': (0, 0),
                        'end': (0, len(words_to_find[0]) - 1)
                    })

                    if move_result['success']:
                        print(f"\n🎯 Movimiento realizado:")
                        print(f"  • Correcto: {move_result['correct']}")
                        print(f"  • Mensaje: {move_result['message']}")
                        print(f"  • Puntos ganados: {move_result['points']}")

        else:
            print("❌ Error iniciando juego")
    else:
        print("❌ Error creando juego")

    print("\n🔤 PRUEBA DE PALABRAS DESORDENADAS:")
    print("=" * 50)

    scramble_id = engine.create_game(
        GameType.WORD_SCRAMBLE,
        GameDifficulty.EASY,
        EducationLevel.PRIMARIA_INICIAL
    )

    if scramble_id:
        print(f"✅ Juego de palabras creado: {scramble_id}")

        if engine.start_game(scramble_id):
            print("🚀 Juego iniciado")

            state = engine.get_game_state(scramble_id)
            if state:
                scrambled_words = state['game_data']['words']
                original_words = state['game_data']['original_words']

                print(f"📝 Palabras desordenadas:")
                for i, (scrambled, original) in enumerate(zip(scrambled_words[:3], original_words[:3])):
                    print(f"  {i + 1}. {scrambled} → {original}")

                if original_words:
                    move_result = engine.make_move(scramble_id, PlayerAction.ENTER_TEXT, original_words[0])
                    print(f"\n🎯 Respuesta: {original_words[0]}")
                    print(f"  • Correcto: {move_result['correct']}")
                    print(f"  • Mensaje: {move_result['message']}")
                    print(f"  • Puntos: {move_result['points']}")

    print(f"\n✅ Pruebas del motor de juegos completadas!")
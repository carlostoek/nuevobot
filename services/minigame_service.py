# services/minigame_service.py
import sqlite3
import random
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import json
import time

class MinigameType(Enum):
    TRIVIA = "trivia"
    MEMORY = "memoria"
    RIDDLE = "acertijo"
    PUZZLE = "puzzle"

class DifficultyLevel(Enum):
    EASY = "fácil"
    MEDIUM = "medio"
    HARD = "difícil"

@dataclass
class TriviaQuestion:
    id: int
    question: str
    options: List[str]
    correct_answer: int
    difficulty: DifficultyLevel
    category: str
    points: int

@dataclass
class MinigameSession:
    user_id: int
    game_type: MinigameType
    start_time: float
    current_question: int = 0
    score: int = 0
    total_questions: int = 5
    time_limit: int = 60
    is_active: bool = True
    answers: List[int] = None
    
    def __post_init__(self):
        if self.answers is None:
            self.answers = []

@dataclass
class GameResult:
    score: int
    total_questions: int
    correct_answers: int
    time_taken: float
    points_earned: int
    rank: str

class MinigameService:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.active_sessions: Dict[int, MinigameSession] = {}
        self._init_trivia_data()
    
    def _init_trivia_data(self):
        """Inicializa preguntas de trivia base"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        trivia_questions = [
            (1, "¿Cuál es la capital de Francia?", 
             '["París", "Londres", "Madrid", "Roma"]', 0, "EASY", "geografía", 10),
            (2, "¿En qué año llegó el hombre a la luna?", 
             '["1969", "1968", "1970", "1971"]', 0, "MEDIUM", "historia", 20),
            (3, "¿Cuál es el elemento químico con símbolo 'Au'?", 
             '["Plata", "Oro", "Aluminio", "Argón"]', 1, "MEDIUM", "ciencia", 20),
            (4, "¿Quién escribió 'Don Quijote de la Mancha'?", 
             '["Lope de Vega", "Garcilaso", "Cervantes", "Góngora"]', 2, "EASY", "literatura", 10),
            (5, "¿Cuál es la fórmula del agua?", 
             '["H2O", "CO2", "NaCl", "CH4"]', 0, "EASY", "ciencia", 10),
        ]
        
        cursor.executemany('''
            INSERT OR IGNORE INTO trivias 
            (id, question, options, correct_answer, difficulty, category, points)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', trivia_questions)
        
        conn.commit()
        conn.close()
    
    def start_trivia_game(self, user_id: int, difficulty: str = "EASY") -> MinigameSession:
        """Inicia un juego de trivia"""
        session = MinigameSession(
            user_id=user_id,
            game_type=MinigameType.TRIVIA,
            start_time=time.time(),
            time_limit=120  # 2 minutos para trivia
        )
        
        self.active_sessions[user_id] = session
        return session
    
    def get_trivia_question(self, user_id: int) -> Optional[TriviaQuestion]:
        """Obtiene la siguiente pregunta de trivia"""
        if user_id not in self.active_sessions:
            return None
        
        session = self.active_sessions[user_id]
        
        if session.current_question >= session.total_questions:
            return None
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, question, options, correct_answer, difficulty, category, points
            FROM trivias 
            ORDER BY RANDOM() 
            LIMIT 1
        ''')
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        return TriviaQuestion(
            id=row[0],
            question=row[1],
            options=json.loads(row[2]),
            correct_answer=row[3],
            difficulty=DifficultyLevel(row[4]),
            category=row[5],
            points=row[6]
        )
    
    def submit_trivia_answer(self, user_id: int, answer: int) -> Tuple[bool, int]:
        """Envía respuesta de trivia y retorna (es_correcto, puntos)"""
        if user_id not in self.active_sessions:
            return False, 0
        
        session = self.active_sessions[user_id]
        
        # Verificar tiempo límite
        if time.time() - session.start_time > session.time_limit:
            session.is_active = False
            return False, 0
        
        # Obtener pregunta actual
        question = self.get_trivia_question(user_id)
        if not question:
            return False, 0
        
        is_correct = answer == question.correct_answer
        points = question.points if is_correct else 0
        
        session.answers.append(answer)
        session.score += points
        session.current_question += 1
        
        return is_correct, points
    
    def finish_game(self, user_id: int) -> Optional[GameResult]:
        """Finaliza el juego y retorna resultado"""
        if user_id not in self.active_sessions:
            return None
        
        session = self.active_sessions[user_id]
        time_taken = time.time() - session.start_time
        
        correct_answers = sum(1 for i, answer in enumerate(session.answers) 
                            if self._is_answer_correct(i, answer))
        
        # Calcular rango
        accuracy = correct_answers / session.total_questions if session.total_questions > 0 else 0
        if accuracy >= 0.9:
            rank = "🏆 Maestro"
        elif accuracy >= 0.7:
            rank = "⭐ Experto"
        elif accuracy >= 0.5:
            rank = "✨ Competente"
        else:
            rank = "🌟 Aprendiz"
        
        result = GameResult(
            score=session.score,
            total_questions=session.total_questions,
            correct_answers=correct_answers,
            time_taken=time_taken,
            points_earned=session.score,
            rank=rank
        )
        
        # Guardar estadísticas
        self._save_game_stats(user_id, session, result)
        
        # Limpiar sesión
        del self.active_sessions[user_id]
        
        return result
    
    def _is_answer_correct(self, question_index: int, answer: int) -> bool:
        """Verifica si una respuesta es correcta (simplificado)"""
        # En implementación real, almacenaríamos las preguntas de la sesión
        return True  # Placeholder
    
    def _save_game_stats(self, user_id: int, session: MinigameSession, result: GameResult):
        """Guarda estadísticas del juego"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO minigame_scores 
            (user_id, game_type, score, questions_total, questions_correct, 
             time_taken, points_earned, played_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))
        ''', (user_id, session.game_type.value, result.score, 
              result.total_questions, result.correct_answers,
              result.time_taken, result.points_earned))
        
        conn.commit()
        conn.close()
    
    def get_user_stats(self, user_id: int) -> Dict:
        """Obtiene estadísticas del usuario"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT game_type, COUNT(*) as games_played, 
                   AVG(score) as avg_score, MAX(score) as best_score,
                   SUM(points_earned) as total_points
            FROM minigame_scores 
            WHERE user_id = ?
            GROUP BY game_type
        ''', (user_id,))
        
        stats = {}
        for row in cursor.fetchall():
            stats[row[0]] = {
                'games_played': row[1],
                'avg_score': round(row[2], 2),
                'best_score': row[3],
                'total_points': row[4]
            }
        
        conn.close()
        return stats
    
    def get_active_session(self, user_id: int) -> Optional[MinigameSession]:
        """Obtiene sesión activa del usuario"""
        return self.active_sessions.get(user_id)
# services/narrative_service.py
import sqlite3
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import random
import json

class LoreRarity(Enum):
    COMMON = "Común"
    UNCOMMON = "Poco Común"
    RARE = "Raro"
    EPIC = "Épico"
    LEGENDARY = "Legendario"

@dataclass
class LorePiece:
    id: int
    title: str
    content: str
    rarity: LoreRarity
    category: str
    unlock_condition: str
    combinations: List[int] = None
    
    def __post_init__(self):
        if self.combinations is None:
            self.combinations = []

@dataclass 
class CombinationResult:
    success: bool
    result_lore_id: Optional[int] = None
    message: str = ""
    new_lore: Optional[LorePiece] = None

class NarrativeService:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_lore_data()
    
    def _init_lore_data(self):
        """Inicializa lore pieces base en la DB"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Lore pieces base
        base_lore = [
            (1, "El Despertar", "Tu aventura comienza en un mundo lleno de misterios...", 
             "COMMON", "historia", "inicial"),
            (2, "Primera Victoria", "Has demostrado tu valor en el combate...", 
             "UNCOMMON", "logro", "ganar_primer_combate"),
            (3, "Explorador", "Los caminos secretos se revelan ante ti...", 
             "RARE", "exploración", "explorar_10_lugares"),
            (4, "Fragmento Antiguo", "Un pedazo de historia olvidada...", 
             "EPIC", "artefacto", "combinar_lore_1_2"),
        ]
        
        cursor.executemany('''
            INSERT OR IGNORE INTO lore_pieces 
            (id, title, content, rarity, category, unlock_condition)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', base_lore)
        
        conn.commit()
        conn.close()
    
    def get_user_lore_pieces(self, user_id: int) -> List[LorePiece]:
        """Obtiene todos los lore pieces del usuario"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT lp.id, lp.title, lp.content, lp.rarity, lp.category, lp.unlock_condition
            FROM lore_pieces lp
            JOIN user_lore_pieces ulp ON lp.id = ulp.lore_piece_id
            WHERE ulp.user_id = ?
            ORDER BY ulp.unlocked_at DESC
        ''', (user_id,))
        
        lore_pieces = []
        for row in cursor.fetchall():
            lore_pieces.append(LorePiece(
                id=row[0],
                title=row[1], 
                content=row[2],
                rarity=LoreRarity(row[3]),
                category=row[4],
                unlock_condition=row[5]
            ))
        
        conn.close()
        return lore_pieces
    
    def unlock_lore_piece(self, user_id: int, lore_id: int) -> bool:
        """Desbloquea un lore piece para el usuario"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Verificar si ya está desbloqueado
        cursor.execute('''
            SELECT 1 FROM user_lore_pieces 
            WHERE user_id = ? AND lore_piece_id = ?
        ''', (user_id, lore_id))
        
        if cursor.fetchone():
            conn.close()
            return False
        
        # Desbloquear
        cursor.execute('''
            INSERT INTO user_lore_pieces (user_id, lore_piece_id, unlocked_at)
            VALUES (?, ?, datetime('now'))
        ''', (user_id, lore_id))
        
        conn.commit()
        conn.close()
        return True
    
    def get_lore_piece_by_id(self, lore_id: int) -> Optional[LorePiece]:
        """Obtiene un lore piece específico"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, title, content, rarity, category, unlock_condition
            FROM lore_pieces WHERE id = ?
        ''', (lore_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
            
        return LorePiece(
            id=row[0],
            title=row[1],
            content=row[2], 
            rarity=LoreRarity(row[3]),
            category=row[4],
            unlock_condition=row[5]
        )
    
    def attempt_combination(self, user_id: int, lore_ids: List[int]) -> CombinationResult:
        """Intenta combinar lore pieces"""
        if len(lore_ids) < 2:
            return CombinationResult(False, message="Necesitas al menos 2 lore pieces")
        
        # Verificar que el usuario tiene todos los lore pieces
        user_lore = self.get_user_lore_pieces(user_id)
        user_lore_ids = {lore.id for lore in user_lore}
        
        if not all(lore_id in user_lore_ids for lore_id in lore_ids):
            return CombinationResult(False, message="No posees todos los lore pieces")
        
        # Buscar combinación válida
        combination_key = "_".join(map(str, sorted(lore_ids)))
        result_lore = self._check_combination(combination_key)
        
        if result_lore:
            # Desbloquear nuevo lore
            if self.unlock_lore_piece(user_id, result_lore.id):
                return CombinationResult(
                    True, 
                    result_lore.id,
                    f"¡Combinación exitosa! Desbloqueaste: {result_lore.title}",
                    result_lore
                )
            else:
                return CombinationResult(False, message="Ya posees este lore")
        
        return CombinationResult(False, message="Esta combinación no produce nada")
    
    def _check_combination(self, combination_key: str) -> Optional[LorePiece]:
        """Verifica si una combinación es válida"""
        combinations = {
            "1_2": 4,  # Despertar + Primera Victoria = Fragmento Antiguo
            "2_3": 5,  # Primera Victoria + Explorador = Nuevo lore
        }
        
        if combination_key in combinations:
            return self.get_lore_piece_by_id(combinations[combination_key])
        
        return None
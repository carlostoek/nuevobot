# utils/keyboards.py - EXTENSIONES NARRATIVA Y MINIJUEGOS

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List

# === TECLADOS DE NARRATIVA ===

def get_backpack_keyboard(lore_pieces: List, can_combine: bool = False) -> InlineKeyboardMarkup:
    """Teclado de mochila narrativa"""
    buttons = []
    
    # Lore pieces (máximo 6 por página)
    for i, lore in enumerate(lore_pieces[:6]):
        rarity_emoji = {"COMMON": "⚪", "UNCOMMON": "🟢", "RARE": "🔵", "EPIC": "🟣", "LEGENDARY": "🟡"}
        emoji = rarity_emoji.get(lore.rarity.value, "⚪")
        buttons.append([InlineKeyboardButton(
            text=f"{emoji} {lore.title}", 
            callback_data=f"view_lore_{lore.id}"
        )])
    
    # Opciones adicionales
    if can_combine:
        buttons.append([InlineKeyboardButton(text="🗝️ Combinar Lore", callback_data="combine_lore")])
    
    buttons.append([InlineKeyboardButton(text="🔙 Volver", callback_data="back_to_main")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_lore_detail_keyboard(lore_id: int) -> InlineKeyboardMarkup:
    """Teclado de detalles de lore"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Volver a Mochila", callback_data="back_to_backpack")]
    ])

def get_combination_keyboard(lore_pieces: List, selected: List[int]) -> InlineKeyboardMarkup:
    """Teclado de combinación de lore"""
    buttons = []
    
    for lore in lore_pieces:
        emoji = "✅" if lore.id in selected else "⚪"
        buttons.append([InlineKeyboardButton(
            text=f"{emoji} {lore.title}",
            callback_data=f"toggle_lore_{lore.id}"
        )])
    
    # Controles
    controls = []
    if len(selected) >= 2:
        controls.append(InlineKeyboardButton(text="🗝️ Intentar Combinación", callback_data="attempt_combination"))
    
    controls.append(InlineKeyboardButton(text="🔙 Cancelar", callback_data="back_to_backpack"))
    buttons.append(controls)
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# === TECLADOS DE MINIJUEGOS ===

def get_minigames_menu_keyboard() -> InlineKeyboardMarkup:
    """Menú principal de minijuegos"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🧠 Trivia", callback_data="start_trivia")],
        [InlineKeyboardButton(text="📊 Mis Estadísticas", callback_data="view_stats")],
        [InlineKeyboardButton(text="🏆 Ranking", callback_data="view_ranking")],
        [InlineKeyboardButton(text="🔙 Volver", callback_data="back_to_main")]
    ])

def get_trivia_options_keyboard(options: List[str], question_id: int) -> InlineKeyboardMarkup:
    """Teclado de opciones de trivia"""
    buttons = []
    
    for i, option in enumerate(options):
        buttons.append([InlineKeyboardButton(
            text=f"{chr(65+i)}. {option}",
            callback_data=f"trivia_answer_{i}"
        )])
    
    buttons.append([InlineKeyboardButton(text="🚪 Abandonar", callback_data="quit_game")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_stats_keyboard() -> InlineKeyboardMarkup:
    """Teclado de estadísticas"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Volver a Juegos", callback_data="back_to_minigames")]
    ])

# ===== utils/messages.py - EXTENSIONES =====

from services.narrative_service import LorePiece, CombinationResult
from services.minigame_service import TriviaQuestion, GameResult
from typing import Dict

# === MENSAJES DE NARRATIVA ===

def format_lore_piece(lore: LorePiece) -> str:
    """Formatea un lore piece para mostrar"""
    rarity_emojis = {
        "COMMON": "⚪ Común",
        "UNCOMMON": "🟢 Poco Común", 
        "RARE": "🔵 Raro",
        "EPIC": "🟣 Épico",
        "LEGENDARY": "🟡 Legendario"
    }
    
    return f"""📖 Lore Desbloqueado

🗝️ {lore.title}

{lore.content}

⭐ Rareza: {rarity_emojis.get(lore.rarity.value, lore.rarity.value)}
🏷️ Categoría: {lore.category.title()}"""

def format_combination_result(result: CombinationResult) -> str:
    """Formatea resultado de combinación"""
    if result.success:
        return f"""🗝️ ¡Combinación Exitosa!

✨ {result.message}

🎁 Has desbloqueado nuevo lore"""
    else:
        return f"""❌ Combinación Fallida

{result.message}

💡 Prueba otras combinaciones"""

# === MENSAJES DE MINIJUEGOS ===

def format_trivia_question(question: TriviaQuestion) -> str:
    """Formatea pregunta de trivia"""
    return f"""❓ {question.question}

🏷️ Categoría: {question.category.title()}
💎 Puntos: {question.points}"""

def format_game_result(result: GameResult) -> str:
    """Formatea resultado del juego"""
    accuracy = (result.correct_answers / result.total_questions) * 100
    
    return f"""🏆 Resultado Final

🎯 Puntuación: {result.score}
✅ Correctas: {result.correct_answers}/{result.total_questions}
📊 Precisión: {accuracy:.1f}%
⏱️ Tiempo: {result.time_taken:.1f}s
🏅 Rango: {result.rank}

💎 Puntos ganados: {result.points_earned}"""

def format_user_stats(stats: Dict, username: str) -> str:
    """Formatea estadísticas del usuario"""
    if not stats:
        return f"""📊 Estadísticas de {username}

¡Aún no has jugado ningún minijuego!

🎲 ¿Quieres empezar tu primera partida?"""
    
    text = f"📊 Estadísticas de {username}\n\n"
    
    for game_type, data in stats.items():
        text += f"""🎮 {game_type.title()}:
   🕹️ Partidas: {data['games_played']}
   📈 Promedio: {data['avg_score']}
   🏆 Mejor: {data['best_score']}
   💎 Puntos: {data['total_points']}

"""
    
    return text
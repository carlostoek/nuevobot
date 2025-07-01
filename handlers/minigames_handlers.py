# handlers/minigames_handlers.py
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from services.minigame_service import MinigameService, MinigameType
from utils.keyboards import get_minigames_menu_keyboard, get_trivia_options_keyboard, get_stats_keyboard
from utils.messages import format_trivia_question, format_game_result, format_user_stats
from middlewares.session_middleware import SessionData
import logging

logger = logging.getLogger(__name__)

class MinigameStates(StatesGroup):
    menu = State()
    playing_trivia = State()
    viewing_stats = State()

router = Router()

@router.message(Command("juegos"))
@router.callback_query(F.data == "open_minigames")
async def show_minigames_menu(update, state: FSMContext, session: SessionData):
    """Muestra el menú principal de minijuegos"""
    text = """🎲 Centro de Minijuegos

¡Pon a prueba tus conocimientos y habilidades!

🧠 Trivia - Responde preguntas y gana puntos
📊 Estadísticas - Ve tu progreso
🏆 Ranking - Compite con otros jugadores

¿Qué te gustaría hacer?"""
    
    keyboard = get_minigames_menu_keyboard()
    
    await state.set_state(MinigameStates.menu)
    
    if isinstance(update, CallbackQuery):
        await update.message.edit_text(text, reply_markup=keyboard)
        await update.answer()
    else:
        await update.answer(text, reply_markup=keyboard)

@router.callback_query(F.data == "start_trivia")
async def start_trivia_game(callback: CallbackQuery, state: FSMContext, session: SessionData, minigame_service: MinigameService):
    """Inicia un juego de trivia"""
    user_id = callback.from_user.id
    
    # Verificar si ya hay un juego activo
    if session.active_minigame:
        await callback.answer("❌ Ya tienes un juego activo", show_alert=True)
        return
    
    # Iniciar nueva sesión de trivia
    game_session = minigame_service.start_trivia_game(user_id)
    session.active_minigame = "trivia"
    
    # Obtener primera pregunta
    question = minigame_service.get_trivia_question(user_id)
    
    if not question:
        await callback.answer("❌ No hay preguntas disponibles", show_alert=True)
        return
    
    text = f"""🎲 ¡Trivia Iniciada!

⚡ Pregunta {game_session.current_question + 1}/{game_session.total_questions}
🎯 Puntos: {game_session.score}

{format_trivia_question(question)}"""
    
    keyboard = get_trivia_options_keyboard(question.options, question.id)
    
    await state.set_state(MinigameStates.playing_trivia)
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()

@router.callback_query(F.data.startswith("trivia_answer_"))
async def handle_trivia_answer(callback: CallbackQuery, state: FSMContext, session: SessionData, minigame_service: MinigameService):
    """Maneja la respuesta de trivia"""
    user_id = callback.from_user.id
    answer = int(callback.data.split("_")[2])
    
    # Verificar sesión activa
    if not session.active_minigame or session.active_minigame != "trivia":
        await callback.answer("❌ No hay juego activo", show_alert=True)
        return
    
    # Enviar respuesta
    is_correct, points = minigame_service.submit_trivia_answer(user_id, answer)
    
    # Obtener sesión actualizada
    game_session = minigame_service.get_active_session(user_id)
    
    if not game_session or not game_session.is_active:
        await callback.answer("⏰ Tiempo agotado", show_alert=True)
        session.active_minigame = None
        await show_minigames_menu(callback, state, session)
        return
    
    # Feedback de respuesta
    feedback = "✅ ¡Correcto!" if is_correct else "❌ Incorrecto"
    if points > 0:
        feedback += f" +{points} puntos"
    
    # Verificar si el juego terminó
    if game_session.current_question >= game_session.total_questions:
        result = minigame_service.finish_game(user_id)
        session.active_minigame = None
        
        text = f"""{feedback}

🏁 ¡Juego Terminado!

{format_game_result(result)}"""
        
        keyboard = get_minigames_menu_keyboard()
        await state.set_state(MinigameStates.menu)
        await callback.message.edit_text(text, reply_markup=keyboard)
        await callback.answer()
        return
    
    # Siguiente pregunta
    next_question = minigame_service.get_trivia_question(user_id)
    
    if not next_question:
        await callback.answer("❌ Error al cargar pregunta", show_alert=True)
        return
    
    text = f"""{feedback}

⚡ Pregunta {game_session.current_question + 1}/{game_session.total_questions}
🎯 Puntos: {game_session.score}

{format_trivia_question(next_question)}"""
    
    keyboard = get_trivia_options_keyboard(next_question.options, next_question.id)
    
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()

@router.callback_query(F.data == "view_stats")
async def show_user_stats(callback: CallbackQuery, state: FSMContext, minigame_service: MinigameService):
    """Muestra estadísticas del usuario"""
    user_id = callback.from_user.id
    
    stats = minigame_service.get_user_stats(user_id)
    
    text = format_user_stats(stats, callback.from_user.first_name)
    keyboard = get_stats_keyboard()
    
    await state.set_state(MinigameStates.viewing_stats)
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()

@router.callback_query(F.data == "quit_game")
async def quit_current_game(callback: CallbackQuery, state: FSMContext, session: SessionData, minigame_service: MinigameService):
    """Abandona el juego actual"""
    user_id = callback.from_user.id
    
    if session.active_minigame:
        # Finalizar juego actual
        minigame_service.finish_game(user_id)
        session.active_minigame = None
        
        text = "🚪 Has abandonado el juego\n\n¿Quieres intentar otro desafío?"
    else:
        text = "❌ No hay juego activo para abandonar"
    
    keyboard = get_minigames_menu_keyboard()
    await state.set_state(MinigameStates.menu)
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()

@router.callback_query(F.data == "back_to_minigames")
async def back_to_minigames(callback: CallbackQuery, state: FSMContext, session: SessionData):
    """Regresa al menú de minijuegos"""
    await show_minigames_menu(callback, state, session)
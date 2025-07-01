# handlers/narrative_handlers.py
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from services.narrative_service import NarrativeService, LoreRarity
from utils.keyboards import get_backpack_keyboard, get_lore_detail_keyboard, get_combination_keyboard
from utils.messages import format_lore_piece, format_combination_result
from middlewares.session_middleware import SessionData
import logging

logger = logging.getLogger(__name__)

class NarrativeStates(StatesGroup):
    viewing_backpack = State()
    viewing_lore = State()
    combining_lore = State()

router = Router()

@router.message(Command("mochila"))
@router.callback_query(F.data == "open_backpack")
async def show_backpack(update, state: FSMContext, session: SessionData, narrative_service: NarrativeService):
    """Muestra la mochila narrativa del usuario"""
    user_id = update.from_user.id
    
    lore_pieces = narrative_service.get_user_lore_pieces(user_id)
    
    if not lore_pieces:
        text = "🎒 Tu mochila está vacía\n\n¡Explora y completa desafíos para desbloquear lore!"
        keyboard = get_backpack_keyboard([], can_combine=False)
    else:
        text = f"🎒 Tu Mochila Narrativa\n\n📖 Lore Pieces: {len(lore_pieces)}\n\nSelecciona un lore para ver detalles:"
        keyboard = get_backpack_keyboard(lore_pieces, can_combine=len(lore_pieces) >= 2)
    
    await state.set_state(NarrativeStates.viewing_backpack)
    
    if isinstance(update, CallbackQuery):
        await update.message.edit_text(text, reply_markup=keyboard)
        await update.answer()
    else:
        await update.answer(text, reply_markup=keyboard)

@router.callback_query(F.data.startswith("view_lore_"))
async def view_lore_detail(callback: CallbackQuery, state: FSMContext, narrative_service: NarrativeService):
    """Muestra detalles de un lore piece específico"""
    lore_id = int(callback.data.split("_")[2])
    
    lore_piece = narrative_service.get_lore_piece_by_id(lore_id)
    
    if not lore_piece:
        await callback.answer("❌ Lore no encontrado", show_alert=True)
        return
    
    text = format_lore_piece(lore_piece)
    keyboard = get_lore_detail_keyboard(lore_id)
    
    await state.set_state(NarrativeStates.viewing_lore)
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()

@router.callback_query(F.data == "combine_lore")
async def start_combination(callback: CallbackQuery, state: FSMContext, session: SessionData, narrative_service: NarrativeService):
    """Inicia el proceso de combinación de lore"""
    user_id = callback.from_user.id
    
    lore_pieces = narrative_service.get_user_lore_pieces(user_id)
    
    if len(lore_pieces) < 2:
        await callback.answer("❌ Necesitas al menos 2 lore pieces para combinar", show_alert=True)
        return
    
    session.combining_lore = []
    
    text = "🗝️ Combinación de Lore\n\nSelecciona 2 o más lore pieces para intentar una combinación:\n\n💡 Tip: Algunos lore pieces tienen conexiones secretas..."
    keyboard = get_combination_keyboard(lore_pieces, session.combining_lore)
    
    await state.set_state(NarrativeStates.combining_lore)
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()

@router.callback_query(F.data.startswith("toggle_lore_"))
async def toggle_lore_selection(callback: CallbackQuery, state: FSMContext, session: SessionData, narrative_service: NarrativeService):
    """Alterna la selección de lore para combinación"""
    lore_id = int(callback.data.split("_")[2])
    user_id = callback.from_user.id
    
    if lore_id in session.combining_lore:
        session.combining_lore.remove(lore_id)
    else:
        session.combining_lore.append(lore_id)
    
    lore_pieces = narrative_service.get_user_lore_pieces(user_id)
    keyboard = get_combination_keyboard(lore_pieces, session.combining_lore)
    
    # Actualizar texto con selección actual
    selected_titles = []
    for piece in lore_pieces:
        if piece.id in session.combining_lore:
            selected_titles.append(piece.title)
    
    text = "🗝️ Combinación de Lore\n\nSelecciona 2 o más lore pieces para intentar una combinación:\n\n"
    if selected_titles:
        text += f"✅ Seleccionados: {', '.join(selected_titles)}\n\n"
    text += "💡 Tip: Algunos lore pieces tienen conexiones secretas..."
    
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()

@router.callback_query(F.data == "attempt_combination")
async def attempt_combination(callback: CallbackQuery, state: FSMContext, session: SessionData, narrative_service: NarrativeService):
    """Intenta realizar la combinación seleccionada"""
    user_id = callback.from_user.id
    
    if len(session.combining_lore) < 2:
        await callback.answer("❌ Selecciona al menos 2 lore pieces", show_alert=True)
        return
    
    result = narrative_service.attempt_combination(user_id, session.combining_lore)
    
    text = format_combination_result(result)
    
    if result.success and result.new_lore:
        # Mostrar el nuevo lore desbloqueado
        text += f"\n\n{format_lore_piece(result.new_lore)}"
    
    # Limpiar selección
    session.combining_lore = []
    
    # Regresar a la mochila
    lore_pieces = narrative_service.get_user_lore_pieces(user_id)
    keyboard = get_backpack_keyboard(lore_pieces, can_combine=len(lore_pieces) >= 2)
    
    await state.set_state(NarrativeStates.viewing_backpack)
    await callback.message.edit_text(text + f"\n\n🎒 Tu Mochila Narrativa\n\n📖 Lore Pieces: {len(lore_pieces)}", reply_markup=keyboard)
    await callback.answer()

@router.callback_query(F.data == "back_to_backpack")
async def back_to_backpack(callback: CallbackQuery, state: FSMContext, session: SessionData, narrative_service: NarrativeService):
    """Regresa a la vista principal de la mochila"""
    session.combining_lore = []
    await show_backpack(callback, state, session, narrative_service)
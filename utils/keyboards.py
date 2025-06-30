from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

MAIN_MENU = ReplyKeyboardMarkup(resize_keyboard=True)
MAIN_MENU.add(
    KeyboardButton('🏠 Inicio'),
    KeyboardButton('🎁 Regalo Diario'),
    KeyboardButton('🏆 Mi Perfil'),
)
MAIN_MENU.add(
    KeyboardButton('📺 Canales'),
    KeyboardButton('🔙 Volver'),
)

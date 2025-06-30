from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

MAIN_MENU = ReplyKeyboardMarkup(resize_keyboard=True)
MAIN_MENU.row(
    KeyboardButton('🏠 Inicio'),
    KeyboardButton('🎁 Regalo Diario'),
    KeyboardButton('🏆 Mi Perfil'),
)
MAIN_MENU.row(
    KeyboardButton('🎯 Misiones'),
    KeyboardButton('🎲 Juegos'),
)
MAIN_MENU.row(
    KeyboardButton('📺 Canales'),
    KeyboardButton('🔙 Volver'),
)

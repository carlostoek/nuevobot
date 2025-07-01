from aiogram import Router, types, F
from services.auction_service import AuctionService
from keyboards import auction_keyboard
from utils.messages import active_auction_message, finished_auction_message
from middlewares.session_middleware import SessionMiddleware

router = Router()
router.message.middleware(SessionMiddleware())

@router.message(F.text == "🛍️ Subastas Activas")
async def active_auctions(message: types.Message):
    auction = await AuctionService.create_auction("Item Especial 🎭", 100)
    await message.answer(active_auction_message(auction.item_name, auction.current_bid, auction.end_time), reply_markup=auction_keyboard())

@router.callback_query(F.data.startswith("bid_"))
async def make_bid(callback: types.CallbackQuery):
    _, auction_id = callback.data.split("_")
    success = await AuctionService.place_bid(int(auction_id), callback.from_user.id, MIN_AUCTION_BID)
    if success:
        await callback.answer("🔨 Oferta realizada con éxito.", show_alert=True)
    else:
        await callback.answer("❌ Oferta no válida.", show_alert=True)
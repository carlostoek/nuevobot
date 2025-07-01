from database.models import Auction, AuctionBid
from database.database import async_session
from datetime import datetime, timedelta
from sqlalchemy import select
from config import MAX_AUCTION_DAYS, MIN_AUCTION_BID

class AuctionService:
    @staticmethod
    async def create_auction(item_name, starting_bid):
        end_time = datetime.utcnow() + timedelta(days=MAX_AUCTION_DAYS)
        async with async_session() as session:
            auction = Auction(item_name=item_name, current_bid=starting_bid, end_time=end_time)
            session.add(auction)
            await session.commit()
            return auction

    @staticmethod
    async def place_bid(auction_id, user_id, bid_amount):
        async with async_session() as session:
            auction = await session.get(Auction, auction_id)
            if auction and bid_amount > auction.current_bid and datetime.utcnow() < auction.end_time:
                auction.current_bid = bid_amount
                bid = AuctionBid(auction_id=auction_id, user_id=user_id, bid_amount=bid_amount, bid_time=datetime.utcnow())
                session.add(bid)
                await session.commit()
                return True
            return False

    @staticmethod
    async def finalize_auction(auction_id):
        async with async_session() as session:
            auction = await session.get(Auction, auction_id)
            if auction and datetime.utcnow() >= auction.end_time:
                winner_bid = await session.execute(select(AuctionBid).where(AuctionBid.auction_id == auction_id).order_by(AuctionBid.bid_amount.desc()))
                winner_bid = winner_bid.scalars().first()
                return winner_bid
            return None
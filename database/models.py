from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from database.base import Base

class Auction(Base):
    __tablename__ = 'auctions'
    id = Column(Integer, primary_key=True)
    item_name = Column(String, nullable=False)
    current_bid = Column(Integer, default=0)
    end_time = Column(DateTime, nullable=False)

class AuctionBid(Base):
    __tablename__ = 'auction_bids'
    id = Column(Integer, primary_key=True)
    auction_id = Column(Integer, ForeignKey('auctions.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    bid_amount = Column(Integer, nullable=False)
    bid_time = Column(DateTime, nullable=False)

class VIPToken(Base):
    __tablename__ = 'vip_tokens'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    token = Column(String, unique=True, nullable=False)
    expiry_date = Column(DateTime, nullable=False)

class VIPContent(Base):
    __tablename__ = 'vip_content'
    id = Column(Integer, primary_key=True)
    content_type = Column(String, nullable=False)
    content_data = Column(Text, nullable=False)

class ExclusiveChannel(Base):
    __tablename__ = 'exclusive_channels'
    id = Column(Integer, primary_key=True)
    channel_id = Column(String, unique=True, nullable=False)
    description = Column(String)
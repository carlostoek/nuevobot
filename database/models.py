from sqlalchemy import Column, Integer, String, DateTime, Boolean, Date, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, unique=True, index=True, nullable=False)
    username = Column(String)
    first_name = Column(String)
    besitos = Column(Integer, default=0)
    level = Column(Integer, default=1)
    vip_status = Column(Boolean, default=False)
    vip_expires_at = Column(DateTime)
    last_daily_gift = Column(Date)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    channels = relationship('UserChannel', back_populates='user')

class Channel(Base):
    __tablename__ = 'channels'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    users = relationship('UserChannel', back_populates='channel')

class UserChannel(Base):
    __tablename__ = 'user_channels'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    channel_id = Column(Integer, ForeignKey('channels.id'))
    user = relationship('User', back_populates='channels')
    channel = relationship('Channel', back_populates='users')

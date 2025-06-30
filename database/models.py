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

class Mission(Base):
    __tablename__ = 'missions'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)
    reward_besitos = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    user_missions = relationship('UserMission', back_populates='mission')

class UserMission(Base):
    __tablename__ = 'user_missions'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    mission_id = Column(Integer, ForeignKey('missions.id'))
    progress = Column(Integer, default=0)
    completed = Column(Boolean, default=False)
    assigned_at = Column(DateTime, default=datetime.utcnow)
    user = relationship('User')
    mission = relationship('Mission', back_populates='user_missions')

class UserAchievement(Base):
    __tablename__ = 'user_achievements'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    name = Column(String)
    achieved_at = Column(DateTime, default=datetime.utcnow)
    user = relationship('User')

class LorePiece(Base):
    __tablename__ = 'lore_pieces'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    description = Column(String)

class UserLorePiece(Base):
    __tablename__ = 'user_lore_pieces'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    lore_piece_id = Column(Integer, ForeignKey('lore_pieces.id'))
    acquired_at = Column(DateTime, default=datetime.utcnow)
    user = relationship('User')
    lore_piece = relationship('LorePiece')

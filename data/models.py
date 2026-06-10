from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Instrument(Base):
    __tablename__ = 'instruments'
    id = Column(Integer, primary_key=True)
    ticker = Column(String, unique=True)

class Position(Base):
    __tablename__ = 'positions'
    id = Column(Integer, primary_key=True)
    instrument_id = Column(Integer)
    quantity = Column(Float)

class Order(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True)
    order_ref = Column(String, unique=True)
    side = Column(String)
    quantity = Column(Float)
    status = Column(String)

class RiskSnapshot(Base):
    __tablename__ = 'risk_snapshots'
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    var_95 = Column(Float)

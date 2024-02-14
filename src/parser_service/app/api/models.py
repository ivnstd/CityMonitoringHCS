from sqlalchemy import Column, Integer, String, DateTime, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Message(Base):
    __tablename__ = 'messages'

    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, default=datetime.utcnow)
    from_user = Column(String, index=True)
    text = Column(String, nullable=True)
    image = Column(LargeBinary, nullable=True)

from sqlalchemy import Column, Integer, String, LargeBinary
from sqlalchemy.orm import relationship

from app.db.database import Base


class User(Base):
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, index=True)
    email = Column(String, unique=True, index=True, nullable=True)
    age = Column(Integer)
    hashed_password = Column(LargeBinary)
    tasks = relationship("Task", back_populates="owner")

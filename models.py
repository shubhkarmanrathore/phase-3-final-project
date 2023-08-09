import bcrypt
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (create_engine, desc,
    Index, Column, DateTime, Integer, String)

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    username = Column(String(25), unique=True)
    password = Column("password", String, nullable=False)

    def set_password(self, password):
        salt = bcrypt.gensalt()
        self._password = bcrypt.hashpw(password.encode("utf-8"), salt)

    def check_password(self, password):
        return bcrypt.checkpw(password.encode("utf-8"), self._password.encode("utf-8"))
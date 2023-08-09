from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (create_engine, desc,
    Index, Column, DateTime, Integer, String)

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    pass
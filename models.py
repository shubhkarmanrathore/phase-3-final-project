from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from passlib.hash import bcrypt_sha256
from sqlalchemy.orm import relationship
import datetime

Base = declarative_base()

# Define the User class to represent user data.
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    username = Column(String(25), unique=True)
    password = Column("password", String, nullable=False)

    security_questions = relationship("SecurityQuestion", backref="user", cascade="all, delete-orphan")
    passwords = relationship("Password", backref="user", cascade="all, delete-orphan")

    def set_password(self, password):
        self.password = bcrypt_sha256.hash(password)

    def check_password(self, password):
        return bcrypt_sha256.verify(password, self.password)

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username})>"

# Define the SecurityQuestion class to store user security questions and answers.
class SecurityQuestion(Base):
    __tablename__ = "security_questions"

    id = Column(Integer, primary_key=True)
    question = Column(String, nullable=False)
    answer = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    def __repr__(self):
        return f"<SecurityQuestion(id={self.id}, question={self.question})>"

# Define the Password class to store user passwords and associated information.
class Password(Base):
    __tablename__ = "passwords"

    id = Column(Integer, primary_key=True)
    website = Column(String, nullable=False)
    username = Column(String, nullable=False)
    password = Column(String, nullable=False)
    notes = Column(String)
    date_added = Column(DateTime, default=datetime.datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    def __repr__(self):
        return f"<Password(id={self.id}, website={self.website}, username={self.username})>"

from models import User
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

def seed_user_data():
    print("Seeding user data...")

    engine = create_engine("sqlite:///user.db")
    Session = sessionmaker(bind=engine)
    session = Session()

    session.query(User).delete()

    user = [
        {
            "first_name": "John",
            "last_name": "Doe",
            "username": "johndoe",
            "password": "12345" 
        }
    ]
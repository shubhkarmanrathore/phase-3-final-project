from models import User
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

print ("Seeding...")

engine = create_engine("sqlite:///user.db")

Session = sessionmaker(bind=engine)
session = Session()

session.query(User).delete()

user = [{
    "first_name": "John",
    "last_name": "Doe",
    "username": "johndoe",
    "password": "12345" 
}]

for user_data in user:
    new_user = User(**user_data)
    session.add(new_user)

session.commit()

print("Seeding done!")
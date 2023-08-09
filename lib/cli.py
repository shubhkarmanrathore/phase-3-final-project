from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from user import User, Base
import bcrypt

# Create the SQLAlchemy engine and session
engine = create_engine("sqlite:///user.db", echo=True)
Session = sessionmaker(bind=engine)
session = Session()

# Function to sign up a new user
def signup():
    first_name = input("Enter your first name: ")
    last_name = input("Enter your last name: ")
    username = input("Enter a username: ")
    existing_user = session.query(User).filter_by(username=username).first()
    
    if existing_user:
        print("Username already exists. Please choose a different username.")
        return

    password = input("Enter a password: ")
    new_user = User(first_name=first_name, last_name=last_name, username=username)
    new_user.set_password(password)

    session.add(new_user)
    session.commit()
    print("User registered successfully!")

# Function to log in an existing user
def login():
    username = input("Enter your username: ")
    password = input("Enter your password: ")
    user = session.query(User).filter_by(username=username).first()

    if not user or not user.check_password(password):
        print("Invalid username or password.")
        return

    print(f"Welcome, {user.first_name}!")

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)  # Create tables if they don't exist
    while True:
        print("1. Signup\n2. Login\n3. Exit")
        choice = input("Enter your choice: ")
        
        if choice == "1":
            signup()
        elif choice == "2":
            login()
        elif choice == "3":
            break
        else:
            print("Invalid choice. Please select a valid option.")

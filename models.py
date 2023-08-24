from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from passlib.hash import bcrypt_sha256
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import relationship
import random
import datetime

Base = declarative_base()

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

class SecurityQuestion(Base):
    __tablename__ = "security_questions"

    id = Column(Integer, primary_key=True)
    question = Column(String, nullable=False)
    answer = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    def __repr__(self):
        return f"<SecurityQuestion(id={self.id}, question={self.question})>"

class Password(Base):
    __tablename__ = "passwords"

    id = Column(Integer, primary_key=True)
    website = Column(String, nullable=False)
    username = Column(String, nullable=False)
    password = Column(String, nullable=False)
    notes = Column(String)
    date_added = Column(DateTime, default=func.now())
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    def __repr__(self):
        return f"<Password(id={self.id}, website={self.website}, username={self.username})>"

class UserApp:
    def __init__(self):
        self.engine = create_engine("sqlite:///user.db")
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()
        self.logged_in_user = None

    def signup(self):
        first_name = input("Enter your first name: ")
        last_name = input("Enter your last name: ")
        username = input("Enter a username: ")
        existing_user = self.session.query(User).filter_by(username=username).first()

        if existing_user:
            print("Username already exists. Please choose a different username.")
            return

        password = input("Enter a password: ")
        new_user = User(first_name=first_name, last_name=last_name, username=username)
        new_user.set_password(password)

        self.session.add(new_user)
        self.session.commit()

        # Set security questions
        for _ in range(3):
            question = input(f"Set security question {_ + 1}: ")
            answer = input(f"Answer for security question {_ + 1}: ")
            new_security_question = SecurityQuestion(question=question, answer=answer, user_id=new_user.id)
            self.session.add(new_security_question)
        
        self.session.commit()
        print("User registered successfully!")

    def login(self):
        username = input("Enter your username: ")
        password = input("Enter your password: ")
        user = self.session.query(User).filter_by(username=username).first()

        if not user or not user.check_password(password):
            print("Invalid username or password.")
            return None

        print(f"Welcome, {user.first_name}!")
        return user

    def account_settings(self):
        if not self.logged_in_user:
            print("You need to log in first.")
            return

        print("Account Settings:")
        print("1. Edit User Account\n2. Delete User Account\n3. Back to Main Menu")
        choice = input("Enter your choice: ")

        if choice == "1":
            self.edit_user_account()
        elif choice == "2":
            self.delete_user_account()

    def edit_user_account(self):
        if not self.logged_in_user:
            print("You need to log in first.")
            return

        new_first_name = input("Enter new first name: ")
        new_last_name = input("Enter new last name: ")
        new_username = input("Enter new username: ")
        new_password = input("Enter new password: ")

        self.logged_in_user.first_name = new_first_name
        self.logged_in_user.last_name = new_last_name
        self.logged_in_user.username = new_username
        self.logged_in_user.set_password(new_password)

        self.session.commit()
        print("User account updated successfully!")

    def delete_user_account(self):
        if not self.logged_in_user:
            print("You need to log in first.")
            return

        confirmation = input("Are you sure you want to delete your account? (yes/no): ").lower()
        if confirmation == "yes":
            self.session.delete(self.logged_in_user)
            self.session.commit()
            self.logged_in_user = None
            print("User account deleted successfully!")
        else:
            print("Account deletion cancelled.")

    def your_passwords(self):
        if not self.logged_in_user:
            print("You need to log in first.")
            return

        for _ in range(3):
            question = random.choice(self.logged_in_user.security_questions)
            user_answer = input(f"Answer the following security question: {question.question}\n")

            if user_answer == question.answer:
                break
            else:
                print("Security question answer is incorrect.")
        else:
            print("Failed to answer security questions. Access denied.")
            return

        print("Your Passwords:")
        print("1. Add Password\n2. Get Passwords\n3. Edit Password\n4. Delete Password\n5. Back to Main Menu")
        choice = input("Enter your choice: ")

        if choice == "1":
            self.add_password()
        elif choice == "2":
            self.get_password()
        elif choice == "3":
            self.edit_password()
        elif choice == "4":
            self.delete_password()
    
    def add_password(self):
        if not self.logged_in_user:
            print("You need to log in first.")
            return

        website = input("Enter the website: ")
        username = input("Enter the username: ")
        password = input("Enter the password: ")
        notes = input("Enter notes (optional): ")

        new_password = Password(website=website, username=username, password=password, notes=notes, user_id=self.logged_in_user.id)
        self.session.add(new_password)
        self.session.commit()
        print("Password added successfully!")

    def get_password(self):
        if not self.logged_in_user:
            print("You need to log in first.")
            return

        passwords = self.session.query(Password).filter_by(user_id=self.logged_in_user.id).all()
        if not passwords:
            print("No passwords stored.")
        else:
            print("Stored passwords:")
            for password in passwords:
                print(f"Website: {password.website}, Username: {password.username}, Password: {password.password}, Date Added: {password.date_added}")
    
    def edit_password(self):
        if not self.logged_in_user:
            print("You need to log in first.")
            return

        passwords = self.session.query(Password).filter_by(user_id=self.logged_in_user.id).all()
        if not passwords:
            print("No passwords stored.")
            return

        print("Stored passwords:")
        for idx, password in enumerate(passwords, start=1):
            print(f"{idx}. Website: {password.website}, Username: {password.username}")

        password_choice = int(input("Select a password to edit (enter number): "))
        selected_password = passwords[password_choice - 1]

        new_website = input("Enter the new website: ")
        new_username = input("Enter the new username: ")
        new_password = input("Enter the new password: ")
        new_notes = input("Enter new notes (optional): ")

        selected_password.website = new_website
        selected_password.username = new_username
        selected_password.password = new_password
        selected_password.notes = new_notes

        self.session.commit()
        print("Password updated successfully!")

    def delete_password(self):
        if not self.logged_in_user:
            print("You need to log in first.")
            return

        passwords = self.session.query(Password).filter_by(user_id=self.logged_in_user.id).all()
        if not passwords:
            print("No passwords stored.")
            return

        print("Stored passwords:")
        for idx, password in enumerate(passwords, start=1):
            print(f"{idx}. Website: {password.website}, Username: {password.username}")

        password_choice = int(input("Select a password to delete (enter number): "))
        selected_password = passwords[password_choice - 1]

        self.session.delete(selected_password)
        self.session.commit()
        print("Password deleted successfully!")


    def run_app(self):
        Base.metadata.create_all(bind=self.engine)  # Create user tables if they don't exist
        while True:
            if not self.logged_in_user:
                print("1. Signup\n2. Login\n3. Exit")
                choice = input("Enter your choice: ")
                
                if choice == "1":
                    self.signup()
                elif choice == "2":
                    self.logged_in_user = self.login()
                elif choice == "3":
                    break
                else:
                    print("Invalid choice. Please select a valid option.")
            else:
                print("1. Account Settings\n2. Your Passwords\n3. Logout")
                choice = input("Enter your choice: ")
                
                if choice == "1":
                    self.account_settings()
                elif choice == "2":
                    self.your_passwords()
                elif choice == "3":
                    self.logged_in_user = None
                else:
                    print("Invalid choice. Please select a valid option.")

if __name__ == "__main__":
    app = UserApp()
    app.run_app()

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, User, SecurityQuestion, Password
import random
from simple_term_menu import TerminalMenu

class UserApp:
    def __init__(self):
        # Initialize the UserApp class, set up database connection and session.
        self.engine = create_engine("sqlite:///user.db")
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()
        self.logged_in_user = None

    def signup(self):
        # Allow users to sign up with info, security questions, and encrypted password.
        user_data = {
            "first_name": input("First name: "),
            "last_name": input("Last name: "),
            "username": input("Username: "),
        }
        existing_user = self.session.query(User).filter_by(username=user_data["username"]).first()

        if existing_user:
            print("Username already taken. Please choose a different username.")
            return

        user_data["password"] = input("Password: ")
        new_user = User(first_name=user_data["first_name"], last_name=user_data["last_name"], username=user_data["username"])
        new_user.set_password(user_data["password"])

        self.session.add(new_user)
        self.session.commit()

        for idx in range(3):
            security_question = input(f"Set security question {idx + 1}: ")
            answer = input(f"Answer for security question {idx + 1}: ")
            new_security_question = SecurityQuestion(question=security_question, answer=answer, user_id=new_user.id)
            self.session.add(new_security_question)
        
        self.session.commit()
        print("User registration successful!\n")

    def login(self):
        # Allow users to log in by verifying username and password.
        username = input("Username: ")
        password = input("Password: ")
        user = self.session.query(User).filter_by(username=username).first()

        if not user or not user.check_password(password):
            print("Invalid username or password.")
            return None

        print(f"Welcome, {user.first_name}!\n")
        return user

    def account_settings(self):
        # Manage user account settings: edit and delete accounts.
        if not self.logged_in_user:
            print("You must be logged in.")
            return

        choices = ["Edit User Account", "Delete User Account", "Back to Main Menu"]
        menu = TerminalMenu(choices, title="Account Settings")
        choice_idx = menu.show()

        if choice_idx == 0:
            self.edit_user_account()
        elif choice_idx == 1:
            self.delete_user_account()

    def edit_user_account(self):
        # Let logged-in users edit account details.
        if not self.logged_in_user:
            print("You must be logged in.")
            return

        new_first_name = input("New first name: ")
        new_last_name = input("New last name: ")
        new_username = input("New username: ")
        new_password = input("New password: ")

        self.logged_in_user.first_name = new_first_name
        self.logged_in_user.last_name = new_last_name
        self.logged_in_user.username = new_username
        self.logged_in_user.set_password(new_password)

        self.session.commit()
        print("User account updated successfully!")

    def delete_user_account(self):
        # Let logged-in users delete their account after confirmation.
        if not self.logged_in_user:
            print("You must be logged in.")
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
        # Access stored passwords after answering security questions.
        if not self.logged_in_user:
            print("You must be logged in.")
            return

        for _ in range(3):
            question = random.choice(self.logged_in_user.security_questions)
            user_answer = input(f"Answer the following security question: {question.question}\n")

            if user_answer.lower() == question.answer.lower():
                break
            else:
                print("Security question answer is incorrect.")
        else:
            print("Failed to answer security questions. Access denied.")
            return

        choices = ["Add Password", "Get Passwords", "Edit Password", "Delete Password", "Back to Main Menu"]
        menu = TerminalMenu(choices, title="Your Passwords")
        choice_idx = menu.show()

        if choice_idx == 0:
            self.add_password()
        elif choice_idx == 1:
            self.get_password()
        elif choice_idx == 2:
            self.edit_password()
        elif choice_idx == 3:
            self.delete_password()
    
    def add_password(self):
        # Let logged-in users add a new password entry.
        if not self.logged_in_user:
            print("You must be logged in.")
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
        # View stored passwords with proper formatting.
        if not self.logged_in_user:
            print("You must be logged in.")
            return

        passwords = self.session.query(Password).filter_by(user_id=self.logged_in_user.id).all()
        if not passwords:
            print("No passwords stored.")
        else:
            print("\nStored passwords:\n")
            for idx, password in enumerate(passwords, start=1):
                print(f"Password {idx}:")
                print(f"Website: {password.website}")
                print(f"Username: {password.username}")
                print(f"Password: {password.password}")
                print(f"Date Added: {password.date_added}")
                print(f"Notes: {password.notes}" if password.notes else "")
                print("-" * 30)
    
    def edit_password(self):
        # Edit a stored password.
        if not self.logged_in_user:
            print("You must be logged in.")
            return

        passwords = self.session.query(Password).filter_by(user_id=self.logged_in_user.id).all()
        if not passwords:
            print("No passwords stored.")
            return

        password_choices = [f"Website: {password.website}, Username: {password.username}" for password in passwords]
        password_choices.append("Go Back")

        password_menu = TerminalMenu(password_choices, title="Select a password to edit:")
        password_choice_idx = password_menu.show()

        if password_choice_idx == len(passwords):
            return

        selected_password = passwords[password_choice_idx]

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
        # Delete a stored password.
        if not self.logged_in_user:
            print("You must be logged in.")
            return

        passwords = self.session.query(Password).filter_by(user_id=self.logged_in_user.id).all()
        if not passwords:
            print("No passwords stored.")
            return

        password_choices = [f"Website: {password.website}, Username: {password.username}" for password in passwords]
        password_choices.append("Go Back")

        password_menu = TerminalMenu(password_choices, title="Select a password to delete:")
        password_choice_idx = password_menu.show()

        if password_choice_idx == len(passwords):
            return

        selected_password = passwords[password_choice_idx]

        self.session.delete(selected_password)
        self.session.commit()
        print("Password deleted successfully!")

    def main(self):
        # Main application loop for user interactions.
        Base.metadata.create_all(bind=self.engine)
        while True:
            if not self.logged_in_user:
                choices = ["Signup", "Login", "Exit"]
                menu = TerminalMenu(choices, title='''
 ____                _____                 
 / __ \              |  __ \                
| |  | | _ __    ___ | |__) |__ _  ___  ___ 
| |  | || '_ \  / _ \|  ___// _` |/ __|/ __|
| |__| || | | ||  __/| |   | (_| |\__ \\__ \\
 \____/ |_| |_| \___||_|    \__,_||___/|___/
                                            
Welcome to OnePass - Your Password Manager
''')
                choice_idx = menu.show()

                if choice_idx == 0:
                    self.signup()
                elif choice_idx == 1:
                    self.logged_in_user = self.login()
                elif choice_idx == 2:
                    break
                else:
                    print("Invalid choice. Please select a valid option.")
            else:
                choices = ["Account Settings", "Your Passwords", "Logout"]
                menu = TerminalMenu(choices, title='Main Menu')
                choice_idx = menu.show()

                if choice_idx == 0:
                    self.account_settings()
                elif choice_idx == 1:
                    self.your_passwords()
                elif choice_idx == 2:
                    self.logged_in_user = None
                else:
                    print("Invalid choice. Please select a valid option.")

if __name__ == "__main__":
    app = UserApp()
    app.main()
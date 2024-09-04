#!/usr/bin/env python3

"""
console that's testing the user model
"""
import cmd
import os
from dotenv import load_dotenv
from models.engine.storage import Storage
from models.user import User
from sqlalchemy import select

load_dotenv()


class USERCommand(cmd.Cmd):
    """
    class definition containing all relevant commands
    """
    prompt = "(USER) "

    def __init__(self, storage: Storage) -> None:
        """
        method definition to initialize storage
        """
        super().__init__()
        self.storage = storage

    def do_create(self, args: str) -> None:
        """
        method definition to create a new user
        """
        try:
            args = args.split()
            print(f"Arguments received: {args}")

            if len(args) < 3:
                print("Usage: create username email password [firstname] [lastname] [age] [phone_number] [user_type]")
                return

            username = args[0]
            email = args[1]
            password = args[2]

            print(f"Username: {username}, Email: {email}, Password: {password}")

            user = User(username=username, email=email, hashed_password="")
            user.set_password(password)

            kwargs = {
                    "firstname": args[3] if len(args) > 3 else None,
                    "lastname": args[4] if len(args) > 4 else None,
                    "age": int(args[5]) if len(args) > 5 else None,
                    "phone_number": args[6] if len(args) > 6 else None,
                    "user_type": args[7] if len(args) > 7 else "user",
                    }

            user = User(username=username, email=email, hashed_password=password, **kwargs)
            self.storage.insert(User, user.to_dict(include_sensitive=True))
            print(f"User {username} created successfully")
        except Exception as e:
            print(f"Error creating user: {e}") # change error statement after testing


    def do_show(self, email: str) -> None:
        """
        method definition to show user details
        """
        query = select(User).where(User.email == email)
        user = self.storage.fetch_one(query)

        if user is None:
            print("User not found")
        else:
            print(user.to_dict(include_sensitive=False))

    def do_update(self, args: str) -> None:
        """
        method definiton to update a user's details
        """
        try:
            args = args.split()
            if len(args) < 2:
                print("Usage: update email key=value [key=value .e.g: key is field to update..]")
                return

            email = args[0]
            updates = dict(arg.split('=') for arg in args[1:])
            self.storage.update(User, updates, {'email': email})
            print(f"User with email {email} updated successfully.")
        except Exception as e:
            print(f"Error updating user: {e}")

    def do_delete(self, username: str) -> None:
        """
        method definition to delete a user
        delete 'username'
        """
        try:
            rows_deleted:int = self.storage.delete('users', {'username': username})
            if rows_deleted:
                print(f"User {username} deleted successfully.")
            else:
                print(f"User {username} not found.")
        except Exception as e:
            print(f"Error deleting user: {e}")

    def do_exit(self, _: str) -> bool:
        """
        method definition to exit the console
        """
        print("Exiting the console.")
        return True


if __name__ == "__main__":
    load_dotenv()

    host = os.getenv('TEST_HOST')
    username = os.getenv('TEST_USER')
    database = os.getenv('TEST_DB_NAME')
    password = os.getenv('TEST_USER_PASSWORD')

    storage = Storage(host=host, username=username, database=database, password=password)
    storage.connect()
    USERCommand(storage).cmdloop()
    storage.disconnect()

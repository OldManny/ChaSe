import logging
import bcrypt
import mysql.connector
from server.database.connection import get_db_connection


def register_user(username, password):
    """
    Registers a new user in the database with a hashed password.

    Args:
        username (str): The username for the new user.
        password (str): The password for the new user.

    Returns:
        bool: True if registration was successful, False if the username already exists.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Check if a case-insensitive match exists for the username
        cursor.execute(
            "SELECT username FROM users WHERE LOWER(username) = %s", (username.lower(),)
        )
        existing_user = cursor.fetchone()

        if existing_user:
            return False  # Username already exists in the system

        # Hash the password and insert the new user with the original case
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (%s, %s)",
            (username, hashed_password),
        )
        conn.commit()
        return True
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return False
    finally:
        cursor.close()
        conn.close()


def login_user(username, password):
    """
    Authenticates a user by checking their credentials.

    Args:
        username (str): The username of the user trying to log in.
        password (str): The password of the user trying to log in.

    Returns:
        str | bool: The original case-preserved username if login is successful, False otherwise.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Perform case-insensitive lookup using LOWER(username)
        cursor.execute(
            "SELECT username, password, is_logged_in FROM users WHERE LOWER(username) = %s",
            (username.lower(),),
        )
        user = cursor.fetchone()

        if user:
            stored_username = user[0]  # This is the original case-preserved username
            hashed_password = user[1]
            is_logged_in = user[2]

            # Check if the password matches and the user is not already logged in
            if (
                bcrypt.checkpw(
                    password.encode("utf-8"), hashed_password.encode("utf-8")
                )
                and not is_logged_in
            ):
                # Mark the user as logged in
                cursor.execute(
                    "UPDATE users SET is_logged_in = TRUE WHERE LOWER(username) = %s",
                    (username.lower(),),
                )
                conn.commit()
                return stored_username  # Return the original case-preserved username
        return False
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return False
    finally:
        cursor.close()
        conn.close()


def logout_user(username):
    """
    Logs out a user by updating their login status in the database.

    Args:
        username (str): The username of the user to log out.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE users SET is_logged_in = FALSE WHERE username = %s", (username,)
        )
        conn.commit()
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        cursor.close()
        conn.close()


def get_all_users():
    """
    Retrieves a list of all registered usernames from the database.

    Returns:
        list: A list of usernames.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT username FROM users")
        users = cursor.fetchall()
        return [user[0] for user in users]  # Extract usernames from the fetched results
    except mysql.connector.Error as err:
        logging.error(f"Error: {err}")
        return []
    finally:
        cursor.close()
        conn.close()

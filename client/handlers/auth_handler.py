import logging
from server.database.user import register_user, login_user

class AuthHandler:
    def __init__(self, login_dialog):
        """
        Initializes the AuthHandler with the provided login dialog.

        Args:
            login_dialog: The dialog interface for user login and registration.
        """
        self.login_dialog = login_dialog

    def handle_login(self):
        """
        Handles the login process by retrieving the username and password,
        authenticating the user, and updating the dialog interface accordingly.
        """
        username = self.login_dialog.login_username.text()
        password = self.login_dialog.login_password.text()

        logging.info(f"Login attempt made.")

        # login_user now returns the case-preserved username
        original_username = login_user(username, password)
        
        if original_username:
            # Store the original case-preserved username on successful login
            self.login_dialog.username = original_username
            logging.info(f"Login successful for user: {original_username}.")
            self.login_dialog.accept()
        else:
            self.login_dialog.login_message_label.setText("Invalid credentials,\nor user already logged in.")
            self.login_dialog.login_message_label.setStyleSheet("color: red")
            self.login_dialog.login_username.setText('')
            self.login_dialog.login_password.setText('')
            logging.warning(f"Login failed for user: {original_username}.")

    def handle_register(self):
        """
        Handles user registration by validating the input and attempting to register the new user.
        Displays messages based on the success or failure of the registration attempt.
        """
        username = self.login_dialog.register_username.text()
        password = self.login_dialog.register_password.text()
        confirm_password = self.login_dialog.confirm_password.text()

        # Log registration attempt
        logging.info("Registration attempt made: %s", username)

        # Check if username or password fields are empty
        if not username:
            self.login_dialog.register_message_label.setText("Username cannot be empty.")
            self.login_dialog.register_message_label.setStyleSheet("color: red")
            logging.warning("Registration failed: Username cannot be empty.")
            return
        if not password:
            self.login_dialog.register_message_label.setText("Password cannot be empty.")
            self.login_dialog.register_message_label.setStyleSheet("color: red")
            logging.warning("Registration failed: Password cannot be empty.")
            return

        if password != confirm_password:
            self.login_dialog.register_message_label.setText("Passwords do not match.")
            self.login_dialog.register_message_label.setStyleSheet("color: red")
            self.login_dialog.register_password.setText('')
            self.login_dialog.confirm_password.setText('')
            logging.warning("Registration failed: passwords do not match.")
        else:
            if register_user(username, password):
                logging.info("Registration successful.")
                self.login_dialog.register_message_label.setText("Successful registration.")
                self.login_dialog.register_message_label.setStyleSheet("color: green")
                self.login_dialog.switch_to_login()
                self.login_dialog.login_username.setText(username)
            else:
                logging.warning("Registration failed: username might be taken.")
                self.login_dialog.register_message_label.setText("Username might be taken.")
                self.login_dialog.register_message_label.setStyleSheet("color: red")
                self.login_dialog.register_username.setText('')
                self.login_dialog.register_password.setText('')
                self.login_dialog.confirm_password.setText('')

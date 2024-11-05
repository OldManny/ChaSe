import os
import sys
import random
import logging
import threading
from dotenv import load_dotenv
from PyQt5.QtWidgets import QApplication, QDialog
from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5.QtMultimedia import QSound
from logging.handlers import RotatingFileHandler
from client.ui.chat_client_ui import ChatClientUI
from client.ui.login_dialog import LoginDialog
from server.database.user import logout_user
from client.ui.chat_management import set_target_client
from client.network.connection import ClientConnection
from client.handlers.message_broadcast import MessageHandler

# Load environment variables from .env file
load_dotenv()

# Server configuration from environment variables
HOST = os.getenv("HOST")
PORT = int(os.getenv("PORT"))

# Create logs folder if it doesn't exist
if not os.path.exists("logs"):
    os.makedirs("logs")

# Configure logging with rotation to avoid oversized logs
log_handler = RotatingFileHandler("logs/client.log", maxBytes=5000000, backupCount=5)
logging.basicConfig(
    handlers=[log_handler],
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


class ChatClient(QObject):
    # Define custom signals for communication between components
    new_message_signal = pyqtSignal(str, str, str)
    display_message_signal = pyqtSignal(str, str, str)
    connection_status_signal = pyqtSignal(bool)

    def __init__(self, host, port, ui, client_name):
        """
        Initializes the ChatClient with server details and UI.

        Args:
            host (str): The server host address.
            port (int): The server port number.
            ui: The UI instance for the chat client.
            client_name (str): The name of the client.
        """
        super().__init__()
        self.ui = ui
        self.client_name = client_name
        self.connection = ClientConnection(host, port, client_name)
        self.message_handler = MessageHandler(
            ui, client_name, self
        )  # Pass self to MessageHandler

        # Connect signals to slots for message handling
        self.new_message_signal.connect(self.ui.display_message)
        self.new_message_signal.connect(
            self.play_notification_sound
        )  # Connect the signal to the method
        self.display_message_signal.connect(self.ui.display_message)

        self.connect_to_server()

    def connect_to_server(self):
        """Attempts to connect to the server and starts the message receiving thread."""
        if self.connection.connect_to_server():
            self.connection_status_signal.emit(True)  # Emit connection status signal
            threading.Thread(
                target=self.receive_messages, daemon=True
            ).start()  # Start a thread to receive messages
        else:
            self.display_message_signal.emit(
                f"Failed to connect after {self.connection.max_reconnect_attempts} attempts",
                "general",
                "left",
            )
            self.connection_status_signal.emit(False)  # Emit connection status signal

    def receive_messages(self):
        """Receives messages from the server and processes them."""
        for message in self.connection.receive_messages():
            self.message_handler.process_message(message)

    def send_message(self, message):
        """Sends a message to the server.

        Args:
            message (str): The message to be sent.
        """
        self.connection.send_message(message)

    def set_target_client(self, target_client):
        """Sets the target client for messaging.

        Args:
            target_client (str): The target client to send messages to.
        """
        set_target_client(self, target_client)

    def play_notification_sound(self, message, message_type, alignment):
        """Plays a notification sound for new messages.

        Args:
            message (str): The received message.
            message_type (str): The type of the message.
            alignment (str): The alignment of the message (left or right).
        """
        # Play sound only for received messages, not history
        if alignment == "left" and message_type != "history":
            QSound.play(os.path.join(os.getcwd(), "notification.wav"))

    def close_connection(self):
        """Closes the connection to the server and logs out the user."""
        self.connection.close_connection()  # Close the client connection
        logout_user(self.client_name)  # Log out the user
        QApplication.instance().quit()  # Quit the application


def main():
    """Main function to start the chat client application."""
    app = QApplication(sys.argv)

    login_dialog = LoginDialog()
    if login_dialog.exec_() == QDialog.Accepted:
        client_name = (
            login_dialog.get_name()
        )  # Get the client name from the login dialog
        if not client_name:
            client_name = f"User{random.randint(1000, 9999)}"  # Assign a random name if none provided
    else:
        sys.exit(0)  # Exit if login is cancelled

    ui = ChatClientUI(client_name)  # Create the main UI

    client = ChatClient(HOST, PORT, ui, client_name)  # Initialize the ChatClient
    ui.send_message_signal.connect(
        client.send_message
    )  # Connect UI signal to send message
    ui.client_selected_signal.connect(
        client.set_target_client
    )  # Connect UI signal to set target client

    ui.show()  # Show the UI
    app.aboutToQuit.connect(
        client.close_connection
    )  # Ensure the connection is closed on app quit
    sys.exit(app.exec_())  # Start the application event loop


if __name__ == "__main__":
    main()

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import pyqtSignal
from client.ui.layouts import setup_ui
from client.ui.chat_management import (
    display_message,
    clear_chat_display,
    request_message_history,
    scroll_to_bottom,
    switch_chat,
    highlight_chat_tab,
    handle_send_button,
)
from client.ui.sidebar_management import (
    update_client_list,
    add_client_to_sidebar,
    add_button_to_sidebar,
)


class ChatClientUI(QMainWindow):
    # Define custom signals for communication between components
    display_message_signal = pyqtSignal(str, str, str)
    send_message_signal = pyqtSignal(str)
    close_connection_signal = pyqtSignal()
    update_client_list_signal = pyqtSignal(list)
    client_selected_signal = pyqtSignal(str)
    group_selected_signal = pyqtSignal(str)

    def __init__(self, client_name):
        """
        Initializes the ChatClientUI with the provided client name.

        Args:
            client_name (str): The name of the client.
        """
        super().__init__()
        self.client_name = client_name
        self.current_chat = "public"
        self.last_click_time = 0
        self.last_sender = None  # Track the sender of the last message
        self.private_chats = []  # Track private chats

        setup_ui(self)  # Set up the user interface

    # Delegate the methods to the respective modules
    def handle_send_button(self):
        """Handles sending messages through the connected handler."""
        handle_send_button(self)

    def display_message(self, message, message_type, alignment):
        """Displays messages in the chat UI."""
        display_message(self, message, message_type, alignment)

    def update_client_list(self, client_list):
        """Updates the sidebar with the current list of clients."""
        update_client_list(self, client_list)

    def add_client_to_sidebar(self, client, chat_identifier=None):
        """Adds a client to the sidebar for chat selection."""
        add_client_to_sidebar(self, client, chat_identifier)

    def add_button_to_sidebar(self, button_text, chat_identifier):
        """Adds a button to the sidebar for switching chats."""
        add_button_to_sidebar(self, button_text, chat_identifier)

    def switch_chat(self, chat_identifier, item):
        """Switches the current chat to the specified identifier."""
        switch_chat(self, chat_identifier, item)

    def clear_chat_display(self):
        """Clears the current chat display area."""
        clear_chat_display(self)

    def request_message_history(self, chat_identifier):
        """Requests the message history for the specified chat."""
        request_message_history(self, chat_identifier)

    def closeEvent(self, event):
        """Handles the close event for the application window."""
        self.close_connection_signal.emit()  # Emit signal to close connection
        event.accept()  # Accept the event to close the window

    def scroll_to_bottom(self):
        """Scrolls the chat area to the bottom."""
        scroll_to_bottom(self)

    def highlight_chat_tab(self, chat_identifier):
        """Highlights the selected chat tab in the UI."""
        highlight_chat_tab(self, chat_identifier)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    chat_client = ChatClientUI("Test Client")
    chat_client.show()
    sys.exit(app.exec_())

import unittest
from unittest.mock import patch, MagicMock
from client.client import ChatClient, main
from PyQt5.QtWidgets import QDialog
import sys


class TestChatClient(unittest.TestCase):
    @patch("client.client.ClientConnection")
    @patch("client.client.MessageHandler")
    @patch("client.client.QSound.play")
    @patch("client.client.logout_user")
    @patch("client.client.ChatClientUI")
    def test_chat_client_initialization(
        self,
        mock_ui,
        mock_logout_user,
        mock_qsound,
        mock_message_handler,
        mock_client_connection,
    ):
        """
        Test the initialization of the ChatClient, ensuring the connection to the server is established
        and UI components are interacting correctly.
        """
        mock_connection = mock_client_connection.return_value
        mock_ui_instance = mock_ui.return_value

        # Create the ChatClient
        client = ChatClient("127.0.0.1", 65432, mock_ui_instance, "TestClient")

        # Check if connection is established
        mock_connection.connect_to_server.assert_called_once()

        # Mock additional methods
        with patch.object(
            client, "play_notification_sound"
        ) as mock_play_sound, patch.object(
            client.ui, "display_message"
        ) as mock_display_message:
            # Simulate signal emission by directly calling the connected slots
            client.ui.display_message("Test Message", "general", "left")
            client.play_notification_sound("Test Message", "general", "left")

            # Verify that display_message was called with the correct arguments
            mock_display_message.assert_called_with("Test Message", "general", "left")

            # Verify that play_notification_sound was called with the correct arguments
            mock_play_sound.assert_called_with("Test Message", "general", "left")

    @patch("client.client.ClientConnection")
    @patch("client.client.MessageHandler")
    @patch("client.client.QSound.play")
    def test_chat_client_send_message(
        self, mock_qsound, mock_message_handler, mock_client_connection
    ):
        """
        Test the send_message functionality, ensuring that the message is sent correctly to the server.
        """
        mock_connection = mock_client_connection.return_value

        # Create the ChatClient
        client = ChatClient("127.0.0.1", 65432, MagicMock(), "TestClient")

        # Simulate sending a message
        client.send_message("Hello")

        # Check if the connection's send_message method was called with the correct arguments
        mock_connection.send_message.assert_called_with("Hello")

    @patch("client.client.ClientConnection")
    @patch("client.client.MessageHandler")
    @patch("client.client.QSound.play")
    def test_chat_client_receive_messages(
        self, mock_qsound, mock_message_handler, mock_client_connection
    ):
        """
        Test the receive_messages functionality, ensuring that incoming messages are processed correctly.
        """
        mock_connection = mock_client_connection.return_value
        mock_connection.receive_messages.return_value = ["message1", "message2"]

        mock_handler_instance = mock_message_handler.return_value

        # Create the ChatClient
        client = ChatClient("127.0.0.1", 65432, MagicMock(), "TestClient")

        # Run the receive_messages function
        client.receive_messages()

        # Ensure that the message handler processes the received messages
        mock_handler_instance.process_message.assert_any_call("message1")
        mock_handler_instance.process_message.assert_any_call("message2")

    @patch("client.client.ClientConnection")
    @patch("client.client.QApplication.instance")
    @patch("client.client.logout_user")
    def test_chat_client_close_connection(
        self, mock_logout_user, mock_qapp_instance, mock_client_connection
    ):
        """
        Test the close_connection method, ensuring that the connection is properly closed,
        and the user is logged out.
        """
        mock_connection = mock_client_connection.return_value
        mock_qapp_instance.return_value = MagicMock()  # Mock QApplication instance

        # Create the ChatClient
        client = ChatClient("127.0.0.1", 65432, MagicMock(), "TestClient")

        # Simulate closing the connection
        client.close_connection()

        # Check if the connection's close_connection method was called
        mock_connection.close_connection.assert_called_once()

        # Check if logout_user was called with the correct client name
        mock_logout_user.assert_called_with("TestClient")

        # Ensure QApplication.quit() is called
        mock_qapp_instance.return_value.quit.assert_called_once()

    @patch("client.client.QApplication")
    @patch("client.client.LoginDialog")
    @patch("client.client.ChatClientUI")
    @patch("client.client.ChatClient")
    def test_main_function(
        self, mock_chat_client, mock_chat_ui, mock_login_dialog, mock_qapp
    ):
        """
        Test the main function, ensuring that the chat client is correctly initialized after login.
        """
        mock_app = MagicMock()
        mock_qapp.return_value = mock_app

        mock_dialog = mock_login_dialog.return_value
        mock_dialog.exec_.return_value = QDialog.Accepted
        mock_dialog.get_name.return_value = "TestClient"

        # Call the main function
        with patch.object(sys, "exit"):
            main()

        # Check if ChatClient was initialized correctly
        mock_chat_client.assert_called_with(
            "127.0.0.1", 65432, mock_chat_ui.return_value, "TestClient"
        )

        # Check if the application quit process is correctly set up
        mock_app.aboutToQuit.connect.assert_called_once_with(
            mock_chat_client.return_value.close_connection
        )


if __name__ == "__main__":
    unittest.main()

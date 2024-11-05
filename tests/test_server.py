import unittest
from unittest.mock import patch, MagicMock
import ssl
import signal
from server.server import start_server, signal_handler
from server.network.connection import handle_new_connection


class TestServer(unittest.TestCase):
    @patch("server.server.ssl.create_default_context")
    @patch("server.server.socket.socket")
    @patch("server.server.signal.signal")
    @patch("sys.exit")  # Patch sys.exit to prevent the test from stopping
    @patch("threading.Thread")  # Patch threading.Thread to mock threading behavior
    def test_start_server(
        self, mock_thread, mock_exit, mock_signal, mock_socket, mock_ssl_context
    ):
        """
        Test the start_server function to ensure SSL context, socket, and threading
        are set up correctly and that connections are handled as expected.
        """
        # Mock SSL context and socket behavior
        mock_context = MagicMock()
        mock_ssl_context.return_value = mock_context
        mock_socket_instance = MagicMock()
        mock_socket.return_value = mock_socket_instance

        # Mock socket to simulate accepting a connection
        mock_conn = MagicMock()
        mock_addr = ("127.0.0.1", 12345)
        mock_socket_instance.accept.return_value = (mock_conn, mock_addr)

        # Simulate server accepting a connection, then stopping
        mock_socket_instance.accept.side_effect = [
            ((mock_conn, mock_addr)),
            KeyboardInterrupt,
        ]

        # Call handle_new_connection directly within the threading patch to simplify test flow
        with patch(
            "threading.Thread.start",
            side_effect=lambda: handle_new_connection(
                mock_conn, mock_addr, mock_context
            ),
        ):
            start_server()

        # Check SSL context creation and certificate loading
        mock_ssl_context.assert_called_once_with(ssl.Purpose.CLIENT_AUTH)
        mock_context.load_cert_chain.assert_called_once_with(
            certfile="cert.pem", keyfile="key.pem"
        )

        # Verify socket setup: binding and listening on the correct port
        mock_socket_instance.bind.assert_called_once_with(("127.0.0.1", 65432))
        mock_socket_instance.listen.assert_called_once()

    @patch("server.server.server_socket")
    @patch("server.server.clients", new_callable=dict)
    @patch("sys.exit")  # Patch sys.exit to prevent test from stopping
    def test_signal_handler(self, mock_exit, mock_clients, mock_server_socket):
        """
        Test the signal_handler to ensure graceful server shutdown,
        closing the server socket and client connections.
        """
        # Mock a client connection and the server socket
        mock_client = MagicMock()
        mock_clients[mock_client] = None

        # Call the signal handler with a SIGINT signal
        signal_handler(signal.SIGINT, None)

        # Verify that the server socket and client connections are closed
        mock_server_socket.close.assert_called_once()
        mock_client.close.assert_called_once()
        mock_exit.assert_called_once_with(0)


if __name__ == "__main__":
    unittest.main()

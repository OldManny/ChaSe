import os
import time
import socket
import ssl
import threading
import logging

class ClientConnection:
    def __init__(self, host, port, client_name):
        """
        Initializes the ClientConnection object with the given host, port, and client name.

        Args:
            host (str): The server host address.
            port (int): The server port.
            client_name (str): The name of the client.
        """
        self.host = host
        self.port = port
        self.client_name = client_name
        self.context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        cert_file = os.path.join('certificates', 'cert.pem')
        self.context.load_verify_locations(cert_file)  # Load SSL certificate for verification
        self.socket = None
        self.stop_event = threading.Event()
        self.connected = False
        self.reconnect_attempt = 0
        self.max_reconnect_attempts = 5

    def connect_to_server(self):
        """
        Attempts to connect to the server with SSL encryption.

        Returns:
            bool: True if the connection was successful, False otherwise.
        """
        while self.reconnect_attempt < self.max_reconnect_attempts:
            try:
                # Create an SSL socket and connect to the server
                self.socket = self.context.wrap_socket(socket.socket(socket.AF_INET), server_hostname=self.host)
                self.socket.connect((self.host, self.port))
                logging.info(f"SSL connection established to server {self.host}:{self.port}.")
                self.socket.sendall(self.client_name.encode())  # Send the client name to the server
                self.connected = True
                self.reconnect_attempt = 0
                return True
            except Exception as e:
                logging.warning(f"Connection attempt {self.reconnect_attempt + 1} failed: {str(e)}")
                self.reconnect_attempt += 1
                time.sleep(5)  # Wait 5 seconds before trying to reconnect
        return False

    def send_message(self, message):
        """
        Sends a message to the server.

        Args:
            message (str): The message to send.
        """
        if not self.connected:
            logging.error("Not connected to server. Message not sent.")
            return

        try:
            self.socket.sendall(message.encode())  # Send the encoded message to the server
        except Exception as e:
            logging.error(f"Failed to send message: {e}")
            self.handle_connection_loss()  # Handle connection loss if sending fails

    def receive_messages(self):
        """
        Generator that receives messages from the server.

        Yields:
            str: The received message decoded.
        """
        while not self.stop_event.is_set():
            try:
                data = self.socket.recv(1024).strip()  # Receive data from the socket
                if not data:
                    raise ConnectionResetError("Server closed the connection")
                yield data.decode()  # Decode and yield the received message
            except (ConnectionResetError, OSError):
                self.handle_connection_loss()
                break

    def handle_connection_loss(self):
        """Handles loss of connection to the server."""
        self.connected = False
        self.stop_event.set()  # Signal to stop receiving messages
        
    def close_connection(self):
        """Closes the connection to the server gracefully."""
        logging.info("Closing connection...")
        self.stop_event.set()
        self.connected = False
        if self.socket:
            try:
                self.socket.shutdown(socket.SHUT_RDWR)  # Shut down the socket
            except OSError as e:
                logging.info(f"Socket already shut down: {e}")
            try:
                self.socket.close()  # Close the socket
            except OSError as e:
                logging.info(f"Error closing socket: {e}")
            finally:
                self.socket = None
        logging.info(f"User {self.client_name} logged out.")

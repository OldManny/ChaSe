import os
import socket
import ssl
import threading
import signal
import sys
import logging
from dotenv import load_dotenv
from logging.handlers import RotatingFileHandler
from server.network.connection import handle_new_connection, clients

# Load environment variables from .env file
load_dotenv()

# Create the logs directory if it doesn't exist
if not os.path.exists("logs"):
    os.makedirs("logs")

# Configure logging to log to server.log with rotation (5 backups, each max size 5 MB)
log_handler = RotatingFileHandler("logs/server.log", maxBytes=5000000, backupCount=5)
logging.basicConfig(
    handlers=[log_handler],
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Server configuration from environment variables
HOST = os.getenv("HOST")
PORT = int(os.getenv("PORT"))

server_socket = None


def signal_handler(sig, frame):
    """
    Handles shutdown signals (e.g., Ctrl+C) and cleans up resources before exiting.

    Args:
        sig: The received signal.
        frame: The current stack frame.
    """
    logging.info("Shutting down server.")
    if server_socket:
        server_socket.close()
    # Close all client connections
    for client in clients.keys():
        client.close()
    sys.exit(0)


def start_server():
    """
    Starts the server, sets up SSL, and begins accepting connections.
    """
    global server_socket
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)

    cert_file = os.path.join("certificates", "cert.pem")
    key_file = os.path.join("certificates", "key.pem")

    # Load SSL certificate and private key
    context.load_cert_chain(certfile=cert_file, keyfile=key_file)
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    logging.info(f"Server started, listening on {HOST}:{PORT}")

    # Register signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)

    while True:
        try:
            # Accept new client connections
            conn, addr = server_socket.accept()
            threading.Thread(
                target=handle_new_connection, args=(conn, addr, context)
            ).start()
        except KeyboardInterrupt:
            break
        except Exception as e:
            logging.error(f"Error accepting connection: {e}")

    # Handle server shutdown
    signal_handler(None, None)


if __name__ == "__main__":
    start_server()

import socket
import ssl
import threading
import logging
from queue import Queue
from server.database.user import get_all_users
from server.shared import clients, send_message_history, enqueue_message
from server.network.message_broadcast import (
    message_sender,
    broadcast_client_list,
    process_message,
)


def handle_new_connection(conn, addr, context):
    """
    Handles a new incoming connection and establishes SSL encryption.

    Args:
        conn: The raw client connection.
        addr: The address of the connecting client.
        context: The SSL context to wrap the connection.
    """
    try:
        conn.settimeout(5)  # Set a timeout for the SSL handshake
        ssl_conn = context.wrap_socket(conn, server_side=True)
        logging.info(f"SSL connection established with {addr}.")  # SSL confirmation log
        ssl_conn.settimeout(None)  # Remove the timeout after a successful handshake
        client_thread = threading.Thread(
            target=handle_client, args=(ssl_conn, addr)
        )  # Pass the SSL connection to the client handler
        client_thread.start()  # Start the client thread
    except ssl.SSLError as e:
        if "HTTP_REQUEST" in str(e):
            logging.info(f"Client at {addr} disconnected during SSL handshake")
        else:
            logging.error(f"SSL Error during handshake with {addr}: {e}")
    except socket.timeout:
        logging.info(f"Timeout during SSL handshake with {addr}")
    except Exception as e:
        logging.error(f"Unexpected error during connection setup with {addr}: {e}")
    finally:
        if "ssl_conn" not in locals():
            try:
                conn.close()
            except Exception:
                pass


def handle_client(conn, addr):
    """
    Handles communication for an individual client, including message processing.

    Args:
        conn: The SSL-wrapped connection for the client.
        addr: The address of the client.
    """
    message_queue = Queue()
    name = None
    try:
        name = conn.recv(1024).decode().strip()
        clients[conn] = {"name": name, "queue": message_queue}
        broadcast_client_list()
        logging.info(f"{name} connected by {addr}")

        # Send the list of all users except the current one
        all_users = get_all_users()
        all_users_list = ",".join([user for user in all_users if user != name])
        enqueue_message(conn, f"ALL_USERS:{all_users_list}")

        # Start a thread for sending messages to the client
        sender_thread = threading.Thread(target=message_sender, args=(conn,))
        sender_thread.start()

        # Send public and private message history to the client
        send_message_history(conn, name, "public")
        send_message_history(conn, name, name)

        while True:
            data = conn.recv(1024)
            if not data:
                break
            message = data.decode().strip()
            logging.debug(f"Received message from {name}")
            if message == "disconnect":
                break
            process_message(conn, name, message)

    except (ConnectionResetError, ssl.SSLError) as e:
        logging.error(f"Error handling client {name}: {e}")
    except Exception as e:
        logging.error(f"Unexpected error handling client {name}: {e}")
    finally:
        cleanup_client_connection(conn, name, addr)


def cleanup_client_connection(conn, name, addr):
    """
    Cleans up client data and closes the connection upon client disconnection.

    Args:
        conn: The connection object of the client.
        name (str): The username of the disconnected client.
        addr: The address of the client.
    """
    if conn in clients:
        del clients[conn]
    if name:
        logging.info(f"{name} disconnected by {addr}")
        broadcast_client_list()

    try:
        # Attempt to gracefully shut down the connection if still open
        conn.getpeername()
        try:
            conn.shutdown(socket.SHUT_RDWR)
        except OSError as e:
            logging.debug(f"Could not shut down connection for {name}: {e}")
    except OSError:
        logging.debug(f"Connection for {name} is closing...")
    finally:
        try:
            conn.close()
        except Exception as e:
            logging.debug(f"Error closing connection for {name}: {e}")

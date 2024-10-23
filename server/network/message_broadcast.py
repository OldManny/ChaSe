import logging
import ssl
from queue import Empty
from server.database.connection import get_db_connection
from server.shared import clients, send_message_history, enqueue_message, store_message_in_db

def broadcast_message(message):
    """
    Broadcasts a public message to all connected clients.

    Args:
        message (str): The message to be sent to all clients.
    """
    for client in clients.keys():
        enqueue_message(client, f"PUBLIC:{message}")

def send_private_message(target_name, message, sender_name):
    """
    Sends a private message from one client to another.

    Args:
        target_name (str): The username of the recipient.
        message (str): The content of the private message.
        sender_name (str): The username of the sender.
    """
    target_client = None
    sender_client = None
    # Find the target and sender clients in the clients dictionary
    for client, info in clients.items():
        if info['name'] == target_name:
            target_client = client
        if info['name'] == sender_name:
            sender_client = client
        if target_client and sender_client:
            break

    if target_client:
        enqueue_message(target_client, f"PRIVATE:{sender_name}:{message}")
    if sender_client:
        enqueue_message(sender_client, f"PRIVATE:{sender_name}:{message}")

def send_group_message(group_name, sender_name, message):
    """
    Sends a message to all members of a specified group.

    Args:
        group_name (str): The name of the group.
        sender_name (str): The username of the sender.
        message (str): The message to be sent to the group.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Fetch group members from the database
        cursor.execute("SELECT users.username FROM users "
                       "JOIN group_memberships ON users.id = group_memberships.user_id "
                       "JOIN groups ON group_memberships.group_id = groups.id "
                       "WHERE groups.name = %s", (group_name,))
        members = cursor.fetchall()
        for member in members:
            # Send the message to all group members who are currently connected
            for client, info in clients.items():
                if info['name'] == member[0]:
                    enqueue_message(client, f"GROUP:{group_name}:{sender_name}:{message}")
    except Exception as e:
        logging.error(f"Error retrieving group members: {e}")
    finally:
        cursor.close()
        conn.close()

def broadcast_client_list():
    """
    Sends the list of currently connected clients to all connected clients.
    """
    # Normalize the client list by converting usernames to lowercase, but preserve the original case
    unique_clients = {info['name'].lower(): info['name'] for info in clients.values()}
    client_list = ",".join(unique_clients.values())  # Use original case-sensitive names
    for client in clients.keys():
        enqueue_message(client, f"CLIENT_LIST:{client_list}")

def message_sender(conn):
    """
    Continuously sends queued messages to the specified client.

    Args:
        conn: The connection object representing the client.
    """
    while conn in clients:
        try:
            # Get the next message from the client's message queue
            message = clients[conn]['queue'].get(timeout=1)
            try:
                conn.sendall(message.encode())  # Send the message to the client
            except ssl.SSLError as e:
                logging.error(f"SSL Error sending message: {e}")
                break
            except Exception as e:
                logging.error(f"Error sending message: {e}")
                break
        except Empty:
            pass

def process_message(conn, name, message):
    """
    Processes a received message and routes it based on its type (public, private, or group).

    Args:
        conn: The connection object representing the client.
        name (str): The username of the sender.
        message (str): The received message to process.
    """
    if message.startswith("HISTORY:"):
        # Handle message history request
        chat_identifier = message[len("HISTORY:"):]
        send_message_history(conn, name, chat_identifier)

    elif message.startswith("@"):
        # Handle private or public message
        target_name, private_message = message.split(":", 1)
        target_name = target_name[1:]  # Remove '@' symbol
        if target_name.lower() == "public":
            # Broadcast message to all clients
            broadcast_message(f"{name}: {private_message}")
            store_message_in_db(name, None, None, private_message)  # Store public message in the DB
        else:
            # Send private message to the specified user
            send_private_message(target_name, private_message, name)
            store_message_in_db(name, target_name, None, private_message)  # Store private message in the DB

    elif message.startswith("GROUP:"):
        # Handle group message
        group_name, group_message = message.split(":", 1)
        group_name = group_name[len("GROUP:"):]  # Extract group name
        send_group_message(group_name, name, group_message)
        store_message_in_db(name, None, group_name, group_message)  # Store group message in the DB

    else:
        # Broadcast message to all clients (default case)
        broadcast_message(f"{name}: {message}")
        store_message_in_db(name, None, None, message)  # Store public message in the DB

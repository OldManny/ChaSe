import logging
import mysql.connector
from server.database.connection import get_db_connection

# Dictionary to manage connected clients
clients = {}

def enqueue_message(conn, message):
    """
    Adds a message to the message queue of the specified client connection.

    Args:
        conn: The connection object representing the client.
        message (str): The message to be enqueued.
    """
    if conn in clients:
        clients[conn]['queue'].put(message)

def store_message_in_db(sender, recipient, group, message):
    """
    Stores a sent message into the database, associated with either a recipient or a group.

    Args:
        sender (str): The username of the message sender.
        recipient (str or None): The username of the recipient, if applicable (for private messages).
        group (str or None): The name of the group, if applicable (for group messages).
        message (str): The content of the message.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Fetch sender ID based on username
        cursor.execute("SELECT id FROM users WHERE username = %s", (sender,))
        sender_id = cursor.fetchone()[0]
        
        recipient_id = None
        group_id = None

        if recipient:
            # Fetch recipient ID for private message
            cursor.execute("SELECT id FROM users WHERE username = %s", (recipient,))
            recipient_id = cursor.fetchone()[0]
        
        if group:
            # Fetch group ID for group message
            cursor.execute("SELECT id FROM `groups` WHERE name = %s", (group,))
            group_id = cursor.fetchone()[0]

        # Insert message into the database
        cursor.execute("INSERT INTO messages (sender_id, recipient_id, group_id, message) VALUES (%s, %s, %s, %s)",
                       (sender_id, recipient_id, group_id, message))
        conn.commit()
        logging.debug("Stored message in DB.")
    except mysql.connector.Error as err:
        logging.error(f"Error storing message in DB: {err}")
    finally:
        cursor.close()
        conn.close()

def send_message_history(conn, username, chat_identifier):
    """
    Sends the message history to the client for a specific chat (public, group, or private).

    Args:
        conn: The connection object representing the client.
        username (str): The username of the client requesting the message history.
        chat_identifier (str): Identifier for the chat (e.g., 'public', 'group:<groupname>', or private username).
    """
    conn_db = get_db_connection()
    cursor = conn_db.cursor()
    try:
        # Fetch user ID based on the username
        user_id_query = "SELECT id FROM users WHERE username = %s"
        cursor.execute(user_id_query, (username,))
        user_id = cursor.fetchone()[0]

        if chat_identifier == "public" or chat_identifier == "All":
            # Retrieve all public messages
            query = ("SELECT users.username, messages.message "
                     "FROM messages JOIN users ON messages.sender_id = users.id "
                     "WHERE recipient_id IS NULL AND group_id IS NULL "
                     "ORDER BY messages.timestamp ASC")
            cursor.execute(query)
        elif chat_identifier.startswith("group:"):
            # Retrieve messages for a specific group
            group_name = chat_identifier.split(":", 1)[1]
            query = ("SELECT users.username, messages.message "
                     "FROM messages JOIN users ON messages.sender_id = users.id "
                     "JOIN `groups` ON messages.group_id = `groups`.id "
                     "WHERE `groups`.name = %s "
                     "ORDER BY messages.timestamp ASC")
            cursor.execute(query, (group_name,))
        else:
            # Retrieve private message history
            query = ("SELECT users.username, messages.message "
                     "FROM messages JOIN users ON messages.sender_id = users.id "
                     "WHERE (messages.sender_id = %s AND messages.recipient_id = (SELECT id FROM users WHERE username = %s)) "
                     "OR (messages.sender_id = (SELECT id FROM users WHERE username = %s) AND messages.recipient_id = %s) "
                     "ORDER BY messages.timestamp ASC")
            cursor.execute(query, (user_id, chat_identifier, chat_identifier, user_id))

        # Send the retrieved messages to the client
        messages = cursor.fetchall()
        for message in messages:
            sender = message[0]
            text = message[1]
            if sender == username:
                enqueue_message(conn, f"HISTORY:ME:{text}\n")
            else:
                enqueue_message(conn, f"HISTORY:{sender}:{text}\n")
        logging.debug(f"Sent message history for {chat_identifier}")
    except mysql.connector.Error as err:
        logging.error(f"Error retrieving message history: {err}")
    finally:
        cursor.close()
        conn_db.close()

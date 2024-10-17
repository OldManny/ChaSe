from PyQt5.QtWidgets import QListWidgetItem, QLabel, QHBoxLayout, QWidget, QPushButton
from PyQt5.QtCore import pyqtSlot, Qt

@pyqtSlot(list)
def update_client_list(chat_client, client_list):
    """
    Updates the sidebar with the current list of clients.

    Args:
        chat_client: The current chat client instance.
        client_list: A list of current connected clients.
    """
    chat_client.sidebar.clear()
    add_client_to_sidebar(chat_client, "All", "public")
    for client in client_list:
        add_client_to_sidebar(chat_client, client)
    
    # Add private chats that are not in the current client list
    for private_chat in chat_client.private_chats:
        if private_chat not in client_list:
            add_client_to_sidebar(chat_client, private_chat)

def add_client_to_sidebar(chat_client, client, chat_identifier=None):
    """
    Adds a client to the sidebar.

    Args:
        chat_client: The current chat client instance.
        client: The name of the client to add.
        chat_identifier: An optional identifier for the chat.
    """
    item = QListWidgetItem()
    item_widget = QWidget()

    item_layout = QHBoxLayout()
    item_layout.setContentsMargins(10, 10, 10, 10)

    initials_label = QLabel(client[:2].upper())
    initials_label.setFixedSize(40, 40)
    initials_label.setStyleSheet("""
        background-color: grey;
        color: white;
        border-radius: 20px;
        padding: 0px;
        margin: 0px;
    """)
    initials_label.setAlignment(Qt.AlignCenter)

    item_layout.addWidget(initials_label)

    name_label = QLabel(client)
    name_label.setStyleSheet("padding: 0px; margin: 0px; color: white; font-size: 14pt;")
    item_layout.addWidget(name_label)

    item_widget.setLayout(item_layout)
    item.setSizeHint(item_widget.sizeHint())

    chat_client.sidebar.addItem(item)
    chat_client.sidebar.setItemWidget(item, item_widget)
    
    chat_identifier = chat_identifier or client
    item_widget.mousePressEvent = lambda event, c=chat_identifier: chat_client.switch_chat(c, item)

    # Keep track of private chats
    if chat_identifier not in chat_client.private_chats and chat_identifier != "public":
        chat_client.private_chats.append(chat_identifier)

def add_button_to_sidebar(chat_client, button_text, chat_identifier):
    """
    Adds a button to the sidebar for switching chats.

    Args:
        chat_client: The current chat client instance.
        button_text: The text to display on the button.
        chat_identifier: The identifier for the chat associated with the button.
    """
    button = QPushButton(button_text)
    button.clicked.connect(lambda: chat_client.switch_chat(chat_identifier))
    item = QListWidgetItem(chat_client.sidebar)
    chat_client.sidebar.addItem(item)
    chat_client.sidebar.setItemWidget(item, button)

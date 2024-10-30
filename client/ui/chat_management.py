from PyQt5.QtWidgets import QLabel, QWidget, QHBoxLayout, QSizePolicy
from PyQt5.QtGui import QTextDocument
from PyQt5.QtCore import Qt, QTimer
import logging
import time

def display_message(chat_client, message, message_type, alignment):
    """
    Displays a message in the chat interface based on its type and alignment.

    Args:
        chat_client: The current chat client instance.
        message: The message string, formatted as 'sender: content'.
        message_type: Type of message ('public', 'private', or 'history').
        alignment: Alignment for displaying the message ('left' or 'right').
    """

    # Split the message into sender and content
    sender, content = message.split(': ', 1) if ': ' in message else (None, message)

    # Calculate the width of the text based on its content
    text_document = QTextDocument()
    text_document.setPlainText(content)
    text_width = text_document.idealWidth()
    max_width = int(chat_client.width() * 0.5)  # Maximum width set to 50% of window width
    min_width = 20
    final_width = min(max_width, max(min_width, int(text_width + 30)))  # Final width calculation

    # Determine if the message should be displayed in the current chat
    should_display = False
    if message_type == "public" and chat_client.current_chat in ["All", "public"]:
        should_display = True
    elif message_type == "private":
        if chat_client.current_chat == sender or chat_client.current_chat == chat_client.client_name or sender == chat_client.client_name:
            should_display = True
    elif message_type == "history":
        should_display = True

    if not should_display:
        return

    # Logic to manage sender initials and message bubble display
    sender_initials = ""
    display_initials = True
    current_sender = None

    if alignment == "right":
        message_parts = message.split(":", 1)
        if len(message_parts) == 2:
            current_sender = chat_client.client_name
            message = message_parts[1]
    elif alignment == "left":
        message_parts = message.split(":", 1)
        if len(message_parts) == 2:
            current_sender = message_parts[0]
            sender_initials = current_sender[:2].upper()
            message = message_parts[1]

    if chat_client.last_sender == current_sender:
        display_initials = False
    else:
        chat_client.last_sender = current_sender

    # Create the message bubble
    label = QLabel(content)
    label.setWordWrap(True)
    label.setStyleSheet(f"""
        background-color: {'#0084FF' if alignment == 'right' else '#7289DA'};
        color: white;
        padding: 10px 7px;
        border-radius: 18px;
        font-size: 15pt;
    """)

    label.setAlignment(Qt.AlignCenter)  # Align the text inside the bubble to the left
    label.setFixedWidth(final_width if len(content) > 0 else min_width)
    label.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Preferred)

    # Set up the container layout for message bubbles
    container = QWidget()
    container_layout = QHBoxLayout()
    container_layout.setContentsMargins(0, 0, 0, 0)
    container_layout.setAlignment(Qt.AlignRight if alignment == "right" else Qt.AlignLeft)

    spacer = QLabel()
    spacer.setFixedSize(30, 30)

    # Add sender initials for received messages
    if alignment == "left":
        if display_initials:
            initials_label = QLabel(sender_initials)
            initials_label.setFixedSize(30, 30)
            initials_label.setStyleSheet("""
                background-color: grey;
                color: white;
                border-radius: 15px;
                padding: 0px;
                margin: 0px;
            """)
            initials_label.setAlignment(Qt.AlignCenter)
            container_layout.addWidget(initials_label)
        else:
            container_layout.addWidget(spacer)

    container.setLayout(container_layout)
    container_layout.addWidget(label)
    container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

    # Wrapping the message container
    wrapper = QWidget()
    wrapper_layout = QHBoxLayout()
    wrapper_layout.setContentsMargins(0, 0, 0, 0)
    wrapper_layout.setAlignment(Qt.AlignRight if alignment == "right" else Qt.AlignLeft)
    wrapper.setLayout(wrapper_layout)
    wrapper_layout.addWidget(container)
    wrapper.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

    # Add the message bubble to the chat layout
    chat_client.chat_layout.addWidget(wrapper)
    QTimer.singleShot(100, chat_client.scroll_to_bottom)  # Scroll to the bottom after displaying the message


def switch_chat(chat_client, chat_identifier, item):
    """
    Switches the current chat to the specified chat identifier.

    Args:
        chat_client: The current chat client instance.
        chat_identifier: Identifier for the chat to switch to.
        item: The item in the sidebar that represents the chat.
    """
    current_time = time.time()
    if current_time - chat_client.last_click_time < 0.5:
        return  # Prevent double-clicking

    chat_client.last_click_time = current_time
    chat_client.current_chat = chat_identifier
    chat_client.last_sender = None  # Reset last sender on chat switch

    # Update the header based on the chat identifier
    if chat_identifier in ["public", "All"]:
        chat_client.header.setText(f"<b>Public Chat</b>")
        chat_client.current_chat = "public"
    elif chat_identifier.startswith("group:"):
        group_name = chat_identifier.split(":", 1)[1]
        chat_client.header.setText(f"<b>Group: {group_name}</b>")
        chat_client.group_selected_signal.emit(group_name)
    else:
        chat_client.header.setText(f"{chat_identifier}")

    chat_client.client_selected_signal.emit(chat_identifier)  # Signal the selected client
    chat_client.chat_layout.setAlignment(Qt.AlignTop)
    chat_client.clear_chat_display()

    # Update styles for the selected chat in the sidebar
    for index in range(chat_client.sidebar.count()):
        list_item = chat_client.sidebar.item(index)
        widget = chat_client.sidebar.itemWidget(list_item)
        if list_item == item:
            widget.setStyleSheet("""
                background-color: #3e4248;
                border: none;
                border-radius: 15px;
                margin: 2px 0px;
            """)
            list_item.setBackground(Qt.transparent)
        else:
            widget.setStyleSheet("""
                background-color: #2C2F33;
                color: white;
            """)
            list_item.setBackground(Qt.transparent)


def clear_chat_display(chat_client):
    """
    Clears the current chat display.

    Args:
        chat_client: The current chat client instance.
    """
    for i in reversed(range(chat_client.chat_layout.count())):
        widget_to_remove = chat_client.chat_layout.itemAt(i).widget()
        chat_client.chat_layout.removeWidget(widget_to_remove)
        widget_to_remove.setParent(None)  # Remove widget from parent layout


def request_message_history(chat_client, chat_identifier):
    """
    Requests the message history for the specified chat identifier.

    Args:
        chat_client: The current chat client instance.
        chat_identifier: Identifier for the chat whose history is requested.
    """
    chat_client.send_message_signal.emit(f"HISTORY:{chat_identifier}")
    QTimer.singleShot(100, chat_client.scroll_to_bottom)  # Delay scrolling to bottom


def scroll_to_bottom(chat_client):
    """
    Scrolls the chat area to the bottom.

    Args:
        chat_client: The current chat client instance.
    """
    chat_client.chat_area.verticalScrollBar().setValue(chat_client.chat_area.verticalScrollBar().maximum())


def handle_send_button(chat_client):
    """
    Handles the send button action to send messages.

    Args:
        chat_client: The current chat client instance.
    """
    message = chat_client.message_input.text().strip()  # Get and trim the input message

    chat_client.message_input.clear()  # Clear the input field immediately after grabbing the message

    if not message:  # Discard empty messages
        return

    # Send the message based on the current chat type
    if chat_client.current_chat == "public":
        chat_client.send_message_signal.emit(message)
    elif chat_client.current_chat.startswith("group:"):
        group_name = chat_client.current_chat.split(":", 1)[1]
        chat_client.send_message_signal.emit(f"#{group_name}:{message}")
    else:
        chat_client.send_message_signal.emit(f"@{chat_client.current_chat}:{message}")


def highlight_chat_tab(chat_client, chat_identifier):
    """
    Highlights the sidebar tab for the specified chat identifier.

    Args:
        chat_client: The current chat client instance.
        chat_identifier: Identifier for the chat tab to highlight.
    """
    for index in range(chat_client.sidebar.count()):
        list_item = chat_client.sidebar.item(index)
        widget = chat_client.sidebar.itemWidget(list_item)
        if widget:
            if chat_identifier in widget.findChildren(QLabel)[1].text():
                widget.setStyleSheet("""
                    background-color: #40444B;
                    border-radius: 15px;
                    margin: 2px 0px;
                    color: white;
                """)
                list_item.setBackground(Qt.transparent)
                break


def set_target_client(self, target_client):
    """
    Sets the target client for messaging and retrieves message history.

    Args:
        self: The instance of the chat client.
        target_client: The target client for the current chat.
    """
    logging.info(f"Setting target client to: {target_client}")
    self.target_client = target_client
    self.ui.header.setText(f"{self.target_client}")
    self.connection.send_message(f"HISTORY:{target_client}")

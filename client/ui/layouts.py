from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QListWidget, QLabel, QScrollArea, QWidget, QLineEdit
from PyQt5.QtCore import Qt

def setup_ui(chat_client):
    """
    Sets up the user interface for the chat client.

    Args:
        chat_client: The current chat client instance.
    """
    chat_client.setWindowTitle(f"ChaSe - {chat_client.client_name}")
    chat_client.setGeometry(100, 100, 1000, 700)
    chat_client.setStyleSheet("background-color: #2C2F33; color: white;")

    main_layout = QVBoxLayout()
    content_layout = QHBoxLayout()

    # Sidebar for chat clients
    chat_client.sidebar = QListWidget()
    chat_client.sidebar.setFixedSize(250, 500)
    chat_client.sidebar.setStyleSheet("""
        QListWidget {
            background-color: #2C2F33;
            border: none;
            color: white;
            font-size: 14pt;
            font-weight: bold;
        }
        QListWidget::item {
            background-color: #2C2F33;
            border: none;
            border-radius: 15px;
        }
        QListWidget::item:selected {
            background-color: transparent;
            border: none;
            border-radius: 15px;
        }
    """)

    content_layout.addWidget(chat_client.sidebar)

    # Chat area layout
    chat_layout = QVBoxLayout()

    # Header displaying the client's name
    chat_client.header = QLabel(f"{chat_client.client_name}")
    chat_client.header.setAlignment(Qt.AlignLeft)
    chat_client.header.setFixedHeight(50)
    chat_client.header.setStyleSheet("""
        background-color: #2C2F33;
        color: white;
        padding: 10px;
        margin: 0px;
        font-size: 18pt;
        font-weight: bold;
    """)
    chat_layout.addWidget(chat_client.header)

    # Chat display area
    chat_client.chat_area = QScrollArea()
    chat_client.chat_area.setWidgetResizable(True)
    chat_client.chat_area.setStyleSheet("""
        QScrollArea {
            background-color: #2C2F33;
            border: none;
        }
        QScrollBar:vertical {
            background: #2C2F33;
            width: 5px;
            margin: 0px;
            border-radius: 2px;
        }
        QScrollBar::handle:vertical {
            background: #808080;
            min-height: 3px;
            border-radius: 2px;
        }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0px;
            subcontrol-origin: margin;
            subcontrol-position: top;
        }
    """)

    chat_client.chat_container = QWidget()
    chat_client.chat_layout = QVBoxLayout()
    chat_client.chat_container.setLayout(chat_client.chat_layout)
    chat_client.chat_area.setWidget(chat_client.chat_container)

    chat_layout.addWidget(chat_client.chat_area)

    # Message input area layout
    input_layout = QHBoxLayout()
    
    # Message input field
    chat_client.message_input = QLineEdit()
    chat_client.message_input.setFixedHeight(50)
    chat_client.message_input.setPlaceholderText("Type a message")
    chat_client.message_input.returnPressed.connect(chat_client.handle_send_button)  # Send message on Enter
    chat_client.message_input.setStyleSheet("""
        background-color: #40444B;
        color: white;
        padding: 10px;
        margin: 0px;
        border: none;
        border-radius: 10px;
        font-size: 14pt;
    """)
    input_layout.addWidget(chat_client.message_input)

    main_layout.addLayout(content_layout)
    main_layout.addLayout(input_layout)

    central_widget = QWidget()
    central_widget.setLayout(main_layout)
    chat_client.setCentralWidget(central_widget)

    chat_client.update_client_list_signal.connect(chat_client.update_client_list)

    # Adding a default client to the sidebar
    chat_client.add_client_to_sidebar("All", "public")

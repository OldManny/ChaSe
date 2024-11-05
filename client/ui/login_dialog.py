from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLineEdit,
    QPushButton,
    QLabel,
    QWidget,
    QStackedLayout,
)
from PyQt5.QtCore import Qt
from client.handlers.auth_handler import AuthHandler


class LoginDialog(QDialog):
    def __init__(self):
        """
        Initializes the LoginDialog for user authentication (login/register).

        Sets up the layout and initializes the AuthHandler.
        """
        super().__init__()
        self.setWindowTitle("Login")
        self.setGeometry(100, 100, 300, 250)
        self.layout = QVBoxLayout()

        self.stacked_layout = QStackedLayout()
        self.layout.addLayout(self.stacked_layout)

        self.auth_handler = AuthHandler(self)  # Pass the dialog instance to the handler

        self.login_widget = self.create_login_widget()
        self.register_widget = self.create_register_widget()

        self.stacked_layout.addWidget(self.login_widget)
        self.stacked_layout.addWidget(self.register_widget)

        self.setLayout(self.layout)
        self.username = ""  # Store the username here

    def create_login_widget(self):
        """
        Creates the login widget interface.

        Returns:
            QWidget: The widget containing the login fields and buttons.
        """
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)  # Add spacing between elements

        self.login_username = QLineEdit()
        self.login_username.setPlaceholderText("Username")
        layout.addWidget(self.login_username)

        self.login_password = QLineEdit()
        self.login_password.setPlaceholderText("Password")
        self.login_password.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.login_password)

        self.login_button = QPushButton("Login")
        layout.addWidget(self.login_button)
        self.login_button.clicked.connect(self.auth_handler.handle_login)

        self.login_message_label = QLabel("")  # Label for feedback messages
        self.login_message_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.login_message_label)

        self.switch_to_register_label = QLabel("or <a href='#'>Register</a>")
        self.switch_to_register_label.setAlignment(
            Qt.AlignCenter
        )  # Center the label horizontally
        layout.addWidget(self.switch_to_register_label)
        self.switch_to_register_label.linkActivated.connect(self.switch_to_register)

        widget.setLayout(layout)
        return widget

    def create_register_widget(self):
        """
        Creates the registration widget interface.

        Returns:
            QWidget: The widget containing the registration fields and buttons.
        """
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(10)  # Add spacing between elements

        self.register_username = QLineEdit()
        self.register_username.setPlaceholderText("Username")
        layout.addWidget(self.register_username)

        self.register_password = QLineEdit()
        self.register_password.setPlaceholderText("Password")
        self.register_password.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.register_password)

        self.confirm_password = QLineEdit()
        self.confirm_password.setPlaceholderText("Confirm Password")
        self.confirm_password.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.confirm_password)

        self.register_button = QPushButton("Register")
        layout.addWidget(self.register_button)
        self.register_button.clicked.connect(self.auth_handler.handle_register)

        self.register_message_label = QLabel("")  # Label for feedback messages
        self.register_message_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.register_message_label)

        self.switch_to_login_label = QLabel("or <a href='#'>Login</a>")
        self.switch_to_login_label.setAlignment(
            Qt.AlignCenter
        )  # Center the label horizontally
        layout.addWidget(self.switch_to_login_label)
        self.switch_to_login_label.linkActivated.connect(self.switch_to_login)

        widget.setLayout(layout)
        return widget

    def switch_to_register(self):
        """
        Switches the dialog view to the registration widget.
        Clears any login messages when switching.
        """
        self.stacked_layout.setCurrentWidget(self.register_widget)
        self.login_message_label.setText("")  # Clear any login messages when switching

    def switch_to_login(self):
        """
        Switches the dialog view to the login widget.
        Clears any registration messages when switching.
        """
        self.stacked_layout.setCurrentWidget(self.login_widget)
        self.register_message_label.setText(
            ""
        )  # Clear any register messages when switching

    def get_name(self):
        """
        Returns the stored username.

        Returns:
            str: The username of the logged-in user.
        """
        return self.username

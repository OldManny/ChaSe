import logging


class MessageHandler:
    def __init__(self, ui, client_name, chat_client):
        """
        Initializes the MessageHandler with the provided UI, client name, and chat client.

        Args:
            ui: The user interface instance for updating UI elements.
            client_name: The name of the client instance.
            chat_client: The chat client instance for handling chat messages.
        """
        self.ui = ui
        self.client_name = client_name
        self.chat_client = chat_client

    def process_message(self, message):
        """
        Processes incoming messages and updates the UI or chat client accordingly.

        Args:
            message (str): The incoming message to be processed.
        """
        logging.info(f"Processing message for {self.client_name}.")

        if message.startswith("CLIENT_LIST:"):
            client_list = message[len("CLIENT_LIST:") :].split(",")
            # Avoid duplicates by normalizing the list to lowercase
            unique_clients = {client.lower(): client for client in client_list}
            client_list = list(unique_clients.values())  # Use the case-preserved values
            client_list.remove(self.client_name)  # Don't include the current client
            self.ui.update_client_list_signal.emit(client_list)
        elif message.startswith("ALL_USERS:"):
            all_users = message[len("ALL_USERS:") :].split(",")
            self.ui.update_client_list_signal.emit(all_users)
        elif message.startswith("PRIVATE:"):
            sender, msg = message[len("PRIVATE:") :].split(":", 1)
            alignment = "left" if sender != self.client_name else "right"
            self.chat_client.new_message_signal.emit(
                f"{sender}: {msg}", "private", alignment
            )
            if (
                sender != self.client_name
            ):  # Only highlight if the message is from someone else
                self.ui.highlight_chat_tab(sender)
        elif message.startswith("GROUP:"):
            group, sender, msg = message[len("GROUP:") :].split(":", 2)
            alignment = "left" if sender != self.client_name else "right"
            self.chat_client.new_message_signal.emit(
                f"{sender} in {group}: {msg}", "group", alignment
            )
            if group != self.ui.current_chat:
                self.ui.highlight_chat_tab(group)
        elif message.startswith("HISTORY:"):
            _, sender, msg = message.split(":", 2)
            alignment = "right" if sender == "ME" else "left"
            self.chat_client.display_message_signal.emit(
                f"{sender}: {msg}", "history", alignment
            )
        elif message.startswith("PUBLIC:"):
            sender, msg = message[len("PUBLIC:") :].split(":", 1)
            alignment = "left" if sender != self.client_name else "right"
            self.chat_client.new_message_signal.emit(
                f"{sender}: {msg}", "public", alignment
            )
            if self.ui.current_chat != "All":
                self.ui.highlight_chat_tab("All")
        else:
            logging.debug(f"Unhandled message: {message}")

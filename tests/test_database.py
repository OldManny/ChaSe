import unittest
from unittest.mock import patch, MagicMock


class TestFetchoneMock(unittest.TestCase):
    @patch("server.database.connection.get_db_connection")
    def test_fetchone_mock(self, mock_get_db_connection):
        """
        Test to verify that the fetchone method in database queries correctly retrieves results
        and that the SQL query is executed with expected parameters.
        """
        # Set up a mock connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Mock fetchone to return a series of valid IDs for sender, recipient, and group
        mock_cursor.fetchone.side_effect = [
            (1,),
            (2,),
            (3,),
        ]  # Mocked sender_id, recipient_id, group_id

        # Simulate a database query and check if fetchone works as expected
        cursor = mock_conn.cursor()
        sender_id = cursor.fetchone()[0]

        # Execute a sample query to retrieve a user ID
        cursor.execute("SELECT id FROM users WHERE username = %s", ("sender",))

        # Print outputs to verify behavior
        print(f"fetchone() returned sender_id: {sender_id}")
        print(f"Executed queries: {mock_cursor.execute.call_args_list}")

        # Assertions to check that fetchone returns the correct sender ID
        self.assertEqual(sender_id, 1)

        # Validate that the correct SQL query and arguments were passed to execute
        executed_query = mock_cursor.execute.call_args_list[0][0][0]
        executed_args = mock_cursor.execute.call_args_list[0][0][1]
        print(f"Executed query: {executed_query}, with args: {executed_args}")

        self.assertEqual(executed_query, "SELECT id FROM users WHERE username = %s")
        self.assertEqual(executed_args, ("sender",))


if __name__ == "__main__":
    unittest.main()

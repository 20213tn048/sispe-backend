import uuid
from unittest.mock import patch, MagicMock
import unittest
import json

from sqlalchemy.exc import SQLAlchemyError
from get_categories.get_categories import lambda_handler


class MyTestCase(unittest.TestCase):

    @patch("get_categories.get_categories.db_connection.connect")
    def test_lambda_handler_success(self, mock_connect):
        # Mock de la conexión y el resultado de la consulta
        mock_conn = MagicMock()
        mock_result = [
            {'category_id': b'\x12\x34', 'name': 'Test Category'}
        ]
        mock_connect.return_value = mock_conn
        mock_conn.execute.return_value = mock_result

        event = {}
        context = {}

        response = lambda_handler(event, context)

        self.assertEqual(response['statusCode'], 200)
        expected_body = [{'category_id': '1234', 'name': 'Test Category'}]
        self.assertEqual(json.loads(response['body']), expected_body)

    @patch("get_categories.get_categories.db_connection.connect")
    def test_lambda_handler_no_categories(self, mock_connect):
        # Mock de la conexión y el resultado vacío de la consulta
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.execute.return_value = []

        event = {}
        context = {}

        response = lambda_handler(event, context)

        self.assertEqual(response['statusCode'], 404)
        self.assertEqual(json.loads(response['body']), 'No categories found')

    @patch("get_categories.get_categories.db_connection.connect")
    def test_lambda_handler_sqlalchemy_error(self, mock_connect):
        # Mock de la conexión que lanza una excepción SQLAlchemyError
        mock_connect.side_effect = SQLAlchemyError("Database error")

        event = {}
        context = {}

        response = lambda_handler(event, context)

        self.assertEqual(response['statusCode'], 500)
        self.assertEqual(json.loads(response['body']), 'Internal server error. Could not fetch categories.')

    @patch("get_categories.get_categories.db_connection.connect")
    def test_lambda_handler_general_exception(self, mock_connect):
        # Mock de la conexión que lanza una excepción general
        mock_connect.side_effect = Exception("Unexpected error")

        event = {}
        context = {}

        response = lambda_handler(event, context)

        self.assertEqual(response['statusCode'], 500)
        self.assertEqual(json.loads(response['body']), 'Internal server error.')



if __name__ == '__main__':
    unittest.main()

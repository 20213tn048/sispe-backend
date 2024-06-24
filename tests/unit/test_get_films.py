import uuid
from decimal import Decimal
from unittest.mock import patch, MagicMock
import unittest
import json

from create_favorite.sqlalchemy.exc import SQLAlchemyError
from get_films.get_films import lambda_handler

class MyTestCase(unittest.TestCase):

    @patch("get_films.get_films.db_connection.connect")
    def test_lambda_handler_success(self, mock_connect):
        # Mock de la conexión y el resultado de la consulta
        mock_conn = MagicMock()
        mock_result = [
            {
                'film_id': b'\x12\x34',
                'title': 'Test Film',
                'description': 'A test film description',
                'length': Decimal('120.00'),
                'status': 'Activo',
                'fk_category': b'\x12\x34',
                'front_page': 'http://example.com/front_page.jpg',
                'file': 'http://example.com/file.mp4'
            }
        ]
        mock_connect.return_value = mock_conn
        mock_conn.execute.return_value = mock_result

        event = {}
        context = {}

        response = lambda_handler(event, context)

        self.assertEqual(response['statusCode'], 200)
        expected_body = [
            {
                'film_id': '1234',
                'title': 'Test Film',
                'description': 'A test film description',
                'length': 120.00,
                'status': 'Activo',
                'fk_category': '1234',
                'front_page': 'http://example.com/front_page.jpg',
                'file': 'http://example.com/file.mp4'
            }
        ]
        self.assertEqual(json.loads(response['body']), expected_body)

    @patch("get_films.get_films.db_connection.connect")
    def test_lambda_handler_no_films(self, mock_connect):
        # Mock de la conexión y el resultado vacío de la consulta
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.execute.return_value = []

        event = {}
        context = {}

        response = lambda_handler(event, context)

        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(json.loads(response['body']), 'No films found')

    @patch("get_films.get_films.db_connection.connect")
    def test_lambda_handler_sqlalchemy_error(self, mock_connect):
        # Mock de la conexión que lanza una excepción SQLAlchemyError
        mock_connect.side_effect = SQLAlchemyError("Database error")

        event = {}
        context = {}

        response = lambda_handler(event, context)

        self.assertEqual(response['statusCode'], 500)
        self.assertEqual(json.loads(response['body']), 'Exception: Database error')

    @patch("get_films.get_films.db_connection.connect")
    def test_lambda_handler_general_exception(self, mock_connect):
        # Mock de la conexión que lanza una excepción general
        mock_connect.side_effect = Exception("Unexpected error")

        event = {}
        context = {}

        response = lambda_handler(event, context)

        self.assertEqual(response['statusCode'], 500)
        self.assertIn('Exception: Unexpected error', json.loads(response['body']))

if __name__ == '__main__':
    unittest.main()

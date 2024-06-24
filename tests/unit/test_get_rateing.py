import uuid
from decimal import Decimal
from unittest.mock import patch, MagicMock
import unittest
import json

from create_favorite.sqlalchemy.exc import SQLAlchemyError
from get_rateing.get_rateing import lambda_handler

class MyTestCase(unittest.TestCase):


    @patch("get_rateing.get_rateing.db_connection.connect")
    def test_lambda_handler_success(self, mock_connect):
        # Mock de la conexión y el resultado de la consulta
        mock_conn = MagicMock()
        mock_result = [
            {
                'rateing_id': b'\x12\x34',
                'grade': Decimal('4.5'),
                'comment': 'Great movie!',
                'fk_user': b'\x56\x78',
                'fk_film': b'\x9A\xBC'
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
                'rateing_id': '1234',
                'grade': 4.5,
                'comment': 'Great movie!',
                'fk_user': '5678',
                'fk_film': '9abc'
            }
        ]
        self.assertEqual(json.loads(response['body']), expected_body)

    @patch("get_rateing.get_rateing.db_connection.connect")
    def test_lambda_handler_no_rateings(self, mock_connect):
        # Mock de la conexión y el resultado vacío de la consulta
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.execute.return_value = []

        event = {}
        context = {}

        response = lambda_handler(event, context)

        self.assertEqual(response['statusCode'], 404)
        self.assertEqual(json.loads(response['body']), 'No rateings found')

    @patch("get_rateing.get_rateing.db_connection.connect")
    def test_lambda_handler_sqlalchemy_error(self, mock_connect):
        # Mock de la conexión que lanza una excepción SQLAlchemyError
        mock_connect.side_effect = SQLAlchemyError("Database error")

        event = {}
        context = {}

        response = lambda_handler(event, context)

        self.assertEqual(response['statusCode'], 500)
        self.assertEqual(json.loads(response['body']), 'Internal server error')

    @patch("get_rateing.get_rateing.db_connection.connect")
    def test_lambda_handler_general_exception(self, mock_connect):
        # Mock de la conexión que lanza una excepción general
        mock_connect.side_effect = Exception("Unexpected error")

        event = {}
        context = {}

        response = lambda_handler(event, context)

        self.assertEqual(response['statusCode'], 500)
        self.assertEqual(json.loads(response['body']), 'Internal server error')


if __name__ == '__main__':
    unittest.main()

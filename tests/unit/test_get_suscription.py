import unittest
import uuid
from datetime import datetime
from decimal import Decimal
from unittest.mock import patch, MagicMock
import unittest
import json

from sqlalchemy.exc import SQLAlchemyError
from get_subscription.get_subscription import lambda_handler


class MyTestCase(unittest.TestCase):

    @patch("get_subscription.get_subscription.db_connection.connect")
    def test_lambda_handler_success(self, mock_connect):
        # Mock de la conexión y el resultado de la consulta
        mock_conn = MagicMock()
        mock_result = {
            'subscription_id': uuid.UUID('12345678123456781234567812345678').bytes,
            'start_date': datetime(2022, 1, 1, 12, 0, 0),
            'end_date': datetime(2023, 1, 1, 12, 0, 0)
        }
        mock_connect.return_value = mock_conn
        mock_conn.execute.return_value.fetchone.return_value = mock_result

        event = {
            'pathParameters': {
                'subscription_id': '12345678-1234-5678-1234-567812345678'
            }
        }
        context = {}

        response = lambda_handler(event, context)

        self.assertEqual(response['statusCode'], 200)
        expected_body = {
            'subscription_id': '12345678-1234-5678-1234-567812345678',
            'start_date': '2022-01-01T12:00:00',
            'end_date': '2023-01-01T12:00:00'
        }
        self.assertEqual(json.loads(response['body']), expected_body)

    @patch("get_subscription.get_subscription.db_connection.connect")
    def test_lambda_handler_subscription_not_found(self, mock_connect):
        # Mock de la conexión y el resultado vacío de la consulta
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.execute.return_value.fetchone.return_value = None

        event = {
            'pathParameters': {
                'subscription_id': '12345678-1234-5678-1234-567812345678'
            }
        }
        context = {}

        response = lambda_handler(event, context)

        self.assertEqual(response['statusCode'], 404)
        self.assertEqual(json.loads(response['body']), {'message': 'Subscription not found'})

    @patch("get_subscription.get_subscription.db_connection.connect")
    def test_lambda_handler_sqlalchemy_error(self, mock_connect):
        # Mock de la conexión que lanza una excepción SQLAlchemyError
        mock_connect.side_effect = SQLAlchemyError("Database error")

        event = {
            'pathParameters': {
                'subscription_id': '12345678-1234-5678-1234-567812345678'
            }
        }
        context = {}

        response = lambda_handler(event, context)

        self.assertEqual(response['statusCode'], 500)
        self.assertEqual(json.loads(response['body']), {'message': 'Internal Server Error'})

    @patch("get_subscription.get_subscription.db_connection.connect")
    def test_lambda_handler_general_exception(self, mock_connect):
        # Mock de la conexión que lanza una excepción general
        mock_connect.side_effect = Exception("Unexpected error")

        event = {
            'pathParameters': {
                'subscription_id': '12345678-1234-5678-1234-567812345678'
            }
        }
        context = {}

        response = lambda_handler(event, context)

        self.assertEqual(response['statusCode'], 500)
        self.assertEqual(json.loads(response['body']), {'message': 'Internal Server Error'})


if __name__ == '__main__':
    unittest.main()

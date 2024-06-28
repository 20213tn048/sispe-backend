import unittest
from unittest.mock import patch, MagicMock
import json
from create_subscription.create_subscription import lambda_handler, create_subscription, create_session
from sqlalchemy.exc import SQLAlchemyError


class TestCreateSubscription(unittest.TestCase):

    @patch('create_subscription.create_subscription.create_checkout_session')
    @patch('create_subscription.create_subscription.db_connection')
    def test_create_subscription_success(self, mock_db_connection, mock_create_checkout_session):
        mock_create_checkout_session.return_value = MagicMock(id='session-id')
        mock_conn = mock_db_connection.connect.return_value
        mock_conn.execute.return_value.rowcount = 1

        event = {
            'body': json.dumps({
                'start_date': '2024-07-01T00:00:00',
                'end_date': '2024-08-01T00:00:00'
            })
        }

        response = lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 201)
        self.assertIn('subscription_id', json.loads(response['body']))

    @patch('create_subscription.create_subscription.create_checkout_session')
    @patch('create_subscription.create_subscription.db_connection')
    def test_create_subscription_no_body(self, mock_db_connection, mock_create_checkout_session):
        event = {
            'body': None
        }

        response = lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 400)
        self.assertIn('Error', json.loads(response['body']))

    @patch('create_subscription.create_subscription.create_checkout_session')
    @patch('create_subscription.create_subscription.db_connection')
    def test_create_subscription_invalid_dates(self, mock_db_connection, mock_create_checkout_session):
        event = {
            'body': json.dumps({
                'start_date': '2024-07-01T00:00:00',
                'end_date': '2024-07-01T00:00:00'
            })
        }

        response = lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 500)
        self.assertIn('Error', json.loads(response['body']))

    @patch('create_subscription.create_subscription.create_checkout_session')
    @patch('create_subscription.create_subscription.db_connection')
    def test_create_subscription_start_date_in_past(self, mock_db_connection, mock_create_checkout_session):
        event = {
            'body': json.dumps({
                'start_date': '2023-01-01T00:00:00',
                'end_date': '2024-08-01T00:00:00'
            })
        }

        response = lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 500)
        self.assertIn('Error', json.loads(response['body']))

    @patch('create_subscription.create_subscription.create_checkout_session')
    @patch('create_subscription.create_subscription.db_connection')
    def test_create_subscription_end_date_before_start_date(self, mock_db_connection, mock_create_checkout_session):
        event = {
            'body': json.dumps({
                'start_date': '2024-08-01T00:00:00',
                'end_date': '2024-07-01T00:00:00'
            })
        }

        response = lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 500)
        self.assertIn('Error', json.loads(response['body']))

    @patch('create_subscription.create_subscription.create_checkout_session')
    @patch('create_subscription.create_subscription.db_connection')
    def test_create_subscription_sqlalchemy_error(self, mock_db_connection, mock_create_checkout_session):
        mock_create_checkout_session.return_value = MagicMock(id='session-id')
        mock_db_connection.connect.side_effect = SQLAlchemyError("Database error")

        event = {
            'body': json.dumps({
                'start_date': '2024-07-01T00:00:00',
                'end_date': '2024-08-01T00:00:00'
            })
        }

        response = lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 500)
        self.assertIn('Error Interno del Servidor', json.loads(response['body']))

if __name__ == '__main__':
    unittest.main()

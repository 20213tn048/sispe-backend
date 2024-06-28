import unittest
from unittest.mock import patch, MagicMock
import json

from sqlalchemy.exc import SQLAlchemyError

from update_user.update_user import lambda_handler


class TestUpdateUser(unittest.TestCase):

    @patch('update_user.update_user.db_connection.connect')
    def test_update_user_success(self, mock_connect):
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.execute.return_value.fetchone.return_value = True

        event = {
            'body': json.dumps({
                'user_id': '4e6f726d616c697a65646e616d65',
                'name': 'updated name',
                'lastname': 'updated lastname',
                'email': 'updated@email.com',
                'password': 'updatedPassword',
                'fk_rol': '4e6f726d616c697a65646e616d65',
                'fk_subscription': '4e6f726d616c697a65646e616d65'
            })
        }

        result = lambda_handler(event, None)
        self.assertEqual(result['statusCode'], 200)
        self.assertEqual(json.loads(result['body']), 'Usuario actualizado')

    @patch('update_user.update_user.db_connection.connect')
    def test_update_user_notFound(self, mock_connect):
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.execute.return_value.fetchone.return_value = False
        event = {
            'body': json.dumps({
                'user_id': '4e6f726d616c697a65646e616d65',
                'name': 'updated name',
                'lastname': 'updated lastname',
                'email': 'updated@email.com',
                'password': 'updatedPassword',
                'fk_rol': '4e6f726d616c697a65646e616d65',
                'fk_subscription': '4e6f726d616c697a65646e616d65'
            })
        }

        result = lambda_handler(event, None)
        self.assertEqual(result['statusCode'], 404)
        self.assertEqual(json.loads(result['body']), 'User not found')

    @patch('update_user.update_user.db_connection.connect')
    def test_update_user_notConecction(self, mock_connect):
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.execute.side_effect = SQLAlchemyError('Error updating user')
        event = {
            'body': json.dumps({
                'user_id': '4e6f726d616c697a65646e616d65',
                'name': 'updated name',
                'lastname': 'updated lastname',
                'email': 'updated@email.com',
                'password': 'updatedPassword',
                'fk_rol': '4e6f726d616c697a65646e616d65',
                'fk_subscription': '4e6f726d616c697a65646e616d65'
            })
        }

        result = lambda_handler(event, None)
        self.assertEqual(result['statusCode'], 500)
        self.assertEqual(json.loads(result['body']), 'Error updating user')

    @patch('update_user.update_user.db_connection.connect')
    def test_update_user_invalidFormat(self, mock_connect):
        event = {'body': '{"user":"angel_Camargo"'}
        response = lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 400)
        self.asserEqual(response['body'], json.dumps("Invalid JSON format"))
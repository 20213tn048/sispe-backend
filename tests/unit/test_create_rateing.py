import unittest
from unittest.mock import patch, MagicMock
import json
import uuid
from sqlalchemy.exc import SQLAlchemyError
from create_rateing.create_rateing import lambda_handler

mock_body = {
    'grade': 4.5,
    'comment': 'Buena película',
    'fk_user': uuid.uuid4().hex,
    'fk_film': uuid.uuid4().hex
}


class TestCreateRateing(unittest.TestCase):

    @patch('create_rateing.create_rateing.db_connection.connect')
    def test_no_body(self, mock_connect):
        event = {'body': None}
        response = lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(response['body'], json.dumps('Invalid JSON format'))

    @patch('create_rateing.create_rateing.db_connection.connect')
    def test_invalid_json(self, mock_connect):
        event = {'body': '{"grade":"4.5'}
        response = lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(response['body'], json.dumps('Invalid JSON format'))

    @patch('create_rateing.create_rateing.db_connection.connect')
    def test_sqlalchemy_error(self, mock_connect):
        event = {'body': json.dumps(mock_body)}
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.execute.side_effect = SQLAlchemyError("Error en la base de datos")  #Forzar error de base de datos

        response = lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 500)
        self.assertEqual(response['body'], json.dumps('Error creating rateing'))

    @patch('create_rateing.create_rateing.db_connection.connect')
    def test_unexpected_error(self, mock_connect):
        event = {'body': json.dumps(mock_body)}
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.execute.side_effect = Exception("Ocurrió un error")  # Forzar la exeption

        response = lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 500)
        self.assertEqual(response['body'], json.dumps('Internal server error'))

    @patch('create_rateing.create_rateing.db_connection.connect')
    def test_successfully_creation(self, mock_connect):
        event = {'body': json.dumps(mock_body)}
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn

        response = lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(response['body'], json.dumps('Rateing creado'))

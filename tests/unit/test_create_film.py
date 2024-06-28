import unittest
from unittest.mock import patch, MagicMock
import json
import uuid
from sqlalchemy.exc import SQLAlchemyError
from create_film.create_film import lambda_handler

mock_body = {
    'title': 'Hércules',
    'description': 'Descripción chida',
    'length': '2.00',
    'status': 'Activo',
    'fk_category': uuid.uuid4().hex,
    'front_page': 'image.mp3',
    'file': 'película.mp4'
}

mock_missing_body = {
    'title': 'Hércules',
    'description': 'Descripción chida',
    'length': '2.00',
    'status': 'Activo',
    'fk_category': uuid.uuid4().hex,
    'front_page': 'image'
    # Falta file
}


class TestCreateFilm(unittest.TestCase):

    @patch('create_film.create_film.db_connection.connect')
    def test_no_body(self, mock_connect):
        event = {'body': None}
        response = lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(response['body'], json.dumps('Invalid JSON format'))

    @patch('create_film.create_film.db_connection.connect')
    def test_invalid_json(self, mock_connect):
        event = {'body': '{"title": "Test Movie"'}  # JSON incompleto
        response = lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(response['body'], json.dumps('Invalid JSON format'))

    @patch('create_film.create_film.db_connection.connect')
    def test_missing_required_key(self, mock_connect):
        data = mock_missing_body
        event = {'body': json.dumps(data)}
        response = lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 400)
        self.assertIn('Missing required key', response['body'])

    @patch('create_film.create_film.db_connection.connect')
    def test_film_not_found(self, mock_connect):
        data = mock_body
        event = {'body': json.dumps(data)}
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.execute.return_value.fetchone.return_value = None  # No existe el ID

        response = lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(response['body'], json.dumps('Category ID does not exist'))

    @patch("create_subscription.create_subscription.db_connection.connect")
    def test_sqlalchemy_error(self, mock_connect):
        event = {"body": json.dumps(mock_body)}
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.execute.side_effect = SQLAlchemyError("Can't connect to MySQL")

        response = lambda_handler(event, None)
        self.assertEqual(response["statusCode"], 500)
        self.assertEqual(response["body"], json.dumps("Error creating film"))

    @patch('create_film.create_film.db_connection.connect')
    def test_successfully_creation(self, mock_connect):
        data = mock_body
        event = {'body': json.dumps(data)}
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.execute.return_value.fetchone.return_value = MagicMock()  # Simulación de que todo esta bien

        response = lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(response['body'], json.dumps('Film created'))


if __name__ == '__main__':
    unittest.main()

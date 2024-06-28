import unittest
from unittest.mock import patch, MagicMock
from update_film.update_film import lambda_handler
import json
from sqlalchemy.exc import SQLAlchemyError

mock_body = {
    'film_id': '1234567890abcdef1234567890abcdef',
    'title': 'Test Film',
    'description': 'Test Description',
    'length': 120,
    'status': 'Activo',
    'fk_category': 'abcdef1234567890abcdef1234567890',
    'front_page': 'test.jpg',
    'file': 'test.mp4'
}


class TestUpdateFilm(unittest.TestCase):

    @patch("update_film.update_film.db_connection.connect")
    def test_missing_required_fields(self, mock_connection):
        event = {
            'body': json.dumps({
                'film_id': '1234567890abcdef1234567890abcdef',
                'title': 'Test Film'
                # Hacen falta campos requeridos
            })
        }

        response = lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 400)
        self.assertIn('Missing required fields', response['body'])

    @patch('update_film.update_film.db_connection.connect')
    def test_film_not_found(self, mock_connection):
        mock_conn = MagicMock()
        mock_connection.return_value = mock_conn
        mock_conn.execute.return_value.fetchone.return_value = None

        event = {'body': json.dumps(mock_body)}

        result = lambda_handler(event, None)
        self.assertEqual(result['statusCode'], 404)
        self.assertIn('Film not found', result['body'])

    @patch('update_film.update_film.db_connection.connect')
    def test_successful_update(self, mock_connection):
        mock_conn = MagicMock()
        mock_connection.return_value = mock_conn
        mock_conn.execute.return_value.fetchone.return_value = {'film_id': '1234567890abcdef1234567890abcdef'}

        event = {'body': json.dumps(mock_body)}

        response = lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 200)
        self.assertIn('Film updated', response['body'])

    @patch('update_film.update_film.db_connection.connect')
    def test_sqlalchemy_error(self, mock_connection):
        mock_conn = MagicMock()
        mock_connection.return_value = mock_conn
        mock_conn.execute.side_effect = SQLAlchemyError('Error de base de datos')

        event = {'body': json.dumps(mock_body)}

        response = lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 500)
        self.assertIn('Error updating film', response['body'])

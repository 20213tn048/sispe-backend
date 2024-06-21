import unittest
from unittest.mock import patch, MagicMock
import json
import uuid
from sqlalchemy.exc import SQLAlchemyError
from create_favorite.create_favorite import lambda_handler


class TestCreateFavorite(unittest.TestCase):

    @patch('create_favorite.create_favorite.db_connection.connect')
    def test_no_body(self, mock_connect):
        event = {'body': None}  # Envíar la solicitud sin un cuerpo
        response = lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(response['body'], json.dumps('Entrada invalida, cuerpo no encontrado'))

    @patch('create_favorite.create_favorite.db_connection.connect')
    def test_missing_fk_user_or_fk_film(self, mock_connect):
        event = {'body': json.dumps({})}  # Enviar la solicitud con un cuerpo vacío
        response = lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(response['body'], json.dumps('Entrada invalida, usuario o pelicula no encontrados'))

    @patch('create_favorite.create_favorite.db_connection.connect')
    def test_invalid_user_or_film_id(self, mock_connect):
        event = {                           # Cuerpo con datos incorrectos
            'body': json.dumps({
                'fk_user': 'invalid',
                'fk_film': 'invalid'
            })
        }
        response = lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(response['body'], json.dumps('El ID de usuario o pelicula no es válido'))

    @patch('create_favorite.create_favorite.db_connection.connect')
    def test_user_not_found(self, mock_connect):
        event = {
            'body': json.dumps({
                'fk_user': uuid.uuid4().hex,
                'fk_film': uuid.uuid4().hex
            })
        }
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.execute.return_value.fetchone.side_effect = [
            None,      # No se encontró un usaurio
            None,      # No se buscó la película
            None       # No se buscó en favoritos
        ]

        response = lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(response['body'], json.dumps('Usuario no encontrado'))

    @patch('create_favorite.create_favorite.db_connection.connect')
    def test_film_not_found_or_inactive(self, mock_connect):
        event = {
            'body': json.dumps({
                'fk_user': uuid.uuid4().hex,
                'fk_film': uuid.uuid4().hex
            })
        }
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.execute.return_value.fetchone.side_effect = [
            MagicMock(),    # Indica que el usuario existe
            None            # La película no existe o esta inactiva
        ]

        response = lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(response['body'], json.dumps('Película no encontrada o no está activa'))

    @patch('create_favorite.create_favorite.db_connection.connect')
    def test_favorite_already_exists(self, mock_connect):
        event = {
            'body': json.dumps({
                'fk_user': uuid.uuid4().hex,
                'fk_film': uuid.uuid4().hex
            })

        }
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.execute.return_value.fetchone.side_effect = [
            MagicMock(),    # Se encontró un usuario
            MagicMock(),    # Se encontró una película activa
            MagicMock()     # La película ya esta en favoritos
        ]

        response = lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(response['body'], json.dumps('Película ya agregada a la lista de favoritos'))

    @patch('create_favorite.create_favorite.db_connection.connect')
    def test_successfull_add_favorite(self, mock_connect):
        event = {
            'body': json.dumps({
                'fk_user': uuid.uuid4().hex,
                'fk_film': uuid.uuid4().hex
            })
        }
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.execute.return_value.fetchone.side_effect = [
            MagicMock(),    # Se encontró un usuario
            MagicMock(),    # Se encontró una película activa
            None            # La película no esta en favoritos
        ]

        response = lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(response['body'], json.dumps('Película agregada a la lista de favoritos'))

    @patch('create_favorite.create_favorite.db_connection.connect')
    def test_sqlalchemy_error(self, mock_connect):
        event = {
            'body': json.dumps({
                'fk_user': uuid.uuid4().hex,
                'fk_film': uuid.uuid4().hex
            })
        }
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.execute.side_effect = SQLAlchemyError("Database error")  # Forzar un eror de la base de datos

        response = lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 500)
        self.assertEqual(response['body'], json.dumps('Error al agregar a favoritos'))

    @patch('create_favorite.create_favorite.db_connection.connect')
    def test_json_decode_error(self, mock_connect):
        event = {'body': '{"fk_user": "JSON inválido'}
        response = lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(response['body'], json.dumps('Formato JSON inválido'))


if __name__ == '__main__':
    unittest.main()

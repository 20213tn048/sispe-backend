import uuid
from unittest.mock import patch, MagicMock
import unittest
import json

from create_favorite.sqlalchemy.exc import SQLAlchemyError
from get_favorites.get_favorites import lambda_handler

mock_event = {
    "pathParameters": {
        "fk_user": "1234567890abcdef1234567890abcdef"
    }
}

class MyTestCase(unittest.TestCase):

    @patch("get_favorites.get_favorites.db_connection.connect")
    def test_succes_no_favorites(self, mock_connect):
        mock_conn = MagicMock()
        mock_connect.return_value.__enter__.return_value = mock_conn

        # Mockear la ejecución SQL y los resultados (ningún favorito encontrado)
        mock_result = MagicMock()
        mock_result.fetchall.return_value = []  # Simular que no hay favoritos
        mock_conn.execute.return_value = mock_result

        # Crear un evento mock con pathParameters
        mock_event = {
            "pathParameters": {
                "fk_user": "1234567890abcdef1234567890abcdef"
            }
        }

        # Llamar a la función lambda_handler
        result = lambda_handler(mock_event, None)

        # Verificar que el resultado devuelto sea el esperado
        self.assertEqual(result["statusCode"], 200)
        self.assertEqual(result['body'], json.dumps('Favoritos no encontrados'))

    def test_invalid_user_id(self):
        # Crear un evento mock con pathParameters con un ID de usuario no válido
        mock_event = {
            "pathParameters": {
                "fk_user": "invalid_id_format"
            }
        }

        # Llamar a la función lambda_handler
        result = lambda_handler(mock_event, None)

        # Verificar que el resultado devuelto sea el esperado
        self.assertEqual(result["statusCode"], 400)
        self.assertEqual(result['body'], json.dumps('El ID de usuario no es válido'))
    @patch('get_favorites.get_favorites.db_connection.connect')
    def test_sqlalchemy_error(self, mock_connect):
        mock_event = {
            "pathParameters": {
                "fk_user": "1234567890abcdef1234567890abcdef"
            }
        }
        # Configurar el mock para lanzar SQLAlchemyError al ejecutar consultas
        mock_conn = MagicMock()
        mock_connect.return_value.__enter__.return_value = mock_conn
        mock_conn.execute.side_effect = SQLAlchemyError("Error en la base de datos")
        # Llamar a la función lambda_handler
        response = lambda_handler(mock_event, None)

        # Verificar que el resultado devuelto sea el esperado
        self.assertEqual(response['statusCode'], 500)
        self.assertEqual(response['body'], json.dumps('Error al procesar los datos'))

    @patch("get_favorites.get_favorites.db_connection.connect")
    def test_lambda_handler(self, mock_connect):
        # Genera un UUID y usa su valor hexadecimal
        valor_id = uuid.uuid4().hex

        mock_event = {
            "pathParameters": {
                "fk_user": valor_id  # Asegúrate de que este es un valor de 32 caracteres hexadecimales
            }
        }

        # Configurar el mock para la conexión a la base de datos
        mock_conn = MagicMock()
        mock_connect.return_value.__enter__.return_value = mock_conn

        # Mock the SQL execution and results
        mock_conn.execute.return_value.fetchall.return_value = [
            {
                "fk_film": bytes.fromhex(valor_id),
                "title": "Film Title",
                "description": "Film Description",
                "length": 120,
                "category_name": "Category"
            }
        ]

        # Expected result
        esperado = [
            {
                "fk_film": valor_id,
                "title": "Film Title",
                "description": "Film Description",
                "length": 120,
                "category_name": "Category"
            }
        ]

        result = lambda_handler(mock_event, None)
        self.assertEqual(result["statusCode"], 200)
        body = json.loads(result["body"])
        self.assertTrue(isinstance(body, list))
        self.assertEqual(body, esperado)


if __name__ == '__main__':
    unittest.main()

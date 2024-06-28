import uuid
from decimal import Decimal
from unittest.mock import patch, MagicMock
import unittest
import json

from sqlalchemy.exc import SQLAlchemyError
from get_user.get_user import lambda_handler


class MyTestCase(unittest.TestCase):

    @patch("get_user.get_user.db_connection.connect")
    def test_lambda_handler_no_users_found(self, mock_connect):
        # Mock de la conexión y el resultado vacío de la consulta
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.execute.return_value.fetchall.return_value = []

        event = {}
        context = {}

        response = lambda_handler(event, context)

        self.assertEqual(response['statusCode'], 404)
        self.assertEqual(json.loads(response['body']), 'No users found')

    @patch("get_user.get_user.db_connection.connect")
    def test_lambda_handler_sqlalchemy_error(self, mock_connect):
        def test_sqlalchemy_error(self, mock_connect):
            mock_event = {}
            # Configurar el mock para lanzar SQLAlchemyError al ejecutar consultas
            mock_conn = MagicMock()
            mock_connect.return_value.__enter__.return_value = mock_conn
            mock_conn.execute.side_effect = SQLAlchemyError("Error en la base de datos")
            # Llamar a la función lambda_handler
            response = lambda_handler(mock_event, None)

            # Verificar que el resultado devuelto sea el esperado
            self.assertEqual(response['statusCode'], 500)
            self.assertEqual(response['body'], json.dumps('Error al procesar los datos'))

    """
    @patch("get_user.get_user.db_connection.connect")
    def test_lambda_handler_success(self, mock_connect):
        # Genera un UUID y usa su valor hexadecimal
        valor_id = uuid.uuid4().hex

        mock_event = {}

        # Configurar el mock para la conexión a la base de datos
        mock_conn = MagicMock()
        mock_connect.return_value.__enter__.return_value = mock_conn

        # Mock the SQL execution and results
        mock_result = MagicMock()
        mock_result.__iter__.return_value = iter([
            {'user_id': bytes.fromhex(valor_id),
             'name': 'John',
             'lastname': 'Doe',
             'email': 'john.doe@example.com',
             'password': 'hashedpassword',
             'fk_rol': bytes.fromhex(valor_id),
             'fk_subscription': bytes.fromhex(valor_id)}
        ])
        mock_conn.execute.return_value = mock_result

        # Expected result
        esperado = [
            {'user_id': valor_id,
             'name': 'John',
             'lastname': 'Doe',
             'email': 'john.doe@example.com',
             'password': 'hashedpassword',
             'fk_rol': valor_id,
             'fk_subscription': valor_id}
        ]

        result = lambda_handler(mock_event, None)
        self.assertEqual(result["statusCode"], 200)
        body = json.loads(result["body"])
        self.assertTrue(isinstance(body, list))
        self.assertEqual(body, esperado)
    """

if __name__ == '__main__':
    unittest.main()

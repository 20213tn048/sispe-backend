import unittest
from unittest.mock import patch, MagicMock
from update_rateing.update_rateing import lambda_handler
import json

mock_body = {
    'grade': 5.0,
    'comment': 'updated_comment',
    'fk_user': '1234567890abcdef',
    'fk_film': '1234567890abcdef'
}

mock_path = {
    'id': '1234567890abcdef'
}


class TestUpdateRateing(unittest.TestCase):

    @patch("update_rateing.update_rateing.db_connection.connect")
    def test_rateing_not_found(self, mock_connection):
        mock_conn = MagicMock()
        mock_connection.return_value = mock_conn
        mock_conn.execute.return_value.fetchone.return_value = None

        event = {'body': json.dumps(mock_body), 'pathPArameters': json.dumps(mock_path)}

        result = lambda_handler(event, None)
        self.assertEqual(result['statusCode'], 404)
        self.assertEqual('Rateing not found', result['body'])
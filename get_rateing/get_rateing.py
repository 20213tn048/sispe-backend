import logging
import json
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.exc import SQLAlchemyError
import os

# Configuración del logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Configuración de la base de datos
DB_USER = os.environ.get("DBUser")
DB_PASSWORD = os.environ.get("DBPassword")
DB_NAME = os.environ.get("DBName")
DB_HOST = os.environ.get("DBHost")
db_connection_str = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'
db_connection = create_engine(db_connection_str)
metadata = MetaData()

# Definición de la tabla de rateings
rateings = Table('rateings', metadata, autoload_with=db_connection)

# Función Lambda para obtener un rateing
def lambda_handler(event, context):
    try:
        logger.info("Getting rateing")
        rateing_id = event['pathParameters']['id']

        conn = db_connection.connect()
        query = rateings.select().where(rateings.c.rateing_id == bytes.fromhex(rateing_id))
        result = conn.execute(query)
        rateing = result.fetchone()
        conn.close()

        if rateing:
            rateing_dict = {column: str(value) if isinstance(value, bytes) else value for column, value in rateing.items()}
            return {
                'statusCode': 200,
                'body': json.dumps(rateing_dict)
            }
        else:
            return {
                'statusCode': 404,
                'body': json.dumps('Rateing not found')
            }
    except SQLAlchemyError as e:
        logger.error(f"Error getting rateing: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps('Error getting rateing')
        }

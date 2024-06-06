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

# Definición de la tabla de raitings
raiting = Table('raiting', metadata, autoload_with=db_connection)

# Función Lambda para obtener un raiting
def lambda_handler(event, context):
    try:
        logger.info("Getting raiting")
        raiting_id = event['pathParameters']['id']

        conn = db_connection.connect()
        query = raiting.select().where(raiting.c.id == raiting_id)
        result = conn.execute(query).fetchone()
        conn.close()

        if result:
            return {
                'statusCode': 200,
                'body': json.dumps(dict(result))
            }
        else:
            return {
                'statusCode': 404,
                'body': json.dumps('Raiting not found')
            }
    except SQLAlchemyError as e:
        logger.error(f"Error getting raiting: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps('Error getting raiting')
        }

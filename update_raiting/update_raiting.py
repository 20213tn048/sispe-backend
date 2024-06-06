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

# Función Lambda para actualizar un raiting
def lambda_handler(event, context):
    try:
        logger.info("Updating raiting")
        data = json.loads(event['body'])
        raiting_id = event['pathParameters']['id']

        conn = db_connection.connect()
        query = raiting.update().where(raiting.c.id == raiting_id).values(
            calificacion=data['calificacion'],
            raitingcol=data['raitingcol'],
            usuarios_id=data['usuarios_id'],
            pelicula_id=data['pelicula_id']
        )
        result = conn.execute(query)
        conn.close()

        if result.rowcount:
            return {
                'statusCode': 200,
                'body': json.dumps('Raiting updated')
            }
        else:
            return {
                'statusCode': 404,
                'body': json.dumps('Raiting not found')
            }
    except SQLAlchemyError as e:
        logger.error(f"Error updating raiting: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps('Error updating raiting')
        }
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON format: {e}")
        return {
            'statusCode': 400,
            'body': json.dumps('Invalid JSON format')
        }

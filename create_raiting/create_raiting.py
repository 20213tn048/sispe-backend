import logging
import json
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, ForeignKey
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
raiting = Table('raiting', metadata,
               Column('id', Integer, primary_key=True),
               Column('calificacion', Integer, nullable=False),
               Column('raitingcol', String(255), nullable=False),
               Column('usuarios_id', Integer, ForeignKey('usuarios.id'), nullable=False),
               Column('pelicula_id', Integer, ForeignKey('pelicula.id'), nullable=False))

# Función Lambda para crear un nuevo raiting
def lambda_handler(event, context):
    try:
        logger.info("Creating raiting")
        data = json.loads(event['body'])

        conn = db_connection.connect()
        query = raiting.insert().values(calificacion=data['calificacion'], raitingcol=data['raitingcol'],
                                       usuarios_id=data['usuarios_id'], pelicula_id=data['pelicula_id'])
        conn.execute(query)
        conn.close()
        return {
            'statusCode': 200,
            'body': json.dumps('Raiting creado')
        }
    except SQLAlchemyError as e:
        logger.error(f"Error creating raiting: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps('Error creating raiting')
        }
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON format: {e}")
        return {
            'statusCode': 400,
            'body': json.dumps('Invalid JSON format')
        }

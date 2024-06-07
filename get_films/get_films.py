import os
import logging
import json
from sqlalchemy import create_engine, MetaData, Table, Column, String, BINARY, Integer, Enum, ForeignKey
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql import select

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

# Definición de la tabla de categorías
categories = Table('categories', metadata,
                   Column('category_id', BINARY(16), primary_key=True),
                   Column('name', String(45), nullable=False))

# Definición de la tabla de film
films = Table('film', metadata,
                   Column('film_id', BINARY(16), primary_key=True),
                   Column('title', String(60), nullable=False),
                   Column('description', String(60), nullable=False),
                   Column('length', Integer, nullable=False),
                   Column('status', Enum('activo', 'inactivo', name='status_enum'), nullable=False),
                   Column('fk_category', BINARY(16), ForeignKey('categories.category_id'), nullable=False)
              )


# Función Lambda para obtener películas
def lambda_handler(event, context):
    try:
        logger.info("Fetching films")
        conn = db_connection.connect()
        query = films.select()
        result = conn.execute(query)
        film_list = [{column: value.hex() if isinstance(value, bytes) else value for column, value in row.items()} for
                     row in result]
        conn.close()

        if not film_list:
            return {
                'statusCode': 404,
                'body': json.dumps('No films found')
            }

        return {
            'statusCode': 200,
            'body': json.dumps(film_list)
        }
    except SQLAlchemyError as e:
        logger.error(f"Error fetching films: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps('Error fetching films')
        }

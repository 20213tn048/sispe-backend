import os
import logging
import json
from sqlalchemy import create_engine, MetaData, Table, Column, String, BINARY, Integer, Enum, ForeignKey, select
from sqlalchemy.exc import SQLAlchemyError

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

# Definición de la tabla de categorías para agregar las tablas foraneas
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


# Función Lambda para crear una nueva película
def lambda_handler(event, context):
    try:
        logger.info("Creating film")
        data = json.loads(event['body'])

        conn = db_connection.connect()
        query = select([categories]).where(categories.c.category_id == bytes.fromhex(data['category_id']))
        result = conn.execute(query)
        existing_category = result.fetchone()
        if not existing_category:
            conn.close()
            return {
                'statusCode': 400,
                'body': json.dumps('Category ID does not exist')
            }

        query = films.insert().values(
            film_id=bytes.fromhex(data['film_id']),
            title=data['title'],
            description=data['description'],
            duration=data['duration'],
            status=data['status'],
            category_id=bytes.fromhex(data['category_id'])
        )
        result = conn.execute(query)
        conn.close()
        return {
            'statusCode': 200,
            'body': json.dumps('Film created')
        }
    except SQLAlchemyError as e:
        logger.error(f"Error creating film: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps('Error creating film')
        }
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON format: {e}")
        return {
            'statusCode': 400,
            'body': json.dumps('Invalid JSON format')
        }
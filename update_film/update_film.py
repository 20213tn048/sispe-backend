import os
import logging
import json
from sqlalchemy import create_engine, MetaData, Table, Column, String, BINARY, Integer, Enum, ForeignKey
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.types import DECIMAL 

# Configuración del logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Configuración de la base de datos
DB_USER = os.environ.get("DBUser")
DB_PASSWORD = os.environ.get("DBPassword")
DB_NAME = os.environ.get("DBName")
DB_HOST = os.environ.get("DBHost")
#db_connection_str = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'

db_connection_str=f'mysql+pymysql://admin:nhL5zPpY1I9w@integradora-lambda.czc42euyq8iq.us-east-1.rds.amazonaws.com/sispe'

db_connection = create_engine(db_connection_str)
metadata = MetaData()

# Definición de la tabla de categorías
categories = Table('categories', metadata,
                   Column('category_id', BINARY(16), primary_key=True),
                   Column('name', String(45), nullable=False))

# Definición de la tabla de film
films = Table('films', metadata,
              Column('film_id', BINARY(16), primary_key=True),
              Column('title', String(60), nullable=False),
              Column('description', String(255), nullable=False),
              Column('length', DECIMAL, nullable=False),  # Corregido aquí
              Column('status', Enum('Activo', 'Inactivo', name='status_enum'), nullable=False),
              Column('fk_category', BINARY(16), ForeignKey('categories.category_id'), nullable=False)
              )



# Función Lambda para actualizar una película
def lambda_handler(event, context):
    try:
        logger.info("Updating film")
        data = json.loads(event['body'])

        # Validar que los datos necesarios están presentes en el cuerpo
        required_fields = ['film_id', 'title', 'description', 'length', 'status', 'fk_category']
        if not all(field in data for field in required_fields):
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json'
                },
                'body': json.dumps('Missing required fields in request body')
            }

        conn = db_connection.connect()
        query = films.select().where(films.c.film_id == bytes.fromhex(data['film_id']))
        result = conn.execute(query)
        existing_film = result.fetchone()
        if not existing_film:
            conn.close()
            return {
                'statusCode': 404,
                'headers': {
                    'Content-Type': 'application/json'
                },
                'body': json.dumps('Film not found')
            }

        # Actualizar la película
        query = films.update().where(films.c.film_id == bytes.fromhex(data['film_id'])).values(
            title=data['title'],
            description=data['description'],
            length=data['length'],
            status=data['status'],
            fk_category=bytes.fromhex(data['fk_category'])
        )
        result = conn.execute(query)
        conn.close()
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps('Film updated')
        }
    except SQLAlchemyError as e:
        logger.error(f"Error updating film: {e}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps('Error updating film')
        }
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON format: {e}")
        return {
            'statusCode': 400,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps('Invalid JSON format')
        }

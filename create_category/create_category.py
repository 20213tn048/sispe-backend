import logging
import json
from sqlalchemy import create_engine, MetaData, Table, Column, String, BINARY
from sqlalchemy.exc import SQLAlchemyError

# Configuración del logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Configuración de la base de datos
DB_USER = 'admin'
DB_PASSWORD = 'nhL5zPpY1I9w'
DB_NAME = 'sispe'
DB_HOST = 'integradora-lambda.czc42euyq8iq.us-east-1.rds.amazonaws.com'
db_connection_str = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'
db_connection = create_engine(db_connection_str)
metadata = MetaData()

# Definición de la tabla de categorías
categories = Table('categories', metadata,
                   Column('category_id', BINARY(16), primary_key=True),
                   Column('name', String(45), nullable=False))

# Función Lambda para crear una nueva categoría
def lambda_handler(event, context):
    try:
        logger.info("Creating category")
        data = json.loads(event['body'])

        conn = db_connection.connect()
        query = categories.select().where(categories.c.category_id == bytes.fromhex(data['category_id']))
        result = conn.execute(query)
        existing_category = result.fetchone()
        if existing_category:
            conn.close()
            return {
                'statusCode': 400,
                'body': json.dumps('Category ID already exists')
            }

        query = categories.insert().values(category_id=bytes.fromhex(data['category_id']), name=data['name'])
        result = conn.execute(query)
        conn.close()
        return {
            'statusCode': 200,
            'body': json.dumps('Categoría creada')
        }
    except SQLAlchemyError as e:
        logger.error(f"Error creating category: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps('Error creating category')
        }
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON format: {e}")
        return {
            'statusCode': 400,
            'body': json.dumps('Invalid JSON format')
        }
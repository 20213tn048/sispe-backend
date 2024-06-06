import os
import logging
import json
from sqlalchemy import create_engine, MetaData, Table, Column, String, BINARY
from sqlalchemy.exc import SQLAlchemyError

# Configuración del logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Configuración de la base de datos
DB_USER = os.environ.get('DBUser')
DB_PASSWORD = os.environ.get('DBPassword')
DB_NAME = os.environ.get('DBName')
DB_HOST = os.environ.get('DBHost')
db_connection_str = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'
db_connection = create_engine(db_connection_str)
metadata = MetaData()

# Definición de la tabla de categorías
categories = Table('categories', metadata,
                   Column('category_id', BINARY(16), primary_key=True),
                   Column('name', String(45), nullable=False))

# Función Lambda para obtener categorías
def lambda_handler(event, context):
    try:
        logger.info("Fetching categories")
        conn = db_connection.connect()
        query = categories.select()
        result = conn.execute(query)
        category_list = [{column: value.hex() if isinstance(value, bytes) else value for column, value in row.items()} for row in result]
        conn.close()
        
        if not category_list:
            return {
                'statusCode': 404,
                'body': json.dumps('No categories found')
            }

        return {
            'statusCode': 200,
            'body': json.dumps(category_list)
        }
    except SQLAlchemyError as e:
        logger.error(f"Error fetching categories: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps('Error fetching categories')
        }
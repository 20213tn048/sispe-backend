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

#Definicion de la tabla roles para agregar atributos foraneos a la tabla users
roles = Table('roles', metadata,
              Column('rol_id', BINARY(16), primary_key=True),
              Column('name', String(45), nullable=True))

#Definicion de la tabla subscription para agregar atributos foraneos a la tabla users
subscriptions = Table('subscriptions', metadata,
                      Column('subscription_id', BINARY(16), primary_key=True),
                      Column('start_date',DATETIME,nullable=False),
                      Column('end_date',DATETIME,nullable=False))

#Definicion de la tabla films para agregar atributos foraneos a la tabla favorites
films = Table('film', metadata,
                   Column('film_id', BINARY(16), primary_key=True),
                   Column('title', String(60), nullable=False),
                   Column('description', String(60), nullable=False),
                   Column('duration', Integer, nullable=False),
                   Column('status', Enum('activo', 'inactivo', name='status_enum'), nullable=False),
                   Column('category_id', BINARY(16), ForeignKey('categories.category_id'), nullable=False)
              )

#Definicion de la tabla users para agregar los atributos foraneos a la tabla favorites
users = Table('users',metadata,
              Column('user_id', BINARY(16), primary_key=True),
              Column('name', String(60), nullable=False),
              Column('lastname', String(60), nullable=False),
              Column('email', String(100), nullable=False),
              Column('password', String(225), nullable=False),
              Column('fk_rol', BINARY(16), ForeignKey('roles.rol_id'), nullable=False),
              Column('fk_subscription', BINARY(16), ForeignKey('subscription.subscription_id'), nullable=False),)

#Definicion de la tabla favorites
favorites = Table('favorites',metadata,
                  Column('favorite_id',BINARY(16), primary_key=True),
                  Column('fk_user',BINARY(16), ForeingKey('users.user_id'), nulleable=False),
                  Column('fk_film',BINARY(16), ForeingKey('films.film_id'), nullable=False),)

def lambda_handler(event,context):
    try:
        logger.info("Fetching favorites")
        conn = db_connection.connect()
        query = favorites.select().where(favorites.c.fk_user == user_id)
        result = conn.execute(query)
        conn.close()

        if result.rowcount == 0:
            return {
                'statusCode': 200,
                'body':json.dumps('Favoritos no encontrados')
            }

        return{
            'statusCode': 200,
            'body':json.dumps(result)
        }
    except SQLAlchemyError as e:
        logger.error(f'Error fetching favorites: {e}')
        return {
            'statusCode': 500,
            'body':json.dumps('Error al obtener favoritos')
        }
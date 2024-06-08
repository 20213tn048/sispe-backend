import os
import logging
import json
from sqlalchemy import create_engine, MetaData, Table, Column, String, BINARY, Integer, Enum, ForeignKey, DATETIME

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql import select

# Configuración del logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Configuración de la base de datos
DB_USER = os.environ.get('DBUser')
DB_PASSWORD = os.environ.get('DBPassword')
DB_NAME = os.environ.get('DBName')
DB_HOST = os.environ.get('DBHost')
#db_connection_str = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'
db_connection_str=f'mysql+pymysql://admin:nhL5zPpY1I9w@integradora-lambda.czc42euyq8iq.us-east-1.rds.amazonaws.com/sispe'
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
                  Column('fk_user',BINARY(16), ForeignKey('users.user_id'), nullable=False),
                  Column('fk_film',BINARY(16), ForeignKey('films.film_id'), nullable=False),)

def is_hex(s):
    return len(s) == 32 and all(c in '0123456789abcdefABCDEF' for c in s)

def lambda_handler(event,context):
    try:
        if event.get('body') is None:
            return{
                'statusCode':400,
                'body':json.dumps('Entrada invalida, cuerpo no encontrado')
            }

        logger.info("Fetching favorites")
        data = json.loads(event['body'])
        fk_user = data.get('fk_user')

        if not fk_user:
            return {
                'statusCode':400,
                'body':json.dumps('usuario necesario')
            }

        if not is_hex(fk_user):
            return{
                'statusCode':400,
                'body':json.dumps('El ID de usuario no es valido')
            }

        user_id = bytes.fromhex(fk_user)

        conn = db_connection.connect()

        #Verificar si el usuario existe
        user_query = select([users]).where(users.c.user_id == user_id)
        user_result = conn.execute(user_query).fetchone()
        print(user_result,'-USUARIO ENCONTRADO')
        if user_result is None:
            conn.close()
            return{
                'statusCode':400,
                'body':json.dumps('Usuario no encontrado')
            }

        #Obtener los favoritos del usuario
        query = select([favorites]).where(favorites.c.fk_user == user_id)
        result = conn.execute(query)
        rows = result.fetchall()
        conn.close()

        if not rows:
            return {
                'statusCode': 200,
                'body':json.dumps('Favoritos no encontrados')
            }

        favorites_list = [dict(row) for row in rows]

        return{
            'statusCode': 200,
            'body':json.dumps(favorites_list)
        }
    except SQLAlchemyError as e:
        logger.error(f'Error fetching favorites: {e}')
        return {
            'statusCode': 500,
            'body':json.dumps('Error al obtener favoritos')
        }
    except json.JSONDecodeError as e:
        logger.error(f'Error json format: {e}')
        return {
            'statusCode': 500,
            'body':json.dumps('Error de formato JSON')
        }
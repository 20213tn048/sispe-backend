import os
import logging
import json
from sqlalchemy import create_engine, MetaData, Table, Column, String, BINARY
from sqlalchemy.exc import SQLAlchemyError

#Configuracion del logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

#Configuracion de la base de datos
DB_USER = os.environ.get("DBUser")
DB_PASSWORD = os.environ.get("DBPassword")
DB_NAME = os.environ.get("DBName")
DB_HOST = os.environ.get("DBHost")
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

#Funcion Lambda para agregar una nueva pelicula a la lista de favoritos
def lambda_handler(event, context):
    try:
        logger.info("Creating favorite")
        data = json.loads(event['body'])
        user_id = bytes.fromhex(data['fk_user'])
        film_id = bytes.fromhex(data['fk_film'])

        conn = db_connection.connect()

        #Verificar si la pelicula ya esta en favoritos
        query = select([favorites]).where(
            and_(
                favorites.c.fk_user == user_id,
                favorites.c.fk_film == film_id
            )
        )
        result = conn.execute(query)
        existing_favorites = result.fetchone()

        if existing_favorites:
            conn.close()
            return {
                'statusCode': 400,
                'body': json.dumps('Pelicula ya agregada a la lista de favoritos')
            }

        #Verificar si la pelicula esta activa
        query = select([films]).where(
            and_(
                films.c.film_id == film_id,
                films.c.status == 'activo'
            )
        )
        result = conn.execute(query)
        active_film = result.fetchone()

        if not active_film:
            conn.close()
            return {
                'statusCode': 400,
                'body':json.dumps('La pelicula no esta disponible o no existe')
            }

        #Verificar si la suscripcion del usuario aun es valida
        query = select([users]).where(
            and_(
                subscriptions.c.subscription_id == users.c.fk_subscription,
                users.c.user_id == user_id,
                subscriptions.c.end_date >= datetime.now()
            )
        )
        result = conn.execute(query)
        valid_subscriptions = result.fetchone()

        if not valid_subscriptions:
            conn.close()
            return {
                'statusCode': 400,
                'body': json.dumps('La suscripcion no es valida o ha caducado')
            }

        #Insertar la pelicula a favoritos
        query = favorites.insert().values(
            favorite_id = bytes.fromhex(data['favorite_id']),
            fk_user = user_id,
            fk_film = film_id
        )
        conn.execute(query)
        conn.close()

        return {
            'statusCode':200,
            'body':json.dumps('Pelicula agregada a la lista de favoritos')
        }
    except SQLAlchemyError as e:
        logger.error(f'Error adding favorite: {e}')
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error al agregar a favoritos')
        }
    except json.JSONDecodeError as e:
        logger.error(f'Invalid JSON format: {e}')
        return {
            'statusCode':400,
            'body':json.dumps(f'Formato invalido')
        }
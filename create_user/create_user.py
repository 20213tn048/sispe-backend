import os
import logging
import json
from sqlalchemy import create_engine, MetaData, Table, Column, String, BINARY, UniqueConstraint, ForeignKey, Index, ForeignKeyConstraint
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.orm import sessionmaker
import uuid

# Configuración del logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Configuración de la base de datos
db_connection_str = 'mysql+pymysql://admin:nhL5zPpY1I9w@integradora-lambda.czc42euyq8iq.us-east-1.rds.amazonaws.com/sispe'
db_connection = create_engine(db_connection_str)
metadata = MetaData()

# Definición de la tabla de usuarios
users = Table('users', metadata,
    Column('user_id', BINARY(16), primary_key=True),
    Column('name', String(60), nullable=False),
    Column('lastname', String(60), nullable=False),
    Column('email', String(100), nullable=False),
    Column('password', String(255), nullable=False),
    Column('fk_rol', BINARY(16), nullable=False),
    Column('fk_subscription', BINARY(16), nullable=False),
    UniqueConstraint('email', name='unique_email'),
    ForeignKeyConstraint(['fk_rol'], ['roles.rol_id'], name='fk_rol'),
    ForeignKeyConstraint(['fk_subscription'], ['subscriptions.subscription_id'], name='fk_subscription'),
    Index('fk_rol_idx', 'fk_rol'),
    Index('fk_subscription_idx', 'fk_subscription')
)

# Crear una fábrica de sessionmaker
Session = sessionmaker(bind=db_connection)

# Función Lambda para crear un nuevo usuario
def lambda_handler(event, context):
    logger.info("Iniciando lambda_handler")
    try:
        data = json.loads(event['body'])
        user_id = uuid.uuid4().bytes
        name = data.get('name')
        lastname = data.get('lastname')
        email = data.get('email')
        password = data.get('password')
        fk_rol = bytes.fromhex(data.get('fk_rol'))
        fk_subscription = bytes.fromhex(data.get('fk_subscription'))

        if not all([user_id, name, lastname, email, password, fk_rol, fk_subscription]):
            logger.error("Faltan datos obligatorios en el cuerpo de la solicitud")
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json'
                },
                'body': json.dumps('Faltan datos obligatorios')
            }

        with Session() as session:
            # Verificar si el email ya existe
            existing_user = session.query(users).filter_by(email=email).first()
            if existing_user:
                logger.error(f"El correo {email} ya está registrado")
                return {
                    'statusCode': 400,
                    'headers': {
                        'Content-Type': 'application/json'
                    },
                    'body': json.dumps('This email is already registered')
                }

            insert_query = users.insert().values(
                user_id=user_id,
                name=name,
                lastname=lastname,
                email=email,
                password=password,
                fk_rol=fk_rol,
                fk_subscription=fk_subscription
            )
            session.execute(insert_query)
            session.commit()
            logger.info(f"Usuario {email} creado exitosamente")

            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json'
                },
                'body': json.dumps('Usuario creado exitosamente')
            }
    except IntegrityError as e:
        logger.error(f"Error de integridad: {e}")
        return {
            'statusCode': 400,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps('This email is already registered')
        }
    except SQLAlchemyError as e:
        logger.error(f"Error al crear el usuario: {e}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps('Error al crear el usuario')
        }
    except json.JSONDecodeError as e:
        logger.error(f"Formato de JSON inválido: {e}")
        return {
            'statusCode': 400,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps('Formato de JSON inválido')
        }
    except Exception as e:
        logger.error(f"Error inesperado: {e}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps('Error interno del servidor')
        }
    finally:
        logger.info("Ejecución de lambda_handler completada")

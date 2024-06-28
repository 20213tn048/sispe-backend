import json
import logging
import uuid
from sqlalchemy import create_engine, MetaData, Table, Column, String, BINARY, DateTime
from sqlalchemy.exc import SQLAlchemyError
import os
from datetime import datetime
import stripe

logger = logging.getLogger()
logger.setLevel(logging.INFO)

DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')
DB_HOST = os.getenv('DB_HOST')

STRIPE_API_KEY = os.getenv('STRIPE_SECRET_KEY')
stripe.api_key = STRIPE_API_KEY

db_connection_str = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'
db_connection = create_engine(db_connection_str)

metadata = MetaData()
subscriptions = Table('subscriptions', metadata,
                      Column('subscription_id', BINARY(16), primary_key=True),
                      Column('start_date', DateTime, nullable=False),
                      Column('end_date', DateTime, nullable=False),
                      Column('transaction', String(255), nullable=False))


def create_checkout_session():
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'mxn',
                'product_data': {
                    'name': 'Subscripción de 1 mes a SISPE'
                },
                'unit_amount': 10000,  # El monto en centavos
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url='http://localhost:3000/success?session_id={CHECKOUT_SESSION_ID}',
        cancel_url='http://localhost:3000/cancel'
    )
    return session


def lambda_handler(event, context):
    try:
        logger.info("Procesando solicitud")

        if event.get('body') is None:
            raise ValueError("El cuerpo de la solicitud no puede estar vacío")

        data = json.loads(event['body'])

        return create_subscription(data)

    except ValueError as ve:
        logger.error(f"Error de valor: {ve}")
        return {
            'statusCode': 400,
            'body': json.dumps(f"Error: {str(ve)}")
        }

    except SQLAlchemyError as e:
        logger.error(f"Error de base de datos: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps('Error Interno del Servidor. No se pudo procesar la solicitud')
        }

    except Exception as e:
        logger.error(f"Error inesperado: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps("Error Interno del Servidor")
        }


def create_subscription(data):
    try:
        if 'start_date' not in data or 'end_date' not in data:
            raise ValueError('Los campos de fecha de inicio y fecha de fin son obligatorios')

        # Eliminar la 'Z' del formato de fecha
        start_date = datetime.fromisoformat(data['start_date'].replace('Z', ''))
        end_date = datetime.fromisoformat(data['end_date'].replace('Z', ''))

        current_date = datetime.now()

        if start_date < current_date:
            raise ValueError('La fecha de inicio no debe estar en el pasado')

        if start_date >= end_date:
            raise ValueError('La fecha de inicio debe ser antes de la fecha de fin')

        session = create_checkout_session()

        subscription_id = uuid.uuid4().bytes
        transaction = session.id

        # Registrar los detalles de la conexión
        logger.info(f"Conectando a la base de datos en {db_connection_str}")
        conn = db_connection.connect()
        trans = conn.begin()

        try:
            # Registrar la consulta de inserción
            query = subscriptions.insert().values(subscription_id=subscription_id, start_date=start_date,
                                                  end_date=end_date, transaction=transaction)
            logger.info(f"Ejecutando consulta: {query}")
            result = conn.execute(query)

            # Verificar si la inserción fue exitosa
            logger.info(f"Filas afectadas: {result.rowcount}")
            trans.commit()

        except Exception:
            trans.rollback()
            raise

        finally:
            conn.close()

        response = {
            'subscription_id': subscription_id.hex(),
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'session_id': session.id
        }

        return {
            'statusCode': 201,
            'body': json.dumps(response)
        }

    except SQLAlchemyError as e:
        logger.error(f"Error de SQLAlchemy: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps("Error Interno del Servidor")
        }

    except Exception as e:
        logger.error(f"Error inesperado en create_subscription: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps("Error Interno del Servidor")
        }


def create_session():
    try:
        session = create_checkout_session()
        return {
            'statusCode': 200,
            'body': json.dumps({'id': session.id})
        }
    except Exception as e:
        logger.error(f"Error inesperado en create_session: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps("Error Interno del Servidor")
        }

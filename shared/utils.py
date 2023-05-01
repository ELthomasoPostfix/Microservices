import psycopg2

from flask import Flask
from flask_restful import Api
from typing import Tuple

from .config import config as shared_flask_app_config


def create_app(app_name: str) -> Tuple[Flask, Api]:
    """A generic Flask app factory that does general app setup.

    The app factory does not register any api endpoints.

    :return: (Flask app, Flask RESTful API)
    """
    # Do Flask app setup
    app = Flask(app_name)
    app.config.from_mapping(shared_flask_app_config)

    # Do Flask RESTful api setup
    api = Api(app)

    return app, api


def retry_connect_until_success(db_name: str, user: str, password: str, host: str):
    """Indefinitely retry establishing a database connection, until successful.

    :param db_name: The name of the database to connect to
    :param user: The user name used to authenticate
    :param password: The password used to authenticate
    :param host: The database host address
    :return: The connection
    """
    conn = None

    while conn is None:
        try:
            conn = psycopg2.connect(dbname=db_name, user=user, password=password, host=host)
            print("DB connection succesful")
            return conn
        except psycopg2.OperationalError:
            import time
            time.sleep(1)
            print("Retrying DB connection")


def initialize_micro_service(microservice_name: str, db_host: str):
    """Perform the necessary setup to initialize a micro service.

    :param microservice_name: The name of the microservice. Used to
    determine the Flask app name and postgresql database name
    :param db_host: The database host address
    :return: The major components of the microservice
    """
    app, api = create_app(microservice_name)

    conn = retry_connect_until_success(db_name=microservice_name,
                                   user=app.config["POSTGRES_USER"],
                                   password=app.config["POSTGRES_PASSWORD"],
                                   host=db_host)
    return app, api, conn

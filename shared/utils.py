import psycopg2

from flask import Flask, Response
from flask_restful import Api, reqparse
from flask_apispec import FlaskApiSpec, marshal_with
from marshmallow import Schema, ValidationError
from json import JSONDecodeError
from typing import Tuple, Callable

from shared.APIResponses import make_response_error, GenericResponseMessages as E_MSG

from .config import config as shared_flask_app_config


def create_app(app_name: str, apispec_config: dict) -> Tuple[Flask, Api, FlaskApiSpec]:
    """A generic Flask app factory that does general app setup.

    The app factory does not register any api endpoints.

    :return: (Flask app, Flask RESTful API)
    """
    # Do Flask app setup
    app = Flask(app_name)
    app.config.from_mapping(shared_flask_app_config)
    app.config.from_mapping(apispec_config)

    # Do Flask RESTful api setup
    api = Api(app)

    # Do Swagger doc generation
    docs = FlaskApiSpec(app)

    return app, api, docs


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


def initialize_micro_service(microservice_name: str, db_host: str, apispec_config: dict):
    """Perform the necessary setup to initialize a micro service.

    :param microservice_name: The name of the microservice. Used to
    determine the Flask app name and postgresql database name
    :param db_host: The database host address
    :return: The major components of the microservice
    """
    app, api, docs = create_app(microservice_name, apispec_config)

    conn = retry_connect_until_success(db_name=microservice_name,
                                   user=app.config["POSTGRES_USER"],
                                   password=app.config["POSTGRES_PASSWORD"],
                                   host=db_host)
    return app, api, docs, conn


def marshal_with_flask_enforced(schema, code='default', description='', inherit=None, apply=None):
    """A convenience wrapper that enforces marshalling of loosely conformant response data.
    
    This wrapper requires the type of all API responses to be flask.Response. Furthermore,
    their data must be json serializable.

    If the response status code is 400 or greater (>= 400), then no marshalling or validation
    is performed, and the flask.Response is simply passed up. This means that this decorator
    is unsuited for use with a *code* parameter in the 400+ range.

    This wrapper condences the boilerplate of validating and marshalling all API response
    data into the correct format, using flask-apispec. Its use is recommended for the
    sake of elegance and, more importantly, avoiding code duplication while also somewhat
    enforcing a uniform return format in the case of response data validation errors.

    Usage: ::

        from flask import Flask, make_response
        from marshmallow import Schema, fields
    
        app = Flask(__name__)

        class CalculatorResponseSchema(Schema):
            result = fields.Integer(required=True)
            precision = fields.Integer()

        @marshal_with_flask_enforced(CalculatorResponseSchema, code=200)
        def add(x: int, y: int):
            return make_response({ "result": x+y })

        @marshal_with_flask_enforced(CalculatorResponseSchema, code=200)
        def add_not_flask_response(x: int, y: int):
            return {
                "result": x+y
            }

        @marshal_with_flask_enforced(CalculatorResponseSchema, code=200)
        def add_missing_res(x: int, y: int):
            return make_response({ })

        @marshal_with_flask_enforced(CalculatorResponseSchema, code=200)
        def add_400s_plus_response(x: int, y: int):
            return make_response({ "foo": "bar" }, 400)

    .. function:: add(x: int, y: int)
    .. function:: sub(x: int, y: int)
    In the previous code, calling :func:`add` would result in the following response body: ::

        {
            'result': 3
        }
    
    Calling :func:`add_not_flask_response` would result in the following response body: ::

        {
            'error': 'All API responses must be flask.Response instances',
            'message': 'Something went wrong'
        }

    Calling :func:`add_missing_res` would result in the following response body: ::

        {
            'error': "The response data does not follow the required scheme: {'result': ['Missing data for required field.']}",
            'message': 'Something went wrong'
        }

    Calling :func:`add_400s_plus_response` would result in the following response body: ::

        {
            'foo': 'bar'
        }


    :param schema: :class:`Schema <marshmallow.Schema>` class or instance, or `None`
    :param code: Optional HTTP response code
    :param description: Optional response description
    :param inherit: Inherit schemas from parent classes
    :param apply: Marshal response with specified schema
    :return: The decorator
    """
    def decorator(http_method: Callable):
        """
        The decorator is called instead of the wrapped
        function, but flask restful expects the called
        method to have an http verb (get, post, put,
        delete, ...) as its name.
        """
        decorator.__name__ = http_method.__name__

        @marshal_with(schema=schema, code=code, description=description, inherit=inherit, apply=apply)
        def wrapper(*args, **kwargs) -> Response:
            # Call http method outside try; pass up
            # exceptions raised in http method transparantly
            to_marshal_result = http_method(*args, **kwargs)

            if not isinstance(to_marshal_result, Response):
                return make_response_error(E_MSG.ERROR, "All API responses must be flask.Response instances", 500)

            if not to_marshal_result.is_json:
                return make_response_error(E_MSG.ERROR, "All API response data must be json", 500)

            # Skip marshalling and validation
            if to_marshal_result.status_code >= 400:
                return to_marshal_result

            try:
                instance: Schema = schema()
                content: dict = to_marshal_result.json

                # Validate content to match marshalling schema
                instance.load(content)

                # Convert content to ensure marshalling happens
                to_marshal_result.data = instance.dumps(content)

                return to_marshal_result
            except ValidationError as e:
                return make_response_error(E_MSG.ERROR, f"The response data does not follow the required scheme: {e}", 500)
            except JSONDecodeError as e:
                return make_response_error(E_MSG.ERROR, f"The response data is malformed", 500)

        return wrapper
    return decorator


def to_params_type(python_builtin_cls) -> str:
    """Convert a python type to an apispec params type string.

    The apispec params type string can be passed to the @doc
    decorator to specify a param's type in the generated
    swagger docs.

    Returns a default value, 'unknown type', if the *python_type* is not recognized.
    Valid python types are int, str and bool.

    The default value of an argument's type param for
    the reqparser is the identity lambda function.
    If Thus, if the python type is not recognized, a
    fallthrough value of 'null' is returned.

    :param python_type: The python type to convert
    :return: The apispec param type string
    """
    valid_type_mapping = {
        int: "integer",
        str: "string",
        bool: "boolean",
    }
    if python_builtin_cls in valid_type_mapping:
        return valid_type_mapping[python_builtin_cls]
    else:
        return "null"

def generate_params_from_parser(parser: reqparse.RequestParser) -> dict:
    """Generate a dict of query parameters that can be passed to the params arg of apispec's doc decorator.

    :param parser: The parser with which the arguments have been registered
    """
    return {
        arg.name: {
            "required": arg.required,
            "in": "query",
            "description": arg.help,
            "type": to_params_type(arg.type)
        } for arg in parser.args
        if 'args' in arg.location
    }

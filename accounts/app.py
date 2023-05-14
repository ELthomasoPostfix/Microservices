from flask_apispec import MethodResource, doc, use_kwargs
from psycopg2.errors import UniqueViolation

from shared.utils import initialize_micro_service, marshal_with_flask_enforced
from shared.exceptions import DoesNotExist, get_409_already_exists, get_404_does_not_exist, get_401_authentication_error
from shared.APIResponses import GenericResponseMessages as E_MSG, make_response_message
from schemas import AccountResponseSchema, MicroservicesResponseSchema, RegisterBodySchema, AuthenticationBodySchema, AuthenticationResponseSchema


MICROSERVICE_NAME = "accounts"
DB_HOST = "accounts_persistence"
APISPEC_CONFIG = {
    'APISPEC_SWAGGER_URL': '/swagger/',
    'APISPEC_SWAGGER_UI_URL': '/swagger-ui/',
    'APISPEC_TITLE': 'Microservices',
    'APISPEC_VERSION': '1.0'
}
app, api, docs, conn = initialize_micro_service(MICROSERVICE_NAME, DB_HOST, APISPEC_CONFIG)


class Account(MethodResource):
    """The api endpoint that represents a single account resource.

    This resource supports the following project requirements
        1. account registration
    """
    @staticmethod
    def route() -> str:
        """Get the route to the Account resource.

        :return: The route string
        """
        return f"/account/<string:username>"

    @doc(description='Get a single Account resource, which represents primary information of a user\'s account.', params={
        'username': {'description': 'The username of the chosen account'}
    })
    @marshal_with_flask_enforced(AccountResponseSchema, code=200)
    def get(self, username: str):
        """The query endpoint of a specific account.

        :return: The primary account information
        """

        with conn.cursor() as curs:
            curs.execute("SELECT * FROM account WHERE username = %s;", (username,))
            res = curs.fetchone()

        # DoesNotExist exception response is handled
        # by DoesNotExist error handler
        if res == None:
            raise DoesNotExist(f"The user '{username}' does not exist")

        return make_response_message(E_MSG.SUCCESS, 200, username=res[0])

    @doc(description='Create an Account resource with the specified credentials', params={
        'username': {'description': 'New account\'s username'},
        'password': {'description': 'New account\'s password'}
    })
    @use_kwargs(RegisterBodySchema, location='form')
    @marshal_with_flask_enforced(MicroservicesResponseSchema, code=201)
    def post(self, username: str, **kwargs):
        """The creation endpoint of an account.

        :return: Whether the creation succeeded
        """

        password = kwargs["password"]

        # Duplicate username exception response is handled
        # by UniqueViolation error handler
        with conn.cursor() as curs:
            curs.execute('INSERT INTO account ("username", "password") VALUES (%s, %s);', (username, password))
            conn.commit()

        return make_response_message(E_MSG.SUCCESS, 201)


class Authentication(MethodResource):
    """The api endpoint that represents an Authentication resource.

    An Authentication resource is an authenticating piece of data
    that proves the posessor has been authenticated by the accounts
    microservice.

    This resource supports the following project requirements
        2. verifying username & password match
    """
    @staticmethod
    def route() -> str:
        """Get the route to the Account resource.

        :return: The route string
        """
        return f"/account/<string:username>/auth"

    @doc(description='Get a single Authentication resource, which represents the proof of authentication of a user.', params={
        'username': {'description': 'The username of the to authenticate account'},
        'password': {'description': 'The password to authenticate with'}
    })
    @use_kwargs(AuthenticationBodySchema, location='form')
    @marshal_with_flask_enforced(AuthenticationResponseSchema, code=200)
    def post(self, username: str, **kwargs):
        """The query endpoint of a single user's authentication flow.

        :return: A proof of authentication
        """

        password = kwargs["password"]

        with conn.cursor() as curs:
            curs.execute("SELECT * FROM account WHERE username = %s AND password = %s;", (username, password))
            res = curs.fetchone()

        # Considers both existing and non-existing user
        if res == None:
            return get_401_authentication_error("username and password do not match", append_error=True, authentication_data=False)

        return make_response_message(E_MSG.SUCCESS, 200, authentication_data=True)


@app.errorhandler(DoesNotExist)
def handle_does_not_exist(e):
    return get_404_does_not_exist(e, append_error=True)

@app.errorhandler(UniqueViolation)
def handle_db_unique_violation(e):
    conn.rollback()
    return get_409_already_exists(e)


# Add resources
api.add_resource(Account, Account.route())
api.add_resource(Authentication, Authentication.route())

# Register apispec docs
docs.register(Account)
docs.register(Authentication)

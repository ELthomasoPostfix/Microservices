from flask_apispec import MethodResource, doc

from shared.utils import initialize_micro_service, marshal_with_flask_enforced
from shared.APIResponses import GenericResponseMessages as E_MSG, make_response_error, make_response_message
from schemas import AccountResponseSchema


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
        2. verifying username & password match
    """
    @staticmethod
    def route() -> str:
        """Get the route to the Account resource.

        :return: The route string
        """
        return f"/account/<string:username>"

    @doc(description='Get a single Account resource, which represents primary information of a user\' account.', params={
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

        if res == None:
            return make_response_error(E_MSG.ERROR, "This resource does not exist", 404)

        return make_response_message(E_MSG.SUCCESS, 200, username=res[0])


# Add resources
api.add_resource(Account, Account.route())

# Register apispec docs
docs.register(Account)

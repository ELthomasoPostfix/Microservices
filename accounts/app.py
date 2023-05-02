from flask_apispec import MethodResource, doc

from shared.utils import initialize_micro_service, marshal_with_flask_enforced
from shared.APIResponses import GenericResponseMessages as E_MSG, make_response_message
from schemas import AccountSchema


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
        return f"/account/<int:account_id>"

    @doc(description='Get a single Account resource, which represents primary information of a user\' account.', params={
        'account_id': {'description': 'The internal id of the chosen account'}
    })
    @marshal_with_flask_enforced(AccountSchema, code=200)
    def get(self, account_id: int):
        """The query endpoint of a specific account.

        :return: The primary account information
        """

        return make_response_message(E_MSG.SUCCESS, 200, username="bob", id=account_id)


# Add resources
api.add_resource(Account, Account.route())

# Register apispec docs
docs.register(Account)

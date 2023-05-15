import requests

from flask_apispec import MethodResource, doc
from psycopg2.errors import UniqueViolation

from shared.utils import initialize_micro_service, marshal_with_flask_enforced
from shared.exceptions import DoesNotExist, get_409_already_exists, get_404_does_not_exist
from shared.APIResponses import GenericResponseMessages as E_MSG, make_response_error, make_response_message
from schemas import FriendResponseSchema, FriendsResponseSchema, MicroservicesResponseSchema


MICROSERVICE_NAME = "friends"
DB_HOST = "friends_persistence"
APISPEC_CONFIG = {
    'APISPEC_SWAGGER_URL': '/swagger/',
    'APISPEC_SWAGGER_UI_URL': '/swagger-ui/',
    'APISPEC_TITLE': 'Microservices Friends',
    'APISPEC_VERSION': '1.0'
}
app, api, docs, conn = initialize_micro_service(MICROSERVICE_NAME, DB_HOST, APISPEC_CONFIG)


class Friends(MethodResource):
    """The api endpoint that represents the collection of Friend resources for a user.

    This resource supports the following project requirements
        4. view user's friends list
    """
    @staticmethod
    def route() -> str:
        """Get the route to the collection of Friend resources.

        :return: The route string
        """
        return "/friends/<string:username>"

    @doc(description='Get the collection of Friend resources, which represents the friend list of a user.', params={
        'username': {'description': 'The username of the account to fetch the friend list of'}
    })
    @marshal_with_flask_enforced(FriendsResponseSchema, code=200)
    def get(self, username: str):
        """The query endpoint of the friend list of a specific account.

        :return: The account's friend list
        """

        with conn.cursor() as curs:
            curs.execute("SELECT * FROM friend WHERE username = %s;", (username,))
            res = [
                {
                    "friend_name": friend_name
                }
                for _, friend_name in curs.fetchall()
            ]

        return make_response_message(E_MSG.SUCCESS, 200, result=res)


class Friend(MethodResource):
    """The api endpoint that represents a single Friend relation resource.

    This resource supports the following project requirements
        3. adding friends
    """
    @staticmethod
    def route() -> str:
        """Get the route to the Friend resource.

        :return: The route string
        """
        return f"{Friends.route()}/<string:friendname>"

    @doc(description='Get a single Friend resource, which represents a friend relation between two users.', params={
        'username': {'description': 'The username of the sender (initiator) of the friend relation'},
        'friendname': {'description': 'The username of the receiver (target) of the friend relation'}
    })
    @marshal_with_flask_enforced(FriendResponseSchema, code=200)
    def get(self, username: str, friendname: str):
        """The query endpoint of a specific friend relation.

        :return: The specified friend relation information
        """

        with conn.cursor() as curs:
            curs.execute("SELECT * FROM friend WHERE username = %s AND friendname = %s;", (username, friendname))
            res = curs.fetchone()

        # DoesNotExist exception response is handled
        # by DoesNotExist error handler
        if res == None:
            raise DoesNotExist(f"the users '{username}' and '{friendname}' are not friends")

        return make_response_message(E_MSG.SUCCESS, 200, friend_name=res[1])

    @doc(description='Create a single Friend resource, which represents a friend relation between two users.', params={
        'username': {'description': 'The username of the sender (initiator) of the friend relation'},
        'friendname': {'description': 'The username of the receiver (target) of the friend relation'}
    })
    @marshal_with_flask_enforced(MicroservicesResponseSchema, code=200)
    def post(self, username: str, friendname: str):
        """The creation endpoint of a specific friend relation.

        :return: The success or error message
        """

        if username == friendname:
            return make_response_error(E_MSG.ERROR, "A user cannot add themselves as a friend", 400)

        require_user_exists(username)
        require_user_exists(friendname)

        # Duplicate username-friendname exception response is handled
        # by UniqueViolation error handler
        with conn.cursor() as curs:
            curs.execute('INSERT INTO friend ("username", "friendname") VALUES (%s, %s);', (username, friendname))
            conn.commit()

        return make_response_message(E_MSG.SUCCESS, 201)


def require_user_exists(username: str) -> None:
    """Require that the specified user exists according to
    the accounts microservice.

    Raise a DoesNotExist exception if the accounts microservice does
    not return the expected, positive response.

    :param username: The username of the user to check existence of
    """
    response = requests.get(f"http://accounts:5000/accounts/{username}")
    if response.status_code != 200:
        raise DoesNotExist(f"the user '{username}' does not exist")


@app.errorhandler(DoesNotExist)
def handle_does_not_exist(e):
    return get_404_does_not_exist(e, append_error=True)

@app.errorhandler(UniqueViolation)
def handle_db_unique_violation(e):
    conn.rollback()
    return get_409_already_exists(e)


# Add resources
api.add_resource(Friends, Friends.route())
api.add_resource(Friend, Friend.route())

# Register apispec docs
docs.register(Friends)
docs.register(Friend)

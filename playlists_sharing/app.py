from flask_apispec import MethodResource, doc
from psycopg2.errors import UniqueViolation, OperationalError, InterfaceError

from shared.utils import initialize_micro_service, marshal_with_flask_enforced
from shared.microserviceInteractions import require_user_exists, require_playlist_exists
from shared.exceptions import DoesNotExist, MicroserviceConnectionError, get_409_already_exists, get_404_does_not_exist, get_500_database_error, get_502_bad_gateway_error
from shared.APIResponses import GenericResponseMessages as E_MSG, make_response_error, make_response_message
from schemas import SharedPlaylistsResponseSchema, SharedPlaylistResponseSchema


MICROSERVICE_NAME = "playlists_sharing"
DB_HOST = "playlists_sharing_persistence"
APISPEC_CONFIG = {
    'APISPEC_SWAGGER_URL': '/swagger/',
    'APISPEC_SWAGGER_UI_URL': '/swagger-ui/',
    'APISPEC_TITLE': 'Microservices Playlists Sharing',
    'APISPEC_VERSION': '1.0'
}
app, api, docs, conn = initialize_micro_service(MICROSERVICE_NAME, DB_HOST, APISPEC_CONFIG)


class SharedPlaylists(MethodResource):
    """The api endpoint that represents a collection of Playlist resources shared with a recipient user.

    This resource collection does not support any project requirements directly,
    it ensures RESTfulness by making the URL hackable up the tree.
    """
    @staticmethod
    def route() -> str:
        """Get the route to the collection Playlist resources shared with a recipient user.

        :return: The route string
        """
        return "/playlists/<string:recipient>/shared"

    @doc(description='Get the collection of Playlist resources shared with a specified recipient user. This endpoint will attempt to query the playlists microservice to add additional, optional information to each playlist share in its response.', params={
        'recipient': {'description': 'The username of the recipient user to fetch the list of shared with playlists of'},
    })
    @marshal_with_flask_enforced(SharedPlaylistsResponseSchema, code=200)
    def get(self, recipient: str):
        """The query endpoint of the collection of shared Playlist resources for a recipient user.

        :return: The list of playlists shared with the recipient user
        """

        with conn.cursor() as curs:
            curs.execute("SELECT * FROM playlist_share WHERE recipient_username = %s;", (recipient,))
            result = []
            for recipient, playlist_id in curs.fetchall():
                # The basic, required data for the playlist
                # share microservice
                playlist_share_info = {
                        "recipient": recipient,
                        "id": playlist_id,
                }
                extend_share_information(playlist_share_info)
                result.append(playlist_share_info)

        return make_response_message(E_MSG.SUCCESS, 200, result=result)


class SharedPlaylist(MethodResource):
    """The api endpoint that represents a single Playlist resources shared with a recipient user.

    This resource supports the following project requirements
        7. sharing playlists with another user
    """
    @staticmethod
    def route() -> str:
        """Get the route to the Playlist resource sharing information with a recipient user.

        :return: The route string
        """
        return f"{SharedPlaylists.route()}/<int:playlist_id>"

    @doc(description='Get the sharing information for a Playlist resource with a specified recipient user. This endpoint will attempt to query the playlists microservice to add additional, optional information to its response.', params={
        'recipient': {'description': 'The username of the recipient user to fetch the specific playlist sharing information for'},
        'playlist_id': {'description': 'The unique identifier of the playlist to fetch the sharing information for'},
    })
    @marshal_with_flask_enforced(SharedPlaylistResponseSchema, code=200)
    def get(self, recipient: str, playlist_id: int):
        """The query endpoint of the single Playlist resource's sharing information for a specified recipient user.

        :return: The sharing information for the playlist and the recipient user
        """

        with conn.cursor() as curs:
            curs.execute("SELECT * FROM playlist_share WHERE recipient_username = %s AND playlist_id = %s;", (recipient, playlist_id))
            res = curs.fetchone()

            # DoesNotExist exception response is handled
            # by DoesNotExist error handler
            if res == None:
                raise DoesNotExist(f"no playlist with id '{playlist_id}' is shared with recipient '{recipient}'")

            playlist_share_info = {
                "recipient": res[0],
                "id": res[1]
            }
            extend_share_information(playlist_share_info)

        return make_response_message(E_MSG.SUCCESS, 200, **playlist_share_info)

    @doc(description='Share a Playlist resource with a specified recipient user.', params={
        'recipient': {'description': 'The username of the recipient user to share the specific playlist with'},
        'playlist_id': {'description': 'The unique identifier of the playlist to share'},
    })
    @marshal_with_flask_enforced(SharedPlaylistResponseSchema, code=200)
    def post(self, recipient: str, playlist_id: int):
        """The creation endpoint of the single Playlist resource's sharing information for a specified recipient user.

        :return: The created sharing information for the playlist and the recipient user
        """

        require_user_exists(recipient)
        response = require_playlist_exists(playlist_id)

        if response is not None:
            playlist = response.json()
            if playlist.get("owner", None) == recipient:
                return make_response_error(E_MSG.ERROR, "You cannot share a playlist with yourself", 400)

        with conn.cursor() as curs:
            curs.execute('INSERT INTO playlist_share ("recipient_username", "playlist_id") VALUES (%s, %s);', (recipient, playlist_id))
            conn.commit()

            curs.execute('SELECT * FROM playlist_share WHERE recipient_username = %s AND playlist_id = %s;', (recipient, playlist_id))
            res = curs.fetchone()

            # Echo back playlist share meta info to caller,
            if res is None:
                return make_response_error(E_MSG.ERROR, f"Failed to share playlist with id '{playlist_id}' with recipient '{recipient}'", 500)

        return make_response_message(E_MSG.SUCCESS, 200, recipient=res[0], id=res[1])


def extend_share_information(share_information: dict) -> None:
    """Attempt to fetch detailed playlist properties to enrich the playlist share response.

    The *share_information* MUST contain a 'id' key that maps to the
    playlist id to query the playlists API for.

    The playlists microservice is queried for the detailed playlist
    information needed to enrich the response. In case no valid,
    successful reply is received, the basic share information does
    not get updated.

    This function catches all errors emitted during the querying of
    the playlist microservice.

    :param share_information: The basic share information to update
    """
    assert "id" in share_information, "The basic share information should contain the playlist id"

    try:
        playlist_id = share_information["id"]
        response = require_playlist_exists(playlist_id)
        if response is None:
            return
        response_json = response.json()
        share_information.update({
            "title": response_json.get("title", "")
        })
    except (DoesNotExist, MicroserviceConnectionError):
        pass


@app.errorhandler(DoesNotExist)
def handle_does_not_exist(e):
    return get_404_does_not_exist(e, append_error=True)

@app.errorhandler(UniqueViolation)
def handle_db_unique_violation(e):
    conn.rollback()
    return get_409_already_exists(e)

@app.errorhandler(InterfaceError)
@app.errorhandler(OperationalError)
def handle_db_operational_error(e):
    """An error handler for notifying the caller that
    an exception occurred during database access.

    Possible causes include: the persistence (db) container
    being down, or errors during calls to the database.
    """
    return get_500_database_error(e)

@app.errorhandler(MicroserviceConnectionError)
def handle_db_connection_error(e):
    """An error handler for notifying the caller that
    an exception occurred during connection to another
    microservice.

    Possible causes include: the target microservice
    container being down
    """
    return get_502_bad_gateway_error(e, append_error=True)


# Add resources
api.add_resource(SharedPlaylists, SharedPlaylists.route())
api.add_resource(SharedPlaylist, SharedPlaylist.route())

# Register apispec docs
docs.register(SharedPlaylists)
docs.register(SharedPlaylist)

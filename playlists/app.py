from flask_apispec import MethodResource, doc, use_kwargs
from psycopg2.errors import UniqueViolation, OperationalError, InterfaceError

from shared.utils import initialize_micro_service, marshal_with_flask_enforced
from shared.microserviceInteractions import require_user_exists, require_song_exists
from shared.exceptions import DoesNotExist, MicroserviceConnectionError, get_409_already_exists, get_404_does_not_exist, get_500_database_error, get_502_bad_gateway_error
from shared.APIResponses import GenericResponseMessages as E_MSG, make_response_error, make_response_message
from schemas import MicroservicesResponseSchema, PlaylistResponseSchema, PlaylistsResponseSchema, PlaylistSongBodySchema, PlaylistMetaResponseSchema, PlaylistMetaBodySchema


MICROSERVICE_NAME = "playlists"
DB_HOST = "playlists_persistence"
APISPEC_CONFIG = {
    'APISPEC_SWAGGER_URL': '/swagger/',
    'APISPEC_SWAGGER_UI_URL': '/swagger-ui/',
    'APISPEC_TITLE': 'Microservices Playlists',
    'APISPEC_VERSION': '1.0'
}
app, api, docs, conn = initialize_micro_service(MICROSERVICE_NAME, DB_HOST, APISPEC_CONFIG)


class Playlists(MethodResource):
    """The api endpoint that represents a collection of Playlist resources for the chosen user.

    This resource supports the following project requirements
        5. creating playlists
    """
    @staticmethod
    def route() -> str:
        """Get the route to the collection of a user's Playlist resources.

        :return: The route string
        """
        return "/playlists/<string:username>"

    @doc(description='Get the collection of Playlist resources of the specified user.', params={
        'username': {'description': 'The username to fetch the list of playlists of'},
    })
    @marshal_with_flask_enforced(PlaylistsResponseSchema, code=200)
    def get(self, username: str):
        """The query endpoint of the collection of Playlist resource for a user.

        :return: The list of the user's playlists
        """

        with conn.cursor() as curs:
            curs.execute("SELECT * FROM playlist WHERE owner_username = %s;", (username,))
            res = [
                {
                    "id": playlist[0],
                    "owner": playlist[1],
                    "title": playlist[2]
                }
                for playlist in curs.fetchall()
            ]

        return make_response_message(E_MSG.SUCCESS, 200, result=res)

    @doc(description='Create a new, empty Playlist resource.', params={
        'username': {'description': 'The username of the owner of the new playlist'},
        'title': {'description': 'The user-designated title of the new playlist'}
    })
    @use_kwargs(PlaylistMetaBodySchema, location='form')
    @marshal_with_flask_enforced(PlaylistMetaResponseSchema, code=200)
    def post(self, username: str, **kwargs):
        """The creation endpoint of a new Playlist resource.

        :return: The created playlist's meta information
        """

        title: str = kwargs["title"]

        require_user_exists(username)

        # Duplicate username-title exception response is handled
        # by UniqueViolation error handler
        with conn.cursor() as curs:
            curs.execute('INSERT INTO playlist ("id", "owner_username", "title") VALUES (DEFAULT, %s, %s);', (username, title))
            conn.commit()

            curs.execute('SELECT * FROM playlist WHERE owner_username = %s AND title = %s;', (username, title))
            res = curs.fetchone()

            # Echo back playlist meta info to caller,
            # plus the playlist id
            if res is None:
                return make_response_error(E_MSG.ERROR, f"Failed to create new playlist named '{title}' for user '{username}'", 500)

        return make_response_message(E_MSG.SUCCESS, 201, id=res[0], owner=res[1], title=res[2])


class Playlist(MethodResource):
    """The api endpoint that represents a single existing Playlist resource.

    Note that while a playlist stores additional information related to
    the playlist itself, it also acts as a collection of simplified Song resources.

    This resource supports the following project requirements
        6. add a song to a playlist
        7. viewing all songs in a playlist
    """
    @staticmethod
    def route() -> str:
        """Get the route to the Playlist resource.

        :return: The route string
        """
        return f"/playlists/<int:playlist_id>"

    @doc(description='Get a single Playlist resource, which represents a playlist of songs added by a user.', params={
        'playlist_id': {'description': 'The unique identifier of the playlist'},
    })
    @marshal_with_flask_enforced(PlaylistResponseSchema, code=200)
    def get(self, playlist_id: int):
        """The query endpoint of a specific playlist.

        :return: The specified playlist
        """

        with conn.cursor() as curs:
            curs.execute("SELECT * FROM playlist WHERE id = %s;", (playlist_id,))
            res = curs.fetchone()

            # DoesNotExist exception response is handled
            # by DoesNotExist error handler
            if res == None:
                raise DoesNotExist(f"no playlist with id '{playlist_id}' exists")

            playlist_id, playlist_owner, playlist_title = res

            curs.execute("SELECT * FROM playlist_song WHERE playlist_id = %s;", (playlist_id,))
            res = [
                {
                    "artist": playlist_song[1],
                    "title": playlist_song[2]
                }
                for playlist_song in curs.fetchall()
            ]

        return make_response_message(E_MSG.SUCCESS, 200, id=playlist_id, owner=playlist_owner,
                                     title=playlist_title, result=res)

    @doc(description='Update a Playlist resource\'s songs with a new song. Any songs already part of the playlist are silently ignored.', params={
        'artist': {'description': 'The artist of the song to add to the playlist', 'location': 'form'},
        'title': {'description': 'The title of the song to add to the playlist', 'location': 'form'},
    })
    @use_kwargs(PlaylistSongBodySchema, location='form')
    @marshal_with_flask_enforced(MicroservicesResponseSchema, code=200)
    def put(self, playlist_id: int, **kwargs):
        """The update endpoint of a specific Playlist resource's contents.

        :return: The success or error message
        """

        song_artist = kwargs["artist"]
        song_title = kwargs["title"]

        require_song_exists(artist=song_artist, title=song_title)

        # Duplicate username-title exception response is handled
        # by UniqueViolation error handler
        with conn.cursor() as curs:
            curs.execute("SELECT id from playlist WHERE id = %s", (playlist_id,))
            res = curs.fetchone()

            # DoesNotExist exception response is handled
            # by DoesNotExist error handler
            if res == None:
                raise DoesNotExist(f"no playlist with id '{playlist_id}' exists")

            playlist_id, = res

            # Silenty ignore unique violations, to satisfy the idempotency of PUT
            curs.execute('INSERT INTO playlist_song ("playlist_id", "song_artist", "song_title") VALUES (%s, %s, %s) ON CONFLICT DO NOTHING;', (playlist_id, song_artist, song_title))
            conn.commit()

        return make_response_message(E_MSG.SUCCESS, 201)


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
api.add_resource(Playlists, Playlists.route())
api.add_resource(Playlist, Playlist.route())

# Register apispec docs
docs.register(Playlists)
docs.register(Playlist)

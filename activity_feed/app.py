import requests

from typing import List, Tuple
from datetime import datetime
from flask_apispec import MethodResource, doc, use_kwargs

from shared.utils import initialize_micro_service, marshal_with_flask_enforced
from shared.microserviceInteractions import require_user_exists
from shared.exceptions import DoesNotExist, MicroserviceConnectionError, get_409_already_exists, get_404_does_not_exist, get_500_database_error, get_502_bad_gateway_error
from shared.APIResponses import GenericResponseMessages as E_MSG, make_response_error, make_response_message
from schemas import MicroservicesResponseSchema, ActivityFeedResponseSchema, ActivityFeedBodySchema


MICROSERVICE_NAME = "activity_feed"
DB_HOST = None
APISPEC_CONFIG = {
    'APISPEC_SWAGGER_URL': '/swagger/',
    'APISPEC_SWAGGER_UI_URL': '/swagger-ui/',
    'APISPEC_TITLE': 'Microservices Activity Feed',
    'APISPEC_VERSION': '1.0'
}
app, api, docs, conn = initialize_micro_service(MICROSERVICE_NAME, DB_HOST, APISPEC_CONFIG)

class ActivityFeed(MethodResource):
    """The api endpoint that represents a single activity feed resource.

    This resource supports the following project requirements
        9. fetching a user's activity feed
    """
    @staticmethod
    def route() -> str:
        """Get the route to the Account resource.

        :return: The route string
        """
        return "/feeds/<string:username>"

    @doc(description='Get a single ActivityFeed resource, which represents a feed of the N most recent activities of all friends of the specified user\'s account.', params={
        'username': {'description': 'The username of the chosen account'}
    })
    @use_kwargs(ActivityFeedBodySchema, location='query')
    @marshal_with_flask_enforced(ActivityFeedResponseSchema, code=200)
    def get(self, username: str, **kwargs):
        """The query endpoint of the activity feed of a specific account.

        :return: The activity feed
        """
        amount = int(kwargs["amount"])

        require_user_exists(username)

        # (date, title, desciption)
        activity_feed: List[Tuple[datetime, str, str]] = []
        def filtered_activity_feed():
            return sorted(activity_feed, key=lambda activity: activity[0])[:amount]

        # Fetch all friends of the user for which to construct the feed
        friends_names: list = []  # A list of all the user's friends
        try:
            response = requests.get(f"http://friends:5000/friends/{username}?amount={amount}")
            if response.status_code == 200:
                friends_names = [
                    friend_name
                    for friend_info in response.json().get("result", list())
                    if (friend_name := friend_info.get("friend_name", None)) is not None
                ]

        # Explicitly set output values, to ensure graceful failure is handled appropriately
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
            friends_names = []

        # Call playlists API
        playlists: list = []
        for friend_name in friends_names:

            # Fetch friend's playlists
            try:
                response = requests.get(f"http://playlists:5000/playlists/{friend_name}?amount{amount}")
                if response.status_code == 200:
                    for playlist_id in response.json().get("result", list()):

                        # Skip malformed
                        if "id" not in playlist_id or "title" not in playlist_id:
                            continue

                        playlists.append((playlist_id["id"], playlist_id["title"]))
                        activity_feed.append((
                            playlist_id["created"],
                            f"Playlist created",
                            f"{friend_name} created a playlist called {playlist_id['title']}")
                        )

                    activity_feed = filtered_activity_feed()

            # Explicitly set output values, to ensure graceful failure is handled appropriately
            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
                playlists = []

            # Update the intermediary activity feed with song additions to playlists
            for playlist_id, playlist_title in playlists:
                # Fetch friend's playlist's songs
                try:
                    response = requests.get(f"http://playlists:5000/playlists/{playlist_id}?amount={amount}")
                    if response.status_code == 200:
                        activity_feed.extend([
                            (
                                playlist_song["created"],
                                f"Song added to playlist",
                                f"{friend_name} added the song {playlist_song['title']} by {playlist_song['artist']} to their playlist called {playlist_title}"
                            )
                            for playlist_song in response.json().get("result", list())
                            if "artist" in playlist_song and "title" in playlist_song
                        ])
                        activity_feed = filtered_activity_feed()

                # Explicitly set output values, to ensure graceful failure is handled appropriately
                except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
                    playlists = []

            # Call playlists sharing API
            # TODO
            # TODO
            # TODO
            # TODO

        # Format results for output
        res = [
            {
                "date": date,
                "description": description,
                "title": title,
            }
            for date, title, description in activity_feed
        ]

        return make_response_message(E_MSG.SUCCESS, 200, result=res)


@app.errorhandler(DoesNotExist)
def handle_does_not_exist(e):
    return get_404_does_not_exist(e, append_error=True)

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
api.add_resource(ActivityFeed, ActivityFeed.route())

# Register apispec docs
docs.register(ActivityFeed)
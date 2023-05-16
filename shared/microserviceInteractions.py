import requests

from typing import Union

from shared.exceptions import MicroserviceConnectionError, DoesNotExist


def require_user_exists(username: str) -> Union[requests.Response, None]:
    """Require that the specified user exists according to
    the accounts microservice.

    Raise a DoesNotExist exception if the accounts microservice does
    not return the expected, positive response.
    Raise a MicroserviceConnectionError exception if connection to the
    accounts microservice cannot be established.

    :param username: The username of the user to check existence of
    :return: The microservice response if no exception
    """
    try:
        response = requests.get(f"http://accounts:5000/accounts/{username}")
        if response.status_code != 200:
            raise DoesNotExist(f"the user '{username}' does not exist")

        return response
    # Explicitly set output values, to ensure graceful failure is handled appropriately
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
        raise MicroserviceConnectionError("could not reach the accounts microservice")

def require_song_exists(artist: str, title: str) -> Union[requests.Response, None]:
    """Require that the specified song exists according to
    the songs microservice.

    Raise a DoesNotExist exception if the songs microservice does
    not return the expected, positive response.
    Raise a MicroserviceConnectionError exception if connection to the
    songs microservice cannot be established.

    :param artist: The artist of the song to check existence of
    :param title: The title of the song to check existence of
    :return: The microservice response if no exception
    """
    try:
        response = requests.get(f"http://songs:5000/songs/exist?artist={artist}&title={title}")
        if response.status_code != 200 or not response.json():
            raise DoesNotExist(f"the song with artist '{artist}' and title '{title}' does not exist")

        return response
    # Explicitly set output values, to ensure graceful failure is handled appropriately
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
        raise MicroserviceConnectionError("could not reach the songs microservice")


def require_playlist_exists(playlist_id: int) -> Union[requests.Response, None]:
    """Require that the specified playlist exists according to
    the playlists microservice.

    Raise a DoesNotExist exception if the playlists microservice does
    not return the expected, positive response.
    Raise a MicroserviceConnectionError exception if connection to the
    playlists microservice cannot be established.

    :param playlist_id: The unique identifier of the playlist to check existence of
    :return: The microservice response if no exception
    """
    try:
        response = requests.get(f"http://playlists:5000/playlists/{playlist_id}")
        if response.status_code != 200:
            raise DoesNotExist(f"the playlist with id '{playlist_id}' does not exist")

        return response
    # Explicitly set output values, to ensure graceful failure is handled appropriately
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
        raise MicroserviceConnectionError("could not reach the playlists microservice")


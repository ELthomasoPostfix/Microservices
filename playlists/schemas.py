from copy import deepcopy
from marshmallow import Schema, fields

from shared.schemas import MicroservicesResponseSchema, MicroservicesResultSchema


class PlaylistSongSchema(Schema):
    """A song resource's information, as stored by a playlist"""
    artist = fields.String(required=True, metadata={
        'description': 'The artist of a song part of a playlist',
    })
    title = fields.String(required=True, metadata={
        'description': 'The title of a song part of a playlist',
    })


class PlaylistSongBodySchema(Schema):
    """A song resource's information, as stored by a playlist,
    provided in a form body to be added to a playlist
    """
    artist = fields.String(required=True, location='form', metadata={
        'description': 'The artist of a song to add to a playlist',
    })
    song_title = fields.String(required=True, location='form', metadata={
        'description': 'The title of a song to add to a playlist',
    })


class PlaylistSchema(Schema):
    """The Playlist resource's playlist specific information"""
    id = fields.Integer(required=True, metadata={
        'description': 'The unique identifier of the playlist',
    })
    owner = fields.String(required=True, metadata={
        'description': 'The username of the user that owns the playlist',
    })
    title = fields.String(required=True, metadata={
        'description': 'The user-designated title of the playlist',
    })


class PlaylistsResponseSchema(MicroservicesResultSchema):
    """The output format of the Playlist resource endpoint"""
    result = fields.List(fields.Nested(PlaylistSchema), required=True, default=[], metadata={
        'description': 'The list of playlists of a user',
    })


class PlaylistResponseSchema(MicroservicesResultSchema, PlaylistSchema):
    """The output format of the Playlist resource endpoint"""
    result = fields.List(fields.Nested(PlaylistSongSchema), required=True, default=[], metadata={
        'description': 'The list of songs part of the playlist',
    })

from marshmallow import Schema, fields, validate

from shared.schemas import MicroservicesResponseSchema, MicroservicesResultSchema


class SharedPlaylistSchema(Schema):
    """The Playlist resource's sharing information"""
    id = fields.Integer(required=True, metadata={
        'description': 'The unique identifier of the playlist',
    })
    recipient = fields.String(required=True, metadata={
        'description': 'The username of the recipient user of the playlist sharing action',
    })
    owner = fields.String(required=True, metadata={
        'description': 'The username of the owner user of the playlist that is shared',
    })
    created = fields.DateTime(format="iso", required=True, metadata={
        'description': 'The ISO8601 date time at which the playlist was shared'
    })


class SharedPlaylistExtendedSchema(SharedPlaylistSchema):
    """Detailed shared Playlist resource properties that are fetched.

    The playlist sharing microservice can attempt to extend the basic
    sharing information it provides to include detailed playlist info.
    """
    title = fields.String(required=False, default="N/A", metadata={
        'description': 'The user-designated title of the playlist',
    })
    playlist_created = fields.DateTime(format="iso", required=False, metadata={
        'description': 'The ISO8601 date time at which the playlist was created'
    })


class SharedPlaylistResponseSchema(MicroservicesResponseSchema, SharedPlaylistExtendedSchema):
    """The output format of the Playlist resource sharing endpoint"""
    pass



class SharedPlaylistsResponseSchema(MicroservicesResultSchema):
    """The output format of the Playlist resource sharing collection endpoint"""
    result = fields.List(fields.Nested(SharedPlaylistExtendedSchema), required=True, default=[], metadata={
        'description': 'The list of playlists shared with a recipient user',
    })


class SharedPlaylistQuerySchema(Schema):
    usernameIdentity = fields.String(required=True, location='query', metadata={
        'description': 'The party/identity of the playlist share relation that the username parameter refers to.',
    }, validate=validate.OneOf(['owner', 'recipient']))

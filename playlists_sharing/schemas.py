from marshmallow import Schema, fields

from shared.schemas import MicroservicesResponseSchema, MicroservicesResultSchema

class SharedPlaylistSchema(Schema):
    """The Playlist resource's sharing information"""
    id = fields.Integer(required=True, metadata={
        'description': 'The unique identifier of the playlist',
    })
    recipient = fields.String(required=True, metadata={
        'description': 'The username of the recipient user of the playlist sharing action',
    })


class SharedPlaylistExtendedSchema(SharedPlaylistSchema):
    """Detailed shared Playlist resource properties that are fetched.

    The playlist sharing microservice can attempt to extend the basic
    sharing information it provides to include detailed playlist info.
    """
    title = fields.String(required=False, default="N/A", metadata={
        'description': 'The user-designated title of the playlist',
    })


class SharedPlaylistResponseSchema(MicroservicesResponseSchema, SharedPlaylistExtendedSchema):
    """The output format of the Playlist resource sharing endpoint"""
    pass



class SharedPlaylistsResponseSchema(MicroservicesResultSchema):
    """The output format of the Playlist resource sharing collection endpoint"""
    result = fields.List(fields.Nested(SharedPlaylistExtendedSchema), required=True, default=[], metadata={
        'description': 'The list of playlists shared with a recipient user',
    })

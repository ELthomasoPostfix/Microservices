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


class SharedPlaylistResponseSchema(MicroservicesResponseSchema, SharedPlaylistSchema):
    """The output format of the Playlist resource sharing endpoint"""
    pass



class SharedPlaylistsResponseSchema(MicroservicesResultSchema):
    """The output format of the Playlist resource sharing collection endpoint"""
    result = fields.List(fields.Nested(SharedPlaylistSchema), required=True, default=[], metadata={
        'description': 'The list of playlists shared with a recipient user',
    })

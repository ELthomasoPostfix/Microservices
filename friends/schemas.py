from marshmallow import Schema, fields

from shared.schemas import MicroservicesResponseSchema, MicroservicesResultSchema


class FriendSchema(Schema):
    """The Friend relation resource information"""
    friend_name = fields.String(required=True, metadata={
        'description': 'The username of the friend/receiver (target) of the friend relation',
    })


class FriendResponseSchema(MicroservicesResponseSchema, FriendSchema):
    """The output format of the Friend resource endpoint"""
    pass


class FriendsResponseSchema(MicroservicesResultSchema):
    """The output format of the Friend resource collection endpoint"""
    result = fields.List(fields.Nested(FriendSchema), required=True, default=[], metadata={
        'description': 'The friend list of a user; the list of all friend relations information of a user',
    })

from marshmallow import Schema, fields

from shared.schemas import MicroservicesResponseSchema, MicroservicesResultSchema


class ActivityFeedBodySchema(Schema):
    amount = fields.String(required=True, location='query', metadata={
        'description': 'The amount of activities to include in the output',
    })


class ActivitySchema(Schema):
    title = fields.String(required=True, metadata={
        'description': 'The title of the activity; a short name for the type of the activity',
    })
    description = fields.String(required=True, metadata={
        'description': 'The description of the activity; a brief description of the specific contents of the activity',
    })
    date = fields.String(required=True, metadata={
        'description': 'The date of the activity; the datetime when the activity took place',
    })


class ActivityFeedResponseSchema(MicroservicesResultSchema):
    """The output format of the ActivityFeed resource endpoint"""
    result = fields.List(fields.Nested(ActivitySchema), required=True, default=[], metadata={
        'description': 'The list of N activities of a specified user\'s friends',
    })

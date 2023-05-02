from marshmallow import Schema, fields


class MicroservicesResponseSchema(Schema):
    message = fields.String(required=True, default='default message', metadata={
        'description': 'The response of the API that can be displayed to non-technical users of a consumer application of the API',
    })
    error= fields.String(required=False, metadata={
        'description': 'An optional, technical error message',
    })

class MicroservicesResultSchema(MicroservicesResponseSchema):
    result = fields.List(fields.Raw, required=True, default=[], metadata={
        'description': 'A generic list of results',
    })
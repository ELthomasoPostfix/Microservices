from marshmallow import fields

from shared.schemas import MicroservicesResponseSchema, MicroservicesResultSchema


class AccountSchema(MicroservicesResponseSchema):
    id = fields.Integer(required=True, metadata={
        'description': 'The unique identifier of the user',
    }, strict=True)
    username = fields.String(required=True, metadata={
        'description': 'The username of the user',
    }, strict=True)


class AccountsSchema(MicroservicesResultSchema):
    result = fields.List(fields.Nested(AccountSchema), required=True, default=[], metadata={
        'description': 'A list of Movie resources',
    })

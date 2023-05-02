from marshmallow import Schema, fields

from shared.schemas import MicroservicesResponseSchema, MicroservicesResultSchema


class AccountSchema(Schema):
    """The primary account information"""
    id = fields.Integer(required=True, metadata={
        'description': 'The unique identifier of the user',
    })
    username = fields.String(required=True, metadata={
        'description': 'The username of the user',
    })


class AccountResponseSchema(MicroservicesResponseSchema, AccountSchema):
    """The output format of the Account resource endpoint"""
    pass


class AccountsSchema(MicroservicesResultSchema):
    result = fields.List(fields.Nested(AccountSchema), required=True, default=[], metadata={
        'description': 'A list of Movie resources',
    })


class RegisterBodySchema(Schema):
    """The form body of an account registration"""
    password = fields.String(required=True, location='form', metadata={
        'description': 'The password to register the account with'
    })

from marshmallow import Schema, fields

from shared.schemas import MicroservicesResponseSchema, MicroservicesResultSchema


class AccountSchema(Schema):
    """The primary account information"""
    username = fields.String(required=True, metadata={
        'description': 'The username of the user',
    })


class AccountResponseSchema(MicroservicesResponseSchema, AccountSchema):
    """The output format of the Account resource endpoint"""
    pass


class RegisterBodySchema(Schema):
    """The form body of an account registration"""
    password = fields.String(required=True, location='form', metadata={
        'description': 'The password to register the account with'
    })


class AuthenticationBodySchema(Schema):
    """The form body of an account authentication"""
    password = fields.String(required=True, location='form', metadata={
        'description': 'The password to authenticate the account with'
    })


class AuthenticationResponseSchema(MicroservicesResponseSchema):
    """The output format of the Authentication resource endpoint"""
    authentication_data = fields.Boolean(required=True, metadata={
        'description': 'The proof of authentication'
    })

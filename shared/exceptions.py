from flask import Response

from .utils import make_response_error
from .APIResponses import GenericResponseMessages as E_MSG


def get_409_already_exists(e) -> Response:
    return make_response_error(E_MSG.ERROR, AlreadyExists.description, AlreadyExists.code)

def get_404_does_not_exist(e) -> Response:
    return make_response_error(E_MSG.ERROR, DoesNotExist.description, DoesNotExist.code)


class DatabaseError(Exception):
    """An error occurred within a Microservice database."""
    pass


class AlreadyExists(DatabaseError):
    """A resource cannot be created because it already exists."""
    code = 409
    description = "This resource already exists"


class DoesNotExist(DatabaseError):
    """A resource cannot be fetched because it does not exist."""
    code = 404
    description = "This resource does not exist"

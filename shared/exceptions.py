from typing import Union
from flask import Response

from .utils import make_response_error
from .APIResponses import GenericResponseMessages as E_MSG


class DatabaseError(Exception):
    """An error occurred within a Microservice database."""
    code = 500
    description = "Something went wrong on our side"


class AlreadyExists(DatabaseError):
    """A resource cannot be created because it already exists."""
    code = 409
    description = "This resource already exists"


class DoesNotExist(DatabaseError):
    """A resource cannot be fetched because it does not exist."""
    code = 404
    description = "This resource does not exist"


class AuthenticationError(Exception):
    """An error occurred concerning user authentication."""
    code = 401
    description = "Authentication failed"


def get_409_already_exists(e: Union[AlreadyExists, str], append_error: bool=False, **kwargs) -> Response:
    """Make a `flask.Response` based on the AlreadyExists exception class
    
    :param e: The error to stringify and append to the error message, if append_error is True
    :param append_error: Whether to append the exception string to the error message
    :return: A `flask.Response` with error messages and the provided kwargs
    """
    error_msg: str = AlreadyExists.description
    if append_error:
        error_msg += ", " + str(e)
    return make_response_error(E_MSG.ERROR, error_msg, AlreadyExists.code, **kwargs)

def get_404_does_not_exist(e: Union[DoesNotExist, str], append_error: bool=False, **kwargs) -> Response:
    """Make a `flask.Response` based on the DoesNotExist exception class
    
    :param e: The error to stringify and append to the error message, if append_error is True
    :param append_error: Whether to append the exception string to the error message
    :return: A `flask.Response` with error messages and the provided kwargs
    """
    error_msg: str = DoesNotExist.description
    if append_error:
        error_msg += ", " + str(e)
    return make_response_error(E_MSG.ERROR, error_msg, DoesNotExist.code, **kwargs)

def get_401_authentication_error(e: Union[AuthenticationError, str], append_error: bool=False, **kwargs) -> Response:
    """Make a `flask.Response` based on the AuthenticationError exception class
    
    :param e: The error to stringify and append to the error message, if append_error is True
    :param append_error: Whether to append the exception string to the error message
    :return: A `flask.Response` with error messages and the provided kwargs
    """
    error_msg: str = AuthenticationError.description
    if append_error:
        error_msg += ", " + str(e)
    return make_response_error(E_MSG.ERROR, error_msg, AuthenticationError.code, **kwargs)

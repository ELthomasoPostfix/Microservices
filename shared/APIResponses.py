from flask import make_response, Response


class GenericResponseMessages:
    """A class of constants used to construct response messages."""
    SUCCESS    = "Success"
    ERROR      = "Something went wrong"
    UNEXPECTED = "Encountered an unexpected exception"
    MALFORMED_REQ = "Malformed request"

def make_response_message(message: str, status_code: int, **kwargs) -> Response:
    """A simple wrapper for the Flask make_response function with
    a message key in the json body content. ::

        >>> response = make_response_message("Success", 200)
        >>> response.json
        {
            "message": "Success"
        }

        >>> response = make_response_message("Success", 200, result={ "name" : "Bob", "age": 31 })
        >>> response.json
        {
            "message": "Success"
            "result": {
                "age": 31,
                "name": "Bob"
            }
        }

    :param message: The json body `message` key's value
    :param status_code: The response status code
    :return: The flask response of the form
        {
            "message": *message*
        }
    """
    return make_response(Message(message=message, **kwargs), status_code)

def make_response_error(message: str, error_message: str, status_code: int, **kwargs) -> Response:
    """A simple wrapper for the Flask make_response function with
    message and error keys in the json body content. ::

        >>> response = make_response_error("Error", "Not implemented", 501)
        >>> response.json
        {
            "message": "Error",
            "error": "Not implemented"
        }

        >>> response = make_response_error("Error", "Not implemented", 501, redirect="https://www.example.com")
        >>> response.json
        {
            "message": "Error",
            "error": "Not implemented",
            "redirect: "https://www.example.com"
        }

    :param message: The json body `message` key's value
    :param error_message: The json body `error` key's value
    :param status_code: The response status code
    :return: The flask response of the form
        {
            "message": *message*,
            "error": *error*
        }
    """
    return make_response(Error(message=message, error_message=error_message, **kwargs), status_code)


class Message(dict):
    """Used as a shortened syntax to pass responses containing
    a message key from the API endpoints.
    """
    def __init__(self, message: str, **kwargs):
        self.__setitem__("message", message)
        super().__init__(kwargs)


class Error(Message):
    """Used as a shortened syntax to pass responses containing
    message and error keys from the API endpoints.
    """
    def __init__(self, message: str, error_message: str, **kwargs):
        super().__init__(message=message, **kwargs)
        self.__setitem__("error", error_message)

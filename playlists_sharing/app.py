from flask_apispec import MethodResource, doc, use_kwargs
from psycopg2.errors import UniqueViolation, OperationalError, InterfaceError

from shared.utils import initialize_micro_service, marshal_with_flask_enforced
from shared.microserviceInteractions import require_user_exists, require_song_exists
from shared.exceptions import DoesNotExist, MicroserviceConnectionError, get_409_already_exists, get_404_does_not_exist, get_500_database_error, get_502_bad_gateway_error
from shared.APIResponses import GenericResponseMessages as E_MSG, make_response_error, make_response_message
from schemas import MicroservicesResponseSchema


MICROSERVICE_NAME = "playlists_sharing"
DB_HOST = "playlists_sharing_persistence"
APISPEC_CONFIG = {
    'APISPEC_SWAGGER_URL': '/swagger/',
    'APISPEC_SWAGGER_UI_URL': '/swagger-ui/',
    'APISPEC_TITLE': 'Microservices Playlists Sharing',
    'APISPEC_VERSION': '1.0'
}
app, api, docs, conn = initialize_micro_service(MICROSERVICE_NAME, DB_HOST, APISPEC_CONFIG)



@app.errorhandler(DoesNotExist)
def handle_does_not_exist(e):
    return get_404_does_not_exist(e, append_error=True)

@app.errorhandler(UniqueViolation)
def handle_db_unique_violation(e):
    conn.rollback()
    return get_409_already_exists(e)

@app.errorhandler(InterfaceError)
@app.errorhandler(OperationalError)
def handle_db_operational_error(e):
    """An error handler for notifying the caller that
    an exception occurred during database access.

    Possible causes include: the persistence (db) container
    being down, or errors during calls to the database.
    """
    return get_500_database_error(e)

@app.errorhandler(MicroserviceConnectionError)
def handle_db_connection_error(e):
    """An error handler for notifying the caller that
    an exception occurred during connection to another
    microservice.

    Possible causes include: the target microservice
    container being down
    """
    return get_502_bad_gateway_error(e, append_error=True)

from shared.utils import initialize_micro_service


MICROSERVICE_NAME = "accounts"
DB_HOST = "accounts_persistence"
app, api, conn = initialize_micro_service(MICROSERVICE_NAME, DB_HOST)
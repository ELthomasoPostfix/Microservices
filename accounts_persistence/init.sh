#!/bin/bash

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE DATABASE accounts;

EOSQL

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "accounts" <<-EOSQL
    CREATE TABLE account(
        username TEXT PRIMARY KEY,
        password TEXT NOT NULL
    );
EOSQL

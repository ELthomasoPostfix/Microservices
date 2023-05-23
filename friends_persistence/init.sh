#!/bin/bash

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE DATABASE friends;

EOSQL

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "friends" <<-EOSQL
    CREATE TABLE friend (
        username TEXT NOT NULL,
        friendname TEXT NOT NULL,
        created_datetime TIMESTAMP NOT NULL DEFAULT now(),
        UNIQUE (username, friendname)
    );
EOSQL

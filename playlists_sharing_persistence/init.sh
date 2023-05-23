#!/bin/bash

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE DATABASE playlists_sharing;

EOSQL

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "playlists_sharing" <<-EOSQL
    CREATE TABLE playlist_share (
        recipient_username TEXT NOT NULL,
        playlist_id INTEGER,
        owner_username TEXT NOT NULL,
        created_datetime TIMESTAMP NOT NULL DEFAULT now(),
        PRIMARY KEY (recipient_username, playlist_id)
    );
EOSQL

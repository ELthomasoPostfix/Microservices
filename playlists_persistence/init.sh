#!/bin/bash

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE DATABASE playlists;

EOSQL

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "playlists" <<-EOSQL
    CREATE TABLE playlist (
        id SERIAL PRIMARY KEY,
        owner_username TEXT NOT NULL,
        title TEXT NOT NULL,
        created_datetime TIMESTAMP NOT NULL DEFAULT now(),
        UNIQUE (owner_username, title)
    );

    CREATE TABLE playlist_song (
        playlist_id SERIAL,
        song_artist TEXT NOT NULL,
        song_title TEXT NOT NULL,
        created_datetime TIMESTAMP NOT NULL DEFAULT now(),
        FOREIGN KEY (playlist_id) REFERENCES playlist(id) ON DELETE CASCADE,
        UNIQUE (playlist_id, song_artist, song_title)
    );
EOSQL

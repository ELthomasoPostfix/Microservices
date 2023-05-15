# syntax=docker/dockerfile:1
FROM python:3.8-slim-buster

# Do microservice specific setup
RUN python3 -m venv venv
RUN . venv/bin/activate
COPY playlists/requirements.txt playlists/requirements.txt
RUN pip3 install -r playlists/requirements.txt

COPY playlists/app.py playlists/app.py
COPY playlists/schemas.py playlists/schemas.py

CMD [ "python3", "-m" , "flask", "--app", "playlists/app.py", "run", "--host=0.0.0.0"]

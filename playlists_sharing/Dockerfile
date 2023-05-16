# syntax=docker/dockerfile:1
FROM python:3.8-slim-buster

# Do microservice specific setup
RUN python3 -m venv venv
RUN . venv/bin/activate
COPY playlists_sharing/requirements.txt playlists_sharing/requirements.txt
RUN pip3 install -r playlists_sharing/requirements.txt

COPY playlists_sharing/app.py playlists_sharing/app.py
COPY playlists_sharing/schemas.py playlists_sharing/schemas.py

CMD [ "python3", "-m" , "flask", "--app", "playlists_sharing/app.py", "run", "--host=0.0.0.0"]

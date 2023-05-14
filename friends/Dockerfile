# syntax=docker/dockerfile:1
FROM python:3.8-slim-buster

# Do microservice specific setup
RUN python3 -m venv venv
RUN . venv/bin/activate
COPY friends/requirements.txt friends/requirements.txt
RUN pip3 install -r friends/requirements.txt

COPY friends/app.py friends/app.py
COPY friends/schemas.py friends/schemas.py

CMD [ "python3", "-m" , "flask", "--app", "friends/app.py", "run", "--host=0.0.0.0"]

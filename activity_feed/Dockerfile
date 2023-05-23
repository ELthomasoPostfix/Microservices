# syntax=docker/dockerfile:1
FROM python:3.8-slim-buster

# Do microservice specific setup
RUN python3 -m venv venv
RUN . venv/bin/activate
COPY activity_feed/requirements.txt activity_feed/requirements.txt
RUN pip3 install -r activity_feed/requirements.txt

COPY activity_feed/app.py activity_feed/app.py
COPY activity_feed/schemas.py activity_feed/schemas.py

CMD [ "python3", "-m" , "flask", "--app", "activity_feed/app.py", "run", "--host=0.0.0.0"]

# syntax=docker/dockerfile:1
FROM python:3.8-slim-buster

# Do microservice specific setup
RUN python3 -m venv venv
RUN . venv/bin/activate
COPY accounts/requirements.txt accounts/requirements.txt
RUN pip3 install -r accounts/requirements.txt

COPY accounts/app.py accounts/app.py
COPY accounts/schemas.py accounts/schemas.py

CMD [ "python3", "-m" , "flask", "--app", "accounts/app.py", "run", "--host=0.0.0.0"]

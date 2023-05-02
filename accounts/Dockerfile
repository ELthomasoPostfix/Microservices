# syntax=docker/dockerfile:1
FROM python:3.8-slim-buster

# Do microservice specific setup
COPY accounts accounts
RUN pip3 install -r accounts/requirements.txt

# Do microservice shared setup
COPY shared shared

CMD [ "python3", "-m" , "flask", "--app", "accounts/app.py", "run", "--host=0.0.0.0"]

# syntax=docker/dockerfile:1
FROM python:3.8-slim-buster
COPY accounts accounts
RUN pip3 install -r accounts/requirements.txt
COPY shared shared

CMD [ "python3", "-m" , "flask", "--app", "accounts/app.py", "run", "--host=0.0.0.0"]

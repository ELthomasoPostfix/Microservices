# Microservices

This repo contains the code for the micro services assignment for the course Distributed Systems (INFORMAT 1500WETDIS) at the University of Antwerp in the academic year of 2022-2023. The author is Thomas Gueutal (s0195095).

To skip to running the project, refer to [this section](#running-the-project).

The following major sections relate directly to the project's required features and deliverables:
* [Run the project](#running-the-project)
* [Decomposition into Microservices](#decomposition-into-microservices)
* [Documentation](#documentation)

Note that the role of the manual deliverable is filled by the [Documentation](#documentation) section.

# Project Specification

The goal of this project is to decompose the given problem into separate micro services that communicate using RESTful APIs. This is done through the use of docker or podman.

This section repeats the project requirements. This serves the double purpose of A) to thoroughly document the project and to allow in-code references to these requirements and deliverables and B) ensure I properly read and understand the assignment.

The required features compose the given problem. They are to be grouped into several micro services, where graceful failure is always possible. The problem description and the subsequent requirements follow:

**Scenario**: Suppose your best friend has a bright new idea for a revolutionary
website, that is guaranteed to generate billions of dollars. The goal is to fuse
music streaming and social features into a single experience. Everything is
prepared, even the name — Spotibook — and a logo. He only needs the following
small set of features implemented.

1. profile creation/Registration
2. username & password combination verification/Login
3. A user can add other users as friends
4. The user can view a friends list
5. The user can create playlists
6. The user can add songs to a playlist
7. The user can view all songs in a playlist
8. The user can share a playlist with another user
9. Each user has a feed that lists the last N activities of its friends. (sorted
by time) Activities are :
   1. creating a playlist,
   2. adding a song to a playlist,
   3. making a friend
   4. sharing a playlist with a friend.

The minimally required deliverables for a passing grade are:

1. Easy or automatic running of the web service and user interface, e.g. via a <b>run.sh</b> script
2. You need to include a report for part 1 of the assignment. As a reminder, this needs to include the decomposed microservices, which features each microservice implements, which data it stores and which connections it has to other microservices.
3. The report also needs to a small section for part 2 of the assignment, where for each required Feature, you list the API endpoint that implemented it and document it, similar to Assignment 1.


## Submission

Following project submission, a small 5-minute demo of the solution is scheduled per student.

The following are additional notes on project submission

* Make sure no files are missing
* Be sure that the Docker images you make will function on another computer.
* Late submissions will automatically have points deducted for tardiness.
* Make sure that your submission has the following format and upload it via Blackboard! 
    <br><b>DS-Assignment1-Snumber-Lastname.zip</b>

# Running the project

// TODO: Add run section

# Decomposition into Microservices

The following sections detail the decomposition of the project description into atomary microservices. But first, a short description of the available swagger documentation follows.

## Swagger Docs

Each microservice exposes interactive swagger documentation for its own RESTful API. Thus, the docs not accessible through one single URL. Below is a list of URLs that should provide access to the swagger docs for the implemented microservices, but each microservice should also specify their own doc urls:

* **account**: http://127.0.0.1:5002/swagger-ui/

## Accounts Microservice:

Swagger docs urls:

* http://127.0.0.1:5002/swagger-ui/
* http://127.0.0.1:5002/swagger/

Implemented requirements:

1. profile creation/Registration
2. username & password combination verification/Login

This microservice is split up into two docker containers: `accounts` and `accounts_persistence`. The `accounts` container pertains to the flask application logic in the form of a RESTful API. It interacts with the `accounts_persistence` container, which hosts a sql database that stores the following data:

* A *account* table with all the username-password pairs, where the username must be unique

Microservice B:

* A user can add other users as friends
* The user can view a friends list

Microservice C:

* The user can create playlists
* The user can add songs to a playlist
* The user can view all songs in a playlist
* The user can share a playlist with another user

Microservice D:

* Each user has a feed that lists the last N activities of its friends. (sorted
by time) Activities are :
   1. creating a playlist,
   2. adding a song to a playlist,
   3. making a friend
   4. sharing a playlist with a friend.

# Documentation

// TODO: Add docs section

# Encountered Techinical Difficulties

# APISpec

## Swagger VS APISpec Config

The automatically generated API docs work based off of the `flask-apispec` python module. This module generates swagger documentation and serves an interactive instance of it at the specified endpoint. However, problems occur if you specifically configure your `flask` application with APISpec config. Take for example the following standalone code:

```py
from flask import Flask
from flask_apispec.extension import MarshmallowPlugin
from apispec import APISpec

app = Flask(__name__)

app.config.from_mapping({
    'APISPEC_SWAGGER_URL': '/swagger/',
    'APISPEC_SWAGGER_UI_URL': '/swagger-ui/',
    'APISPEC_SPEC': APISpec(
        title='Accounts Microservice',
        version='v1',
        openapi_version='3.0.0',
        plugins=(MarshmallowPlugin(),),
    )
})
```

This `/swagger-ui/` endpoint would serve a broken frontend, some components cannot be loaded and report: *Could not render this component, see the console*. This is because the `flask-apispec` module mixes swagger and openAPI specification rules. Because the documentation is also marked with an openAPI version instead of a swagger version, the frontend tries to interpret the documentation format as OpenAPI (?), which results in a broken frontend.

Instead, ensure the API specification is marked as swagger documentation by configuring the `flask` app as follows:

```py
from flask import Flask

app = Flask(__name__)

MICROSERVICE_NAME = "accounts"
DB_HOST = "accounts_persistence"
app.config.from_mapping({
    'APISPEC_SWAGGER_URL': '/swagger/',
    'APISPEC_SWAGGER_UI_URL': '/swagger-ui/',
    'APISPEC_TITLE': 'Accounts Microservice',
    'APISPEC_VERSION': '1.0'
})
```

## 422 Unprocessable Entity

Error handlers need to be defined to handle such errors. An example of such an error occurring is for the following call:

```sh
$ curl -X POST "http://127.0.0.1:5002/account/bob" -H "Content-Type: application/json" -d password=a
<!doctype html>
<html lang=en>
<title>422 Unprocessable Entity</title>
<h1>Unprocessable Entity</h1>
<p>The request was well-formed but was unable to be followed due to semantic errors.</p>
```

## Flask Error Handlers

To cleanly handle common exceptions thrown in multiple API endoints, `flask` error handlers are desirable. However, `flask-restful` overwrites the error handling facilities of `flask`. A quick and dirty fix that allows the use of `flask` error handlers again, is to simply ask `flask-restful` to propagate errors further up:

```
app.config['PROPAGATE_EXCEPTIONS'] = True
```

source: https://stackoverflow.com/questions/73336629/flask-error-handling-not-working-properly
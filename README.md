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
4. The user can view their friends list
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

The following sections detail the decomposition of the project description into atomary microservices. But first, they are precluded by short descriptions of the available swagger documentation and some notes on graceful failure of microservices.

## Swagger Docs

Each microservice exposes interactive swagger documentation for its own RESTful API. Thus, the docs are not accessible through one single URL. Below is a list of URLs that should provide access to the swagger-ui docs for the implemented microservices, **once the microservices are running**, for easy access. But, each microservice should also specify their own doc urls in their decomposition section.

| Microservice      | url                               |
| -                 | -                                 |
| [accounts](#accounts-microservice)          | http://127.0.0.1:5002/swagger-ui/ |
| [friends](#friends-microservice)           | http://127.0.0.1:5003/swagger-ui/ |
| [playlists](#playlists-microservice)         | http://127.0.0.1:5004/swagger-ui/ |
| [playlists sharing](#playlists-sharing-microservice) | http://127.0.0.1:5005/swagger-ui/ |

## Graceful Failure

It is desirable for errors due to unavailable microservice dependencies to be handled in a controlled manner. For this to be implemented in the assignment, two cases are considered.

The first case entails exceptions occurring due to database access, between a flask server container and its corresponding postgres persistence container. Possible problems include erroneous database transactions or queries and the persistence container failing and going down. To counter these problems, each microservice should define an error handler for the `psycopg2.errors.OperationalError` and `psycopg2.errors.InterfaceError` exception classes. A minimal, flask-only example follows.

```py
from flask import Flask
from psycopg2.errors import OperationalError

app = Flask("microservice")

@app.errorhandler(InterfaceError)
@app.errorhandler(OperationalError)
def handle_db_operational_error(e):
    """Handle database access error or the persistence container being unavailable"""
    return "Error during database access", 500
```

The second case pertains to a flask server container itself being down. For example, the container managing user accounts is depended on by many other microservices, due to their need for verifying a user's existence. If the container providing this service were to go down, then dependent microservices should still return an appropriate response. To resolve this case, all requests to microservices should take into account the possible timeout of the request, or for some other connection error to occur. A first, quite radical solution can be modeled similarly to the previous case. A simple python example for an alternate, less impactful solution follows. This second solution keeps the exception handling closer to the cause.

```py
success = False     # Default output value
try:
    response = requests.get("http://microservice:5000/resource/exists")
    # Set output vars iff. expected, successful response code
    if response.status_code == 200:
        success = True
# Explicitly set output values, to ensure graceful failure is handled appropriately
except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
    success = False
```

In the above example, the url specifies a microservice named `microservice` accessible on port `5000`. The `/resource/exists` path, which is admittedly not a RESTful example, responds with a `200` code iff. the resource exists and no exception is raised within the callee. On success of the call, the output variable `success` is assigned. On an unexpected or erroneous status code, the default value of the output variable `success` is maintained. In case of a failed request call, a `requests.exceptions.Timeout` or `requests.exceptions.ConnectionError` exception occurs, then the output variable is explicitly set to a *failure* or default value. This way, the unavailability of microservice dependencies results in default output being generated regardless.

Lastly, note that the `gui` flask app also implements this second precaution, as it has dependencies on all microservices.

## Songs Microservice:

The songs microservice was provided to us at the start of the assignment. It stores artist-title combinations that represent songs.

## Accounts Microservice:

Swagger docs urls:

* http://127.0.0.1:5002/swagger-ui/
* http://127.0.0.1:5002/swagger/

Implemented requirements:

1. profile creation/Registration
2. username & password combination verification/Login

<details style="background: #3B3B3B; padding: 10px; border-radius: 1rem;">
  <summary>Detailed Implemented Requirements</summary>

| Project Req Nr | API Resource class | HTTP method | URI |
| :-:  | :-: | :-: | :- |
| 1. | [Account](/accounts/app.py)        | POST | /accounts/\<username>      |
| 2. | [Authentication](/accounts/app.py) | POST | /accounts/\<username>/auth |

</details>
<br>

This microservice is split up into two docker containers: `accounts` and `accounts_persistence`. The `accounts` container pertains to the flask application logic in the form of a RESTful API. It interacts with the `accounts_persistence` container, which hosts a [sql database](/accounts_persistence/init.sh) that stores the following data:

* A *account* table with all the `(username, password)` pairs, where the `username` must be unique

Microservice dependencies:

***NONE***

Passwords are stored in plaintext and not encrypted, hashed or treated in any way, neither in storage not in transport. The username of a user will function as the primary, unique identifier of the user in all other microservices.

## Friends Microservice:

Swagger docs urls:

* http://127.0.0.1:5003/swagger-ui/
* http://127.0.0.1:5003/swagger/

Implemented requirements:

3. A user can add other users as friends
4. The user can view a friends list

<details style="background: #3B3B3B; padding: 10px; border-radius: 1rem;">
  <summary>Detailed Implemented Requirements</summary>

| Project Req Nr | API Resource class | HTTP method | URI |
| :-:  | :-: | :-: | :- |
| 3. | [Friend](/friends/app.py)  | POST | /friends/\<username>/\<friendname> |
| 4. | [Friends](/friends/app.py) | GET  | /friends/\<username>               |

</details>
<br>

This microservice is split up into two docker containers: `friends` and `friends_persistence`. The `friends` container pertains to the flask application logic in the form of a RESTful API. It interacts with the `friends_persistence` container, which hosts a [sql database](/friends_persistence/init.sh) that stores the following data:

* A *friend* table with all the `(username, friendname)` pairs, where the `(username, friendname)` pair must be unique.

Microservice dependencies:

* [accounts](#accounts-microservice) - verify account resource existence during any state changing friend APIs

Adding a friend is a one-way operation; it is *NOT* a binary operation. If `bob` adds `dylan` as a friend, then `dylan`'s friend list will remain unaltered. It is then still possible for `dylan` to add `bob` as a friend. The friend adding actions of either user are thus independent.

Note that the POST `friends` API endpoints strictly require **EVERY** user target of the requests to exist. This means that a request to create a friend relationship from `bob` to `dylan` requires both `bob` *and* `dylan` to be existing users. Their existence is verified with the [accounts microservice](#accounts-microservice).

The GET `friends` API endpoints on the other hand do not do any verification of the existence of the user targets for received requests. They rely on the state altering endpoints to do their due diligence, and just provide the stored data. This is done as a form of graceful failure and failure tolerance. If the depended on microservices that store related resources and facilitate the creation and update of friend resources are down, the friends microservice can still provide parts of its service normally. Namely, the friendship relations can still be queried.

## Playlists Microservice:

Swagger docs urls:

* http://127.0.0.1:5004/swagger-ui/
* http://127.0.0.1:5004/swagger/

Implemented requirements:

5. The user can create playlists
6. The user can add songs to a playlist
7. The user can view all songs in a playlist

<details style="background: #3B3B3B; padding: 10px; border-radius: 1rem;">
  <summary>Detailed Implemented Requirements</summary>

| Project Req Nr | API Resource class | HTTP method | URI |
| :-:  | :-: | :-: | :- |
| 5.   | [Playlists](/playlists/app.py) | POST | /playlists/\<username>    |
| 6.   | [Playlist](/playlists/app.py)  | PUT  | /playlists/\<playlist_id> |
| 7.   | [Playlist](/playlists/app.py)  | GET  | /playlists/\<playlist_id> |

</details>
<br>

This microservice is split up into two docker containers: `playlists` and `playlists_persistence`. The `playlists` container pertains to the flask application logic in the form of a RESTful API. It interacts with the `playlists_persistence` container, which hosts a [sql database](/playlists_persistence/init.sh) that stores the following data:

* A *playlist* table with all playlists specific information, where the `(owner_username, title)` pair must be unique.
* A *playlist_song* table which maps playlists to songs, where `(playlist_id, song_artist, song_title)` tuple must be unique.

Microservice dependencies:

* [accounts](#accounts-microservice) - verify account resource existence during any state changing playlist APIs
* [songs](#songs-microservice) - verify song resource existence during any state changing playlist APIs

Note the particular structure of the API endpoints for the playlists microservice specially. The resources that make it up are ordered as follows, from most to least coarse grained: `Playlists > Playlist`.

The top-level `Playlists` resource supports the RESTfulness of the API by making the URI hackable up the tree. It allows retrieval of all playlists that belong to a user, as well as creation of a playlist by a user. This creation step happens with a POST that contains the song title in the request body. RESTfulness is maintained, as POSTing to a collection of resources implicitly specifies the, for now non-existent, target resource. At the time of creation it is impossible to explicitly refer to the resource by its unique URI, `playlists/<int:playlist_id>`, because the resource does not exist at that time.

Next, `Playlist` supports the fetching of all songs in a playlist and the extension of a playlist by adding a new song to it. It can be argued that a playlist is a single resource that transparently encapsulates a collection of simplified songs, meaning that an update of that collection's content is still RESTful, as it is simply updating a resource.

It is worth highlighting that both the playlist creation (POST) and playlist update (PUT) strictly require the existence of some resources related to the target resource. Playlist creation requires the owner of the playlist to exist, for the playlist to be created. It verifies this with the [accounts microservice](#accounts-microservice). The update functionality requires for the song's artist-title combination to constitute an existing song. It verifies this with the provided [songs microservice](#songs-microservice). It does *NOT* check whether the owner of the playlist still exists. This responsibility lies with the playlist creation process and is considered fulfilled as long as it is checked at the time of playlist creation. Note that songs are marked `ON DELETE CASCADE`, so deleting a playlist if the owner were deleted would ensure a valid database state.

The endpoints that make persistent changes to the playlists database perform existence checks for related resources. The GET/fetch endpoints do no such thing. They rely on the state altering endpoints to do their due diligence, and just provide the stored data. This is done as a form of graceful failure and failure tolerance. If the depended on microservices that store related resources and facilitate the creation and update of playlist resources are down, the playlists microservice can still provide parts of its service normally. Namely, the playlists of a user can still be queried.

The following paragraph does not reflect the current implementation, but serves to illustrate a design consideration.

An alternate implementation could have split the updating of a playlist into a separate resource, `PlaylistSong`. Adding the extension functionality of an existing playlist as a PUT on the `Playlist` resource could be rejected in favour of adding a new `PlaylistSong` resource for two reasons. First, the song in a playlist could be considered a separate resource, whose creation via a POST would model updating the playlist. This is perhaps the more RESTful of the two solutions. Additionally, PUT should be idempotent. If it is desirable behavior for a "Resource Already Exists" error to be returned upon adding a song to a playlist it is already a part of, then the PUT implementation would be prohibitive.

## Playlists Sharing Microservice:

Swagger docs urls:

* http://127.0.0.1:5005/swagger-ui/
* http://127.0.0.1:5005/swagger/

Implemented requirements:

8. The user can share a playlist with another user

<details style="background: #3B3B3B; padding: 10px; border-radius: 1rem;">
  <summary>Detailed Implemented Requirements</summary>

| Project Req Nr | API Resource class | HTTP method | URI |
| :-:  | :-: | :-: | :- |
| 8.   | [SharedPlaylist](/playlists_sharing/app.py) | POST | /playlists/\<recipient>/shared/\<playlist_id> |

</details>
<br>

This microservice is split up into two docker containers: `playlists_sharing` and `playlists_sharing_persistence`. The `playlists_sharing` container pertains to the flask application logic in the form of a RESTful API. It interacts with the `playlists_sharing_persistence` container, which hosts a [sql database](/playlists_sharing_persistence/init.sh) that stores the following data:

* A *playlist_share* table with all playlist sharing information, where the `(playlist_id, recipient_username)` pair must be unique. The recipient is the username of the recipient of the sharing action
Microservice dependencies:

Microservice dependencies:

* [playlists](#playlists-microservice) - verify playlist resource existence during any state changing playlist sharing APIs
* [accounts](#accounts-microservice) - verify account resource existence during any state changing playlist APIs


The playlist sharing feature has been consciously split from the [playlists microservice](#playlists-microservice) in favour of atomicity of services. This is analogous to the [accounts microservice](#accounts-microservice) being separate from the [friends microservice](#friends-microservice), in that a consumer app can still find out which playlists have been shared with a specific user even if the [playlists microservice](#playlists-microservice) is down. Though, without access to the proper [playlists microservice](#playlists-microservice), the reponse of the playlists sharing microservice would only specify a list of `(recipient, playlist_id)` tuples. The playlist title is not also included in this microservice due to its possibly mutable nature, so as to avoid data synchronization issues.

The following two paragraphs explain the soft dependency of the playlist sharing microservice on the [playlists microservice](#playlists-microservice) in the context of attaching the playlist title to each shared playlist in the response.

Of note is that the GET operations of the playlists sharing microservice will attempt to query the [playlists microservice](#playlists-microservice) to enrich their own responses. Consider the database contents of playlists sharing, which stores the minimally required sharing information: The recipient username and the playlist id. However, if the list of (or one singular) shared playlists is requested, it is likely that the caller also wants the corresponding playlist meta information, such as the playlist title. Hence the playlists sharing microservice always attempts to fetch the meta info for each shared playlist part of the GET responses; it somewhat acts as a proxy for the [playlists microservice](#playlists-microservice), except that works with shared playlists only.

However, failing a fetch to the [playlists microservice](#playlists-microservice) is not seen as catastrophic. This simply means that for the failing playlist, only the basic sharing information found in the playlist sharing microservice itself is returned. Furthermore, the responses of the [playlists microservice](#playlists-microservice) are *NOT* used to validate whether the contents of the playlists sharing microservice database are valid. Suppose that the sharing database contains a row `('bob', 4)`, meaning playlist `4` was shared with user `bob`. If the [playlists microservice](#playlists-microservice) returns a `404 Not Found` for that playlist, then the playlist sharing microservice does not consider the implications for its data validity. Only simple inquiry success VS failure is considered for the purpose of populating the response with the fetched meta info in addition to the basic information it always responds with. That basic info being playlist id and recipient username.

Microservice E:

* Each user has a feed that lists the last N activities of its friends. (sorted
by time) Activities are :
   1. creating a playlist,
   2. adding a song to a playlist,
   3. making a friend
   4. sharing a playlist with a friend.

# Documentation

// TODO: Add docs section

# Encountered Techinical Difficulties

## APISpec

### Swagger VS APISpec Config

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

Error handlers need to be defined to handle exceptions. An example of such an error occurring is for the following call:

```sh
$ curl -X POST "http://127.0.0.1:5002/account/bob" -H "Content-Type: application/json" -d password=a
<!doctype html>
<html lang=en>
<title>422 Unprocessable Entity</title>
<h1>Unprocessable Entity</h1>
<p>The request was well-formed but was unable to be followed due to semantic errors.</p>
```

Such an error may occur due to flask-apispec trying to format the form or path parameters into their corresponding variables in the API function. Meaning the path params would be placed in the function arguments and the form params into the kwargs function param. If the received param names do not match the expected ones, then the request is wellformed, but flask-apispec cannot resolve the parameters to the corresponding variables. 

## Flask Error Handlers

To cleanly handle common exceptions thrown in multiple API endoints, `flask` error handlers are desirable. However, `flask-restful` overwrites the error handling facilities of `flask`. A quick and dirty fix that allows the use of `flask` error handlers again, is to simply ask `flask-restful` to propagate errors further up:

```
app.config['PROPAGATE_EXCEPTIONS'] = True
```

source: https://stackoverflow.com/questions/73336629/flask-error-handling-not-working-properly

## SQL

### Table-Level Unique Row Combinations

The following design decisions are *NOT* part of the friends microservice any more. Instead, a friend relation goes one way; `bob` can add `dylan` as a friend, and `dylang` has to separately add `bob` as a friend

The friends database potentially requires for a pair of usernames to be unique in the entire table, regardless of the order in which the two usernames are passed to the API. For example, inserting `('bob', 'dylan')` would be the same as inserting `('dylan', 'bob')`. Implementing such a constraint can be done in (at least?) two ways: a trigger or a check constraint.

A trigger would be a more automatic way of handling any inserts on the friend table. It would also decrease the amount of error handling done in the python code, as unique violations would automatically be prevented. However, it would be an inefficient and overcomplicated solution to a simple problem.

The second option is to require the usernames inserted into the table to be ordered, and for the inserted pair to be unique. The check constraint partially pushes the row uniqueness constraint to the database access code, by requiring the insert to sort the usernames.

```sql
CREATE TABLE friend (
    username_1 TEXT NOT NULL,
    username_2 TEXT NOT NULL,
    CONSTRAINT unique_combination CHECK ( username_1 < username_2 ),
    UNIQUE (username_1, username_2)
);
```

### Auto-Incrementing Column

To store playlists, a clean separation of playlist meta information from the playlist's contained songs makes for a more robust implementation. The postgresql sql dialect provides the [serial pseudo datatype](https://www.postgresql.org/docs/15/datatype-numeric.html#DATATYPE-SERIAL). Coupled with the `DEFAULT` keyword, autogenerated, unique ids can be selected:

```postgresql
CREATE TABLE people (
    id SERIAL,
    name TEXT
);

INSERT INTO people values
    (DEFAULT, 'bob'),
    (DEFAULT, 'tony')
;
```

### Insert If Not Exists

Note that I'm not sure which of the below two solutions will be the preferred solution, so do not try to infer from the following paragraph which solution was implemented. It simply documents an encountered choice.

Implementing the playlists functionality to update a playlist can be done in two ways. First, add a separate resource to represent a single song part of a playlist and specify a POST method. Alternately, specify a PUT method on the `Playlist` resource and define the behavior to silently ignore duplicate inserts. For this second option to be viable, it is desirable to have some postgresql functionality available to write an "INSERT IF NOT EXISTS" type query. This [stack overflow post](https://stackoverflow.com/questions/4069718/postgres-insert-if-does-not-exist-already) provides some references.

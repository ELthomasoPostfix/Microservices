# Webservices

This repo contains the code for the micro services assignment for the course Distributed Systems (INFORMAT 1500WETDIS) at the University of Antwerp in the academic year of 2022-2023. The author is Thomas Gueutal (s0195095).

To skip to running the project, refer to [this section](#running-the-project).

The following major sections relate directly to the project's required features and deliverables:
* [Run the project](#running-the-project)
* [Documentation](#documentation)

Note that the role of the manual deliverable is filled by the [RESTful Design Considerations](#restful-design-considerations) section as wel as the [Documentation](#documentation) section.

# Project Specification

The goal of this project is to decompose the given problem into separate micro services that communicate using RESTful APIs. This is done through the use of docker or podman.

This section repeats the project requirements. This serves the double purpose of A) to thoroughly document the project and to allow in-code references to these requirements and deliverables and B) ensure I properly read and undestand the assignment.

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

# Documentation

// TODO: Add docs section
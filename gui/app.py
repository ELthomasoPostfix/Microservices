from flask import Flask, render_template, redirect, request, url_for
import requests

app = Flask(__name__)


# The Username & Password of the currently logged-in User
username = None
password = None

session_data = dict()


def save_to_session(key, value):
    session_data[key] = value


def load_from_session(key):
    return session_data.pop(key) if key in session_data else None  # Pop to ensure that it is only used once


@app.route("/")
def feed():
    # ================================
    # FEATURE 9 (feed)
    #
    # Get the feed of the last N activities of your friends.
    # ================================

    global username

    N = 10

    if username is not None:
        feed = []  # TODO: call
        try:
            response = requests.get(f"http://activity_feed:5000/feeds/{username}?amount={N}")
            if response.status_code == 200:
                feed = [
                    (activity["date"], activity["title"], activity["description"])
                    for activity in response.json().get("result", [])
                    if "date" in activity and "title" in activity and "description" in activity
                ]
        # Explicitly set output values, to ensure graceful failure is handled appropriately
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
            feed = []

    else:
        feed = []

    return render_template('feed.html', username=username, password=password, feed=feed)


@app.route("/catalogue")
def catalogue():
    try:
        songs = requests.get("http://songs:5000/songs").json()
    # Explicitly set output values, to ensure graceful failure is handled appropriately
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
        songs = []

    return render_template('catalogue.html', username=username, password=password, songs=songs)


@app.route("/login")
def login_page():

    success = load_from_session('success')
    return render_template('login.html', username=username, password=password, success=success)


@app.route("/login", methods=['POST'])
def actual_login():
    req_username, req_password = request.form['username'], request.form['password']

    # ================================
    # FEATURE 2 (login)
    #
    # send the username and password to the microservice
    # microservice returns True if correct combination, False if otherwise.
    # Also pay attention to the status code returned by the microservice.
    # ================================
    success = False

    try:
        data = { "password": req_password }
        response = requests.post(f"http://accounts:5000/accounts/{req_username}/auth", data=data)
        if response.status_code == 200:
            success = response.json().get("authentication_data", False)
    # Explicitly set output values, to ensure graceful failure is handled appropriately
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
        success = False

    save_to_session('success', success)
    if success:
        global username, password

        username = req_username
        password = req_password

    return redirect('/login')


@app.route("/register")
def register_page():
    success = load_from_session('success')
    return render_template('register.html', username=username, password=password, success=success)


@app.route("/register", methods=['POST'])
def actual_register():

    req_username, req_password = request.form['username'], request.form['password']

    # ================================
    # FEATURE 1 (register)
    #
    # send the username and password to the microservice
    # microservice returns True if registration is succesful, False if otherwise.
    #
    # Registration is successful if a user with the same username doesn't exist yet.
    # ================================

    success = False

    try:
        data = { "password": req_password }
        response = requests.post(f"http://accounts:5000/accounts/{req_username}", data=data)
        if response.status_code == 201:
            success = True
    # Explicitly set output values, to ensure graceful failure is handled appropriately
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
        success = False

    save_to_session('success', success)

    if success:
        global username, password

        username = req_username
        password = req_password

    return redirect('/register')


@app.route("/friends")
def friends():
    success = load_from_session('success')

    global username

    # ================================
    # FEATURE 4
    #
    # Get a list of friends for the currently logged-in user
    # ================================

    if username is not None:
        friend_list = []
        try:
            response = requests.get(f"http://friends:5000/friends/{username}")
            if response.status_code == 200:
                friend_list = [
                    friend_name
                    for friend_info in response.json().get("result", list())
                    if (friend_name := friend_info.get("friend_name", None)) is not None
                ]
        # Explicitly set output values, to ensure graceful failure is handled appropriately
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
            friend_list = []
    else:
        friend_list = []

    return render_template('friends.html', username=username, password=password, success=success, friend_list=friend_list)


@app.route("/add_friend", methods=['POST'])
def add_friend():

    # ==============================
    # FEATURE 3
    #
    # send the username of the current user and the username of the added friend to the microservice
    # microservice returns True if the friend request is successful (the friend exists & is not already friends), False if otherwise
    # ==============================

    global username
    req_username = request.form['username']

    success = False

    try:
        response = requests.post(f"http://friends:5000/friends/{username}/{req_username}")
        if response.status_code == 201:
            success = True
    # Explicitly set output values, to ensure graceful failure is handled appropriately
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
        success = False

    save_to_session('success', success)

    return redirect('/friends')


@app.route('/playlists')
def playlists():
    global username

    my_playlists = []
    shared_with_me = []

    if username is not None:
        # ================================
        # FEATURE
        #
        # Get all playlists you created and all playlist that are shared with you. (list of id, title pairs)
        # ================================

        my_playlists = []
        shared_with_me = []  # TODO: call

        try:
            response = requests.get(f"http://playlists:5000/playlists/{username}")
            if response.status_code == 200:
                my_playlists = [
                    (playlist["id"], playlist["title"])
                    for playlist in response.json().get("result", list())
                    if "id" in playlist and "title" in playlist
                ]
        # Explicitly set output values, to ensure graceful failure is handled appropriately
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
            my_playlists = []

        try:
            response = requests.get(f"http://playlists_sharing:5000/playlists/{username}/shared?usernameIdentity=recipient")
            if response.status_code == 200:
                shared_playlists = response.json().get("result", list())
                shared_with_me = [
                    (shared_playlist["id"], shared_playlist["title"])
                    for shared_playlist in shared_playlists
                    if "id" in shared_playlist and "title" in shared_playlist
                ]
        # Explicitly set output values, to ensure graceful failure is handled appropriately
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
            shared_with_me = []

    return render_template('playlists.html', username=username, password=password, my_playlists=my_playlists, shared_with_me=shared_with_me)


@app.route('/create_playlist', methods=['POST'])
def create_playlist():
    # ================================
    # FEATURE 5
    #
    # Create a playlist by sending the owner and the title to the microservice.
    # ================================
    global username
    title = request.form['title']

    try:
        data = { "title": title }
        requests.post(f"http://playlists:5000/playlists/{username}", data=data)
    # Explicitly set output values, to ensure graceful failure is handled appropriately
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
        pass    # No output value required

    return redirect('/playlists')


@app.route('/playlists/<int:playlist_id>')
def a_playlist(playlist_id):
    # ================================
    # FEATURE 7
    #
    # List all songs within a playlist
    # ================================
    songs = []

    try:
        response = requests.get(f"http://playlists:5000/playlists/{playlist_id}")
        if response.status_code == 200:
            songs = [
                (song["title"], song["artist"])
                for song in response.json().get("result", list())
                if "title" in song and "artist" in song
            ]
    # Explicitly set output values, to ensure graceful failure is handled appropriately
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
        songs = []

    return render_template('a_playlist.html', username=username, password=password, songs=songs, playlist_id=playlist_id)


@app.route('/add_song_to/<int:playlist_id>', methods=["POST"])
def add_song_to_playlist(playlist_id):
    # ================================
    # FEATURE 6
    #
    # Add a song (represented by a title & artist) to a playlist (represented by an id)
    # ================================
    title, artist = request.form['title'], request.form['artist']

    try:
        data = {
            "artist": artist,
            "title": title
        }
        requests.put(f"http://playlists:5000/playlists/{playlist_id}", data=data)
    # Explicitly set output values, to ensure graceful failure is handled appropriately
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
        pass    # No output value required

    return redirect(f'/playlists/{playlist_id}')


@app.route('/invite_user_to/<int:playlist_id>', methods=["POST"])
def invite_user_to_playlist(playlist_id):
    # ================================
    # FEATURE 8
    #
    # Share a playlist (represented by an id) with a user.
    # ================================
    recipient = request.form['user']

    try:
        requests.post(f"http://playlists_sharing:5000/playlists/{recipient}/shared/{playlist_id}")
    # Explicitly set output values, to ensure graceful failure is handled appropriately
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
        pass    # No output value required

    return redirect(f'/playlists/{playlist_id}')


@app.route("/logout")
def logout():
    global username, password

    username = None
    password = None
    return redirect('/')

from flask import render_template, request, redirect, session, url_for, jsonify
import requests
import time
from main import CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, SPOTIFY_TOKEN_URL, SPOTIFY_API_BASE_URL
from spotutility import refresh_access_token, login, logout
from kworb_utils import extrair_top_artistas_spotify_kworb

# Página inicial (usuário logado ou não)
def index():
    username = session.get("username")
    top_artists_df = extrair_top_artistas_spotify_kworb()
    top_artists_list = []
    if top_artists_df is not None:
        top_artists_list = top_artists_df.head(10).to_dict('records')
    return render_template('index.html', username=username, top_artists=top_artists_list)

def spotmostpopular():
    username = session.get("username")
    top_artists_df = extrair_top_artistas_spotify_kworb()
    top_artists_list = []
    if top_artists_df is not None:
        top_artists_list = top_artists_df.head(10).to_dict('records')
    return render_template('/spotmostpopular.html', username=username, top_artists=top_artists_list)

# Callback do Spotify depois do login
def callback():
    if "error" in request.args:
        return jsonify({"error": f"Erro de autenticação: {request.args['error']}"})

    auth_code = request.args["code"]

    token_data = {
        "grant_type": "authorization_code",
        "code": auth_code,
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }

    try:
        response = requests.post(SPOTIFY_TOKEN_URL, data=token_data)
        response.raise_for_status()
        token_info = response.json()

        session["access_token"] = token_info["access_token"]
        session["refresh_token"] = token_info["refresh_token"]
        session["expires_at"] = time.time() + token_info["expires_in"]

        # Após obter o token, pega o nome do usuário
        headers = {
            "Authorization": f"Bearer {session['access_token']}"
        }
        user_response = requests.get(f"{SPOTIFY_API_BASE_URL}/me", headers=headers)

        if user_response.status_code == 200:
            user_data = user_response.json()
            session["username"] = user_data.get("display_name", "Usuário")

        return redirect(url_for("index"))
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Erro ao obter tokens: {e}"}), 500

def make_spotify_request(endpoint, params=None):
    access_token = session.get("access_token")
    expires_at = session.get("expires_at", 0)

    if time.time() > expires_at:
        refreshed = refresh_access_token()
        if not refreshed:
            return None, redirect(url_for("login"))
        access_token = session.get("access_token")

    headers = {"Authorization": f"Bearer {access_token}"}
    url = f"{SPOTIFY_API_BASE_URL}{endpoint}"
    response = requests.get(url, headers=headers, params=params)

    if response.status_code != 200:
        error_details = ""
        try:
            error_details = response.json()
        except requests.exceptions.JSONDecodeError:
            error_details = response.text
        return None, jsonify({
            "error": f"Erro ao acessar {endpoint}",
            "status_code": response.status_code,
            "details": error_details
        })
    return response.json(), None

def get_recent_tracks(limit=12):
    data, error = make_spotify_request("/me/player/recently-played", params={"limit": limit})
    if error:
        return None, error

    items = data.get("items", [])
    recent_tracks = []
    for item in items:
        track = item["track"]
        track_info = {
            "name": track["name"],
            "artist": track["artists"][0]["name"],
            "album": track["album"]["name"],
            "image": track["album"]["images"][0]["url"]
        }
        recent_tracks.append(track_info)

    return recent_tracks, None
def recent_tracks():
    recent_tracks, error = get_recent_tracks()

    if error:
        return error

    return jsonify(recent_tracks)

# Rotas
view = [
    ("/", index),
    ("/login", login),
    ("/callback", callback),
    ("/logout", logout),
    ("/recent-tracks", recent_tracks),
    ("/spotmostpopular", spotmostpopular)
]
from flask import render_template, request, redirect, session, url_for, jsonify
import requests
import time
from main import CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, SPOTIFY_AUTH_URL, SPOTIFY_TOKEN_URL, SPOTIFY_API_BASE_URL, AUTH_SCOPE

# Página inicial (usuário logado ou não)
def index():
    username = session.get("username")
    return render_template('index.html', username=username)

# Redirecionar para o login do Spotify
def login():
    auth_url = f"{SPOTIFY_AUTH_URL}?client_id={CLIENT_ID}&response_type=code&redirect_uri={REDIRECT_URI}&scope={AUTH_SCOPE}"
    return redirect(auth_url)

# Encerrar sessão
def logout():
    session.pop("access_token", None)
    session.pop("refresh_token", None)
    session.pop("expires_at", None)
    session.pop("username", None)

    return redirect(url_for("index", spotify_logout="1"))

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

# Painel (faixas recentes)
def dashboard():
    access_token = session.get("access_token")
    if not access_token:
        return redirect(url_for("login"))

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    params = {
        "limit": 10
    }

    response = requests.get(f"{SPOTIFY_API_BASE_URL}/me/player/recently-played", headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        recent_tracks = []

        for item in data.get("items", []):
            track = item["track"]
            track_info = {
                "name": track["name"],
                "artist": track["artists"][0]["name"],
                "album": track["album"]["name"],
                "image": track["album"]["images"][0]["url"]
            }
            recent_tracks.append(track_info)

        username = session.get("username")
        return render_template("index.html", tracks=recent_tracks, username=username)
    else:
        return jsonify({"error": "Erro ao buscar faixas recentes", "details": response.json()}), response.status_code   
# Retorna HTML com as faixas recentes

def recent_tracks():
    if 'access_token' not in session:
        return redirect(url_for('index'))

    access_token = session['access_token']
    headers = {'Authorization': f'Bearer {access_token}'}
    params = {'limit': 10}
    response = requests.get('https://api.spotify.com/v1/me/player/recently-played', headers=headers, params=params)

    if response.status_code != 200:
        return 'Erro ao obter faixas recentes'

    items = response.json().get('items', [])

    html = '<ul class="songs-list">'
    for item in items:
        track = item['track']
        name = track['name']
        artist = track['artists'][0]['name']
        album = track['album']['name']
        image_url = track['album']['images'][0]['url']
        html += f"""
        <div class="songs">
            <img src="{image_url}" width="100"><br>
            <strong>{name}</strong><br>
            Artista: {artist}<br>
            Álbum: {album}<br><br>
        </div>
        """
    html += '</ul>'
    return html

# Rotas
view = [
    ("/", index),
    ("/login", login),
    ("/callback", callback),
    ("/dashboard", dashboard),
    ("/logout", logout),
    ("/recent-tracks", recent_tracks)
]

import requests
import time
from flask import redirect, session, url_for
from main import CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, SPOTIFY_AUTH_URL, SPOTIFY_TOKEN_URL, AUTH_SCOPE

def login():
    auth_url = f"{SPOTIFY_AUTH_URL}?client_id={CLIENT_ID}&response_type=code&redirect_uri={REDIRECT_URI}&scope={AUTH_SCOPE}"
    return redirect(auth_url)

def logout():
    session.pop("access_token", None)
    session.pop("refresh_token", None)
    session.pop("expires_at", None)
    session.pop("username", None)

    return redirect(url_for("index", spotify_logout="1"))

def refresh_access_token():
    refresh_token = session.get("refresh_token")
    if not refresh_token:
        return False

    token_data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }

    try:
        response = requests.post(SPOTIFY_TOKEN_URL, data=token_data)
        response.raise_for_status()
        token_info = response.json()

        session["access_token"] = token_info["access_token"]
        session["expires_at"] = time.time() + token_info.get("expires_in", 3600)

        return True
    except requests.exceptions.RequestException as e:
        print(f"Erro ao atualizar token: {e}")
        return False

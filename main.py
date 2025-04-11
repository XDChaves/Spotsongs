from flask import Flask
from dotenv import load_dotenv
import os

load_dotenv()

CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")
REDIRECT_URI = "http://127.0.0.1:5000/callback"
SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API_BASE_URL = "https://api.spotify.com/v1"
AUTH_SCOPE = "user-top-read user-library-read user-read-recently-played"

def create_app():
    app = Flask(__name__)
    app.secret_key = "secret_key"

    from view import view

    for route, view_func in view:
        app.add_url_rule(route, view_func.__name__, view_func, methods=["POST", "GET"])
    
    return app

if __name__ == '__main__':
    app=create_app()
    app.run(debug=True)
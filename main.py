from flask import Flask, jsonify, request
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import subprocess
from dotenv import load_dotenv
import os
from os.path import join, dirname
import re

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path=dotenv_path)

SPOTIFY_CLIENT_ID = os.environ.get("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.environ.get("SPOTIFY_CLIENT_SECRET")

app = Flask(__name__)

client_credentials_manager = SpotifyClientCredentials(client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET)

spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

def get_spotify_track_id(spotify_url):
    match = re.match(r'https://open.spotify.com/track/(\w+)', spotify_url)
    if match:
        return match.group(1)
    return None

@app.route('/play')
def get_url():
    try:
        spotify_url = request.args.get('url')
        # result = subprocess.run(['spotdl', 'url', spotify_url ], capture_output=True, text=True)

        track_id = get_spotify_track_id(spotify_url=spotify_url)

        if not track_id:
            return jsonify({"error": "Invalid Spotify URL"}), 400
        
        track = spotify.track(track_id=track_id)

        track_name = track['name']
        artists = ", ".join([artist['name'] for artist in track['artists']])

        search_query = f"{track_name} {artists}"

        yt_dlp_command = f'yt-dlp "ytsearch1:{search_query}" --get-url --extract-audio'
        
        result = subprocess.run(yt_dlp_command, shell=True, capture_output=True, text=True)

        if result.returncode != 0:
            return jsonify({"error": "Failed to download song", "details": result.stderr}), 500

        return jsonify({"link": result.stdout})
       
    except Exception as e:
        return jsonify({ "message": str(e) }), 500
 
@app.route('/songs')
def get_song():

    try:
        songs = []
        song = {}
        song_name = request.args.get('name')

        if not song_name:
            return jsonify({ "message": "No song name provided" }), 400
        
        result = spotify.search(q='track:' + song_name, type='track', limit=20)

        if result['tracks']['items']:
            tracks = result['tracks']['items']

            for track in tracks:
                artists = [artist['name'] for artist in track['artists']]

                song = {
                    "name": track['name'],
                    "artists": artists,
                    "preview_url": track['preview_url'],
                    "image_url": track['album']['images'][0]['url'],
                    "url": track['external_urls']['spotify']
                }
                songs.append(song)
            
            return jsonify(songs)
    
        else:
            return jsonify({ "message": "No songs found" }), 404
    
       
    except Exception as e:
        return jsonify({ "message": str(e) }), 500
    
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
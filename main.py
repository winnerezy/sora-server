from flask import Flask, jsonify, request
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import subprocess
import urllib.parse

SPOTIFY_CLIENT_ID="7bbc84e56a3147c3a43f7dace62f38f3"
SPOTIFY_CLIENT_SECRET="8d79b82120a5473cab53d86801f4b3af"
app = Flask(__name__)

client_credentials_manager = SpotifyClientCredentials(client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET)

spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

@app.route('/play')
def get_url():
    try:
        spotify_url = request.args.get('url')
        result = subprocess.run(['spotdl', 'url', spotify_url ], capture_output=True, text=True)

        if result.returncode == 0:

            output_lines = result.stdout.splitlines()

            link = None
            for line in output_lines:
                if line.startswith('https://rr2'):
                    link = line
                    break
       
        if link:
            return jsonify({ "link": link })
        
        else:
                return jsonify({"message": "YouTube URL not found in spotdl output"}), 404


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
    app.run(debug=True)
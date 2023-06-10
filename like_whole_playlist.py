import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Instructions for use in README.md file
# Getting user specific details from env
load_dotenv()
CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')
# Can be any valid website
REDIRECT_URI = 'https://github.com/Harjas6'
# Is your user-ID
USERNAME = os.getenv('USERNAME')
# Here because I had a very large playlist and API calls only do 100 songs at a time
# Adjust for size of playlist
MAX_SONGS_ADDED = 1700

# Included reading and modifying from playlists and libraries alongside listening history
SCOPE = 'playlist-read-private playlist-modify-private playlist-modify-public' \
        ' user-library-modify user-library-read user-read-playback-position user-top-read ' \
        'user-read-recently-played'


# Making a SpotifyOAuth object which acts as a token
# using details from env
def create_spotify():
    auth_manager = SpotifyOAuth(
        scope=SCOPE,
        username=USERNAME,
        redirect_uri=REDIRECT_URI,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET)

    spotify = spotipy.Spotify(auth_manager=auth_manager)

    return auth_manager, spotify


# If SpotifyOAuth object/token is expired, refreshes it.
def refresh_spotify(auth_manager, spotify):
    token_info = auth_manager.cache_handler.get_cached_token()
    if auth_manager.is_token_expired(token_info):
        auth_manager, spotify = create_spotify()
    return auth_manager, spotify


# Find a given playlist by name and returning its ID if exists
def find_playlist(playlist_name, spotify):
    index = 0
    raw_playlists = spotify.current_user_playlists()

    # filtering playlists into a convenient form to iterate through
    name_playlists = raw_playlists['items']
    for playlist in name_playlists:
        if playlist['name'] == playlist_name:
            return name_playlists[index]['id']
        index += 1


# Slits a sequence into n sized  chunks
def chunker(seq, size):
    return (seq[pos:pos + size] for pos in range(0, len(seq), size))


# Unlikes all songs that exist in a playlist
def delete_all_songs(spotify, id, offset):
    tracks = make_list_of_song_uri(id=id, spotify=spotify, offset=offset)
    for chunk in chunker(tracks, 50):
        spotify.current_user_saved_tracks_delete(chunk)
    print("Songs Unsaved!")


# Adds all songs from playlist id to liked songs without creating duplicates
def add_all_songs(spotify, id, offset):
    tracks = make_list_of_song_uri(id=id, spotify=spotify, offset=offset)
    for chunk in chunker(tracks, 50):
        spotify.current_user_saved_tracks_add(chunk)
    print("Songs Liked!")


# Makes repeated calls to the API to workaorund 100 song limit to generate list of all songs in playlist
def make_list_of_song_uri(id, spotify, offset):
    song_uri = []
    print("Loading")
    while offset <= MAX_SONGS_ADDED:
        raw_tracks = spotify.playlist_tracks(playlist_id=id, offset=offset)
        songs = raw_tracks['items']
        offset += 100
        for song in songs:
            raw_uri = song['track']['uri']
            raw_uri = raw_uri.removeprefix("spotify:track:")
            song_uri.append(raw_uri)

    return song_uri


# Asks to add or delete songs
def add_or_delete(id, offset, spotify, name):
    ans = input(f"Add or Delete all songs from {name} to/from saved songs [A/D] ").lower()
    if ans == "d":
        delete_all_songs(spotify=spotify, id=id, offset=offset)
    elif ans == "a":
        add_all_songs(spotify=spotify, id=id, offset=offset)
    else:
        add_or_delete(id, offset, spotify)


# Adds all songs in a playlist to liked songs
def main():
    offset = 0
    auth, spotify = create_spotify()
    while True:
        name = input("To quit press enter with no other characters inputted.\nEnter name of playlist: ")
        id = find_playlist(name, spotify)
        if name == '':
            print('\nThanks for using this script!\nCheck out my github at https://github.com/Harjas6')
            break
        if id is not None:
            add_or_delete(id, offset, spotify,name)
        else: print("Playlist not found")




main()

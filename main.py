import spotipy
from spotipy.oauth2 import SpotifyOAuth

from concepts.albums import saved_albums
from concepts.albums import serialize_albums
from concepts.artits import favourite_artists
from concepts.artits import serialize_artists

scope = "user-library-read,user-follow-read"


def main():
    client = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

    artists, artist_count = favourite_artists(client)
    print("Artists count:", artist_count)
    serialize_artists(artists, "data/artists.csv")

    albums, albums_count = saved_albums(client)
    print("Albums count:", albums_count)
    serialize_albums(albums, "data/albums.csv")


if __name__ == '__main__':
    main()


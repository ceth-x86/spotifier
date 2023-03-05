from dataclasses import dataclass
from typing import List
from typing import Dict
from typing import Tuple

from spotipy import Spotify

import csv

MY_ID = "31epeiix5dttigntvwaztibsrgcu"


@dataclass
class PlaylistTrack:
    id: str
    track_number: int
    name: str
    artist_name: str
    album_name: str
    uri: str


@dataclass
class PlaylistOwner:
    id: str
    display_name: str  # ceth for me
    type: str


@dataclass
class Playlist:
    id: str
    name: str
    description: str
    image: str
    collaborative: bool
    tracks: List[PlaylistTrack]
    owner: PlaylistOwner


def selected_playlists(client: Spotify, with_sorting=True) -> Tuple[List[Playlist], int]:
    counter, result = 0, []

    def process_playlist(playlist: Dict):
        nonlocal counter, result
        tracks, items = [], []

        if playlist["owner"]["id"] == MY_ID:
            items = client.playlist_items(playlist_id=playlist["id"])["items"]
            print('O', end='')
        else:
            print('.', end='')

        for item in items:
            track = PlaylistTrack(
                id=item["track"]["id"],
                track_number=item["track"]["track_number"],
                name=item["track"]["name"],
                artist_name=item["track"]["artists"][0]["name"],
                album_name=item["track"]["album"]["name"],
                uri=item["track"]["uri"],
            )
            tracks.append(track)

        owner = PlaylistOwner(
            id=playlist["owner"]["id"],
            display_name=playlist["owner"]["display_name"],
            type=playlist["owner"]["type"],
        )

        pl = Playlist(
            id=playlist["id"],
            name=playlist["name"],
            description=playlist["description"],
            image=playlist["images"][0]["url"],
            collaborative=playlist["collaborative"],
            tracks=tracks,
            owner=owner,

        )

        result.append(pl)
        counter += 1

    playlists = client.current_user_playlists(limit=50)["items"]
    for playlist in playlists:
        process_playlist(playlist)

    while len(playlists) > 0:
        playlists = client.current_user_playlists(limit=50, offset=counter)["items"]
        for playlist in playlists:
            process_playlist(playlist)

    if with_sorting:
        result = sorted(result, key=lambda item: item.id, reverse=False)

    return result, counter


def serialize_playlists(playlists: List[Playlist], filename: str):
    with open(filename, "w") as output_file:
        with open("data/playlists/index.csv", "w") as index_file:
            writer = csv.writer(output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
            index_writer = csv.writer(index_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
            for pl in playlists:
                if pl.owner.id != MY_ID:
                    writer.writerow(
                        [pl.id, pl.name, pl.description, pl.image, pl.owner.id, pl.owner.display_name, pl.owner.type])
                else:
                    index_writer.writerow(
                        [pl.id, pl.name, pl.description, pl.image, pl.owner.id, pl.owner.display_name, pl.owner.type])

                    # TODO: remove deleted playlist files

                    # TODO: refactore
                    with open("data/playlists/" + pl.id + ".csv", "w") as pl_file:
                        pl_writer = csv.writer(pl_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
                        for tr in pl.tracks:
                            # TODO: sort by track number
                            pl_writer.writerow([
                                tr.id, tr.track_number, tr.name, tr.artist_name, tr.album_name, tr.uri])

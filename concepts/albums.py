from dataclasses import dataclass
from typing import List
from typing import Dict
from typing import Tuple

from spotipy import Spotify

import csv

from concepts.artits import Artist


@dataclass
class Album:
    id: str
    name: str
    album_type: str
    release_date: str
    added_at: str
    label: str
    artists: List[Artist]


def saved_albums(client: Spotify, with_sorting=True) -> Tuple[List[Album], int]:
    counter, result = 0, []

    def process_albums(data: List[Dict]):
        nonlocal counter, result
        for item in data:
            album = Album(
                id=item["album"]["id"],
                name=item["album"]["name"],
                label=item["album"]["label"],
                album_type=item["album"]["album_type"],
                release_date=item["album"]["release_date"],
                artists=[],
                added_at=item["added_at"]
            )
            for artist in item["album"]["artists"]:
                album.artists.append(Artist(id=artist["id"], name=artist["name"]))
            result.append(album)
            counter += 1

    albums = client.current_user_saved_albums(limit=50)["items"]
    process_albums(albums)

    while len(albums) > 0:
        albums = client.current_user_saved_albums(limit=50, offset=counter)["items"]
        process_albums(albums)

    if with_sorting:
        result = sorted(result, key=lambda item: item.release_date, reverse=True)

    return result, counter


def serialize_albums(albums: List[Album], filename: str):
    with open(filename, "w") as output_file:
        writer = csv.writer(output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
        for album in albums:
            writer.writerow([album.artists[0].name, album.name, album.release_date, album.album_type, album.label,
                             album.id])

def deserialize_albums(filename: str) -> List[Album]:
    result = []
    with open(filename, "r") as input_file:
        reader = csv.reader(input_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
        for row in reader:
            album = Album(
                id=row[5],
                name=row[1],
                label=row[4],
                album_type=row[3],
                release_date=row[2],
                artists=[row[0]],  # TODO: fix me
                added_at="",
            )
            result.append(album)
        result = sorted(result, key=lambda item: item.release_date, reverse=False)
        return result


def delete_albums(client: Spotify, albums: List[Album]):
    ids = [album.id for album in albums]
    for i in range(0, len(ids), 10):
        current_ids = ids[i:i+10]
        client.current_user_saved_albums_delete(current_ids)


def add_albums(client: Spotify, albums: List[Album]):
    ids = [album.id for album in albums]
    for i in range(0, len(ids), 5):
        current_ids = ids[i:i+5]
        client.current_user_saved_albums_add(current_ids)

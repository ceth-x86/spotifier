from dataclasses import dataclass
from typing import List
from typing import Dict
from typing import Tuple

from spotipy import Spotify

import csv

@dataclass
class Artist:
    id: str
    name: str


def favourite_artists(client: Spotify, with_sorting=True) -> Tuple[List[Artist], int]:
    counter, last_id, result = 0, "", []

    def process_artists(data: List[Dict]):
        nonlocal counter, last_id, result
        for item in data:
            result.append(Artist(id=item["id"], name=item["name"]))
            counter += 1
            last_id = item["id"]

    artists = client.current_user_followed_artists(limit=50)["artists"]["items"]
    process_artists(artists)

    while len(artists) > 0:
        artists = client.current_user_followed_artists(limit=50, after=last_id)["artists"]["items"]
        process_artists(artists)

    if with_sorting:
        result = sorted(result, key=lambda item: item.name)

    return result, counter


def serialize_artists(artists: List[Artist], filename: str):
    with open(filename, "w") as output_file:
        writer = csv.writer(output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
        for artist in artists:
            writer.writerow([artist.name, artist.id])



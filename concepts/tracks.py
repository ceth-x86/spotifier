from dataclasses import dataclass
from typing import List
from typing import Dict
from typing import Tuple

from spotipy import Spotify

import csv

from concepts.artits import Artist

@dataclass
class Track:
    id: str
    name: str
    artist_name: str
    album_name: str
    added_at: str


def saved_tracks(client: Spotify, with_sorting=True) -> Tuple[List[Track], int]:
    counter, result = 0, []

    def process_tracks(data: List[Dict]):
        nonlocal counter, result
        for item in data:
            track = Track(
                id=item["track"]["id"],
                name=item["track"]["name"],
                artist_name=item["track"]["artists"][0]["name"],
                album_name=item["track"]["album"]["name"],
                added_at=item["added_at"]
            )
            result.append(track)
            counter += 1

    tracks = client.current_user_saved_tracks(limit=50)["items"]
    process_tracks(tracks)

    while len(tracks) > 0:
        tracks = client.current_user_saved_tracks(limit=50, offset=counter)["items"]
        process_tracks(tracks)

    if with_sorting:
        result = sorted(result, key=lambda item: item.added_at, reverse=True)

    return result, counter


def serialize_tracks(tracks: List[Track], filename: str):
    with open(filename, "w") as output_file:
        writer = csv.writer(output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
        for track in tracks:
            writer.writerow([track.name, track.artist_name, track.album_name, track.added_at, track.id])

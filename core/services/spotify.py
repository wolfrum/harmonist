import os
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
from django.utils import timezone
from django.db import transaction
from dotenv import load_dotenv

from core.models import Artist, Album, ArtistAlias, Song, Genre

load_dotenv()  # Load environment variables from .env

class SpotifyService:
    def __init__(self):
        self.client = Spotify(
            auth_manager=SpotifyClientCredentials(
                client_id=os.getenv("SPOTIPY_CLIENT_ID"),
                client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
            )
        )

    def search_artist(self, name):
        """Search Spotify for an artist by name."""
        results = self.client.search(q=name, type='artist', limit=1)
        artists = results.get("artists", {}).get("items", [])
        return artists[0] if artists else None

    def get_artist_albums(self, spotify_artist_id):
        """Return all albums for a given artist ID."""
        albums = []
        results = self.client.artist_albums(spotify_artist_id, album_type='album')
        while results:
            albums.extend(results.get("items", []))
            results = self.client.next(results) if results.get("next") else None
        return albums

    def get_album_tracks(self, spotify_album_id):
        """Fetch all tracks for a given album ID."""
        tracks = []
        results = self.client.album_tracks(spotify_album_id)
        while results:
            tracks.extend(results.get("items", []))
            results = self.client.next(results) if results.get("next") else None
        return tracks

    @transaction.atomic
    def save_artist_and_albums(self, spotify_artist, imported_as=None):
        """Create or update Artist and related Albums/Songs in Django."""

        existing_artist = Artist.objects.filter(spotify_id=spotify_artist["id"]).first()

        if existing_artist:
            existing_artist.name = spotify_artist["name"]
            existing_artist.popularity = spotify_artist.get("popularity")
            existing_artist.followers = spotify_artist.get("followers", {}).get("total")
            existing_artist.image_url = spotify_artist.get("images", [{}])[0].get("url")
            existing_artist.uri = spotify_artist.get("uri")
            existing_artist.last_synced_at = timezone.now()
            existing_artist.save()
            artist = existing_artist
        else:
            artist = Artist.objects.create(
                spotify_id=spotify_artist["id"],
                name=spotify_artist["name"],
                popularity=spotify_artist.get("popularity"),
                followers=spotify_artist.get("followers", {}).get("total"),
                image_url=spotify_artist.get("images", [{}])[0].get("url"),
                uri=spotify_artist.get("uri"),
                last_synced_at=timezone.now(),
            )

        if imported_as and imported_as != artist.name:
            ArtistAlias.objects.get_or_create(artist=artist, name_used=imported_as)

        for genre_name in spotify_artist.get("genres", []):
            genre_obj, _ = Genre.objects.get_or_create(name=genre_name)
            artist.genres.add(genre_obj)

        albums = self.get_artist_albums(spotify_artist["id"])
        for album in albums:
            album_obj, _ = Album.objects.get_or_create(
                spotify_id=album["id"],
                defaults={
                    "title": album["name"],
                    "release_date": album.get("release_date"),
                    "cover_url": album.get("images", [{}])[0].get("url"),
                }
            )
            album_obj.artists.add(artist)

            tracks = self.get_album_tracks(album["id"])
            for track in tracks:
                Song.objects.get_or_create(
                    spotify_id=track["id"],
                    defaults={
                        "title": track["name"],
                        "album": album_obj,
                        "duration_ms": track.get("duration_ms"),
                        "track_number": track.get("track_number"),
                        "disc_number": track.get("disc_number"),
                        "explicit": track.get("explicit", False),
                        "uri": track.get("uri"),
                        "preview_url": track.get("preview_url"),
                        "external_url": track.get("external_urls", {}).get("spotify"),
                    }
                )

        return artist

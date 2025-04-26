from django.db import models
from datetime import datetime
from django.forms import ValidationError

class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='subgenres')

    def __str__(self):
        return self.name

class Artist(models.Model):
    name = models.CharField(max_length=200, db_index=True)
    spotify_id = models.CharField(max_length=100, blank=True, null=True, unique=True)
    popularity = models.IntegerField(null=True, blank=True)
    followers = models.IntegerField(null=True, blank=True)
    genres = models.ManyToManyField(Genre, related_name='artists', blank=True)
    image_url = models.URLField(blank=True, null=True)
    uri = models.CharField(max_length=100, blank=True, null=True)
    last_synced_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.name

class Album(models.Model):
    title = models.CharField(max_length=200)
    artists = models.ManyToManyField(Artist, related_name='albums')
    spotify_id = models.CharField(max_length=100, blank=True, null=True, unique=True)
    release_date = models.CharField(max_length=32, blank=True, null=True)
    cover_url = models.URLField(blank=True, null=True)

    @property
    def release_year(self):
        if self.release_date:
            try:
                return datetime.strptime(self.release_date, "%Y-%m-%d").year
            except ValueError:
                try:
                    return datetime.strptime(self.release_date, "%Y-%m").year
                except ValueError:
                    try:
                        return datetime.strptime(self.release_date, "%Y").year
                    except ValueError:
                        return None
        return None

class ArtistConnection(models.Model):
    CONNECTION_TYPES = [
        ("influenced_by", "Influenced By"),
        ("influences", "Influences"),
        ("listens_to", "Listens To"),
        ("listened_by", "Listened By"),
    ]

    from_artist = models.ForeignKey(Artist, related_name="connections_from", on_delete=models.CASCADE)
    to_artist = models.ForeignKey(Artist, related_name="connections_to", on_delete=models.CASCADE)
    connection_type = models.CharField(max_length=20, choices=CONNECTION_TYPES)
    note = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("from_artist", "to_artist", "connection_type")

    def __str__(self):
        return f"{self.from_artist} {self.connection_type} {self.to_artist}"
    
class ArtistConnectionSource(models.Model):
    SOURCE_TYPES = [
        ("article", "Article"),
        ("interview", "Interview"),
        ("podcast", "Podcast"),
        ("video", "Video"),
        ("book", "Book"),
        ("social", "Social Media"),
        ("other", "Other"),
    ]

    connection = models.ForeignKey(
        "ArtistConnection",
        related_name="sources",
        on_delete=models.CASCADE,
    )
    url = models.URLField()
    description = models.CharField(
        max_length=255,
        blank=True,
        help_text="Optional note about this source (e.g. 'Rolling Stone 2020 interview')"
    )
    source_type = models.CharField(
        max_length=20,
        choices=SOURCE_TYPES,
        default="article",
        help_text="Type of source for this connection"
    )
    date_found = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"{self.get_source_type_display()} for {self.connection.from_artist.name} → {self.connection.to_artist.name}"

class ArtistAdminNote(models.Model):
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name='admin_notes')
    note = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Admin Note for {self.artist.name} ({self.created_at.date()})"


class ArtistFanNote(models.Model):
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name='fan_notes')
    note = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Fan Note for {self.artist.name} ({self.created_at.date()})"

class ArtistMembership(models.Model):
    member = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name='groups')
    group = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name='members')
    note = models.TextField(blank=True, null=True)
    joined_on = models.DateField(blank=True, null=True)
    left_on = models.DateField(blank=True, null=True)

    class Meta:
        unique_together = ('member', 'group')

    def __str__(self):
        return f"{self.member.name} is/was a member of {self.group.name}"


class ArtistAlias(models.Model):
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name='aliases')
    name_used = models.CharField(max_length=200)

    def __str__(self):
        return f"Alias '{self.name_used}' for {self.artist.name}"
    
class Song(models.Model):
    title = models.CharField(max_length=200)
    album = models.ForeignKey(Album, on_delete=models.CASCADE, related_name='songs')
    spotify_id = models.CharField(max_length=100, blank=True, null=True, unique=True)
    duration_ms = models.IntegerField(blank=True, null=True)
    track_number = models.IntegerField(blank=True, null=True)
    disc_number = models.IntegerField(blank=True, null=True)
    explicit = models.BooleanField(default=False)
    uri = models.CharField(max_length=100, blank=True, null=True)  
    preview_url = models.URLField(blank=True, null=True)
    external_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"{self.album.title} – {self.title}"

    @property
    def duration_minutes(self):
        """Returns duration in minutes:seconds format."""
        if self.duration_ms:
            minutes, seconds = divmod(self.duration_ms // 1000, 60)
            return f"{minutes}:{str(seconds).zfill(2)}"
        return None

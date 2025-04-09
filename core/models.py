from django.db import models
from datetime import datetime

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

class ArtistInfluence(models.Model):
    from_artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name='influences')
    to_artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name='influenced_by')
    note = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('from_artist', 'to_artist')

    def __str__(self):
        return f"{self.from_artist} influenced {self.to_artist}"


class ArtistInfluenceLink(models.Model):
    influence = models.ForeignKey(ArtistInfluence, on_delete=models.CASCADE, related_name='links')
    url = models.URLField()

    def __str__(self):
        return self.url


class ArtistListening(models.Model):
    listener = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name='listens_to')
    listening_to = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name='listened_by')
    note = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('listener', 'listening_to')

    def __str__(self):
        return f"{self.listener} listens to {self.listening_to}"


class ArtistListeningLink(models.Model):
    listening = models.ForeignKey(ArtistListening, on_delete=models.CASCADE, related_name='links')
    url = models.URLField()

    def __str__(self):
        return self.url


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

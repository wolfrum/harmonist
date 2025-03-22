from django.db import models

class Artist(models.Model):
    name = models.CharField(max_length=200, unique=True)
    spotify_id = models.CharField(max_length=100, blank=True, null=True, unique=True)
    genres = models.JSONField(blank=True, null=True)
    image_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name


class Album(models.Model):
    title = models.CharField(max_length=200)
    artists = models.ManyToManyField(Artist, related_name='albums')
    spotify_id = models.CharField(max_length=100, blank=True, null=True, unique=True)
    release_date = models.DateField(blank=True, null=True)
    cover_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.title


class Song(models.Model):
    title = models.CharField(max_length=200)
    album = models.ForeignKey(Album, on_delete=models.CASCADE, related_name='songs')
    spotify_id = models.CharField(max_length=100, blank=True, null=True, unique=True)
    duration_ms = models.IntegerField(blank=True, null=True)
    track_number = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.title


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


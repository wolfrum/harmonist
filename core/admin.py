from django.contrib import admin
from django.urls import path
from django.utils.html import format_html
from django.shortcuts import render, redirect
from django.db.models import Q
from core.models import Artist, Genre, Album, Song, ArtistInfluenceLink, ArtistInfluence

class HarmonistAdminSite(admin.AdminSite):
    site_header = "Harmonist Admin"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('genre-cleanup/', self.admin_view(self.genre_cleanup_view), name='genre_cleanup'),
        ]
        return custom_urls + urls

    
    def genre_cleanup_view(self, request):
        artists = Artist.objects.filter(Q(genres__isnull=True) | Q(genres=[]))

        if request.method == "POST":
            artist_id = request.POST.get("artist_id")
            genre_list = request.POST.get("genres")
            artist = Artist.objects.filter(id=artist_id).first()
            if artist and genre_list:
                artist.genres = [genre.strip() for genre in genre_list.split(",") if genre.strip()]
                artist.save()
                return redirect("/admin/genre-cleanup/")

        return render(request, "admin/genre_cleanup.html", {
            "artists": artists,
        })

# Custom inlines and admin classes
class ArtistInfluenceLinkInline(admin.TabularInline):
    model = ArtistInfluenceLink
    extra = 1

class ArtistInfluenceAdmin(admin.ModelAdmin):
    list_display = ("from_artist", "to_artist", "note")
    search_fields = ("from_artist__name", "to_artist__name", "note")
    autocomplete_fields = ["from_artist", "to_artist"]
    inlines = [ArtistInfluenceLinkInline]

class ArtistAdmin(admin.ModelAdmin):
    search_fields = ["name"]
    filter_horizontal = ("genres",)

class GenreAdmin(admin.ModelAdmin):
    list_display = ("name", "parent")
    list_filter = ("parent", )
    search_fields = ["name"]
    autocomplete_fields = ["parent"]

# Use our custom admin site
admin_site = HarmonistAdminSite(name='harmonist_admin')

# Register your models
admin_site.register(ArtistInfluence, ArtistInfluenceAdmin)
admin_site.register(Artist, ArtistAdmin)
admin_site.register(Genre, GenreAdmin)
admin_site.register(Album)
admin_site.register(Song)
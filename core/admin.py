from django.contrib import admin
from django.urls import path
from django.utils.html import format_html
from django.shortcuts import render, redirect
from django.db.models import Q
from core.models import Artist

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

# Use our custom admin site
admin_site = HarmonistAdminSite(name='harmonist_admin')

# Register your models
from core.models import Album, Song
admin_site.register(Artist)
admin_site.register(Album)
admin_site.register(Song)
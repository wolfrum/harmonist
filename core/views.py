from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from core.models import Artist
from urllib.parse import unquote

def home_view(request):
    return render(request, "core/index.html")

def settings_view(request):
    return render(request, "core/settings.html")

def about_view(request):
    return render(request, "core/about.html")

def blog_view(request):
    return render(request, "core/blog.html")

def explore_view(request):
    return render(request, "core/explore.html")

def genres_view(request):
    genre_map = {}

    for artist in Artist.objects.all():
        genres = artist.genres or ["Uncategorized"]
      
        for genre in genres:
            genre_map.setdefault(genre, []).append(artist)

    # ✅ Sort artists in each genre by popularity (descending)
    for genre in genre_map:
        genre_map[genre] = sorted(
            genre_map[genre], key=lambda a: a.popularity or 0, reverse=True
        )

    return render(request, 'core/genres.html', {'genre_map': genre_map})

def genre_detail_view(request, genre):
    genre = unquote(genre)  # in case there's URL-encoded content
    artists = Artist.objects.filter(genres__contains=[genre]).order_by('name')

    return render(request, 'core/genre_detail.html', {
        'genre': genre.title(),
        'genre_slug': genre,
        'artists': artists,
    })

def artist_detail(request, artist_id):
    artist = get_object_or_404(Artist, id=artist_id)
    albums = artist.albums.prefetch_related("songs").all()

    return render(request, "core/artist_detail.html", {
        "artist": artist,
        "albums": albums,
    })


def set_language(request):
    """Handles language selection from the settings page."""
    if request.method == "POST":
        lang = request.POST.get("language", "en")  # Default to English
        response = redirect("settings")  # Redirect back to settings page
        response.set_cookie("language", lang, max_age=31536000)  # Store for 1 year
        return response
    return HttpResponse("Invalid request", status=400)

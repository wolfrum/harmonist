from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.urls import reverse
from core.models import Artist, Genre
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

    for genre in Genre.objects.prefetch_related('artists'):
        artists = genre.artists.order_by('-popularity')
        genre_map[genre] = artists

    # 🔥 Sort genres by total popularity of their artists
    sorted_genre_items = sorted(
        genre_map.items(),
        key=lambda item: sum(artist.followers or 0 for artist in item[1]),
        reverse=True,
    )

    return render(request, 'core/genres.html', {
        'genre_map': dict(sorted_genre_items),
    })

def genre_detail_view(request, genre):
    genre = get_object_or_404(Genre, name=unquote(genre))
    artists = genre.artists.order_by('name')

    return render(request, 'core/genre_detail.html', {
        'genre': genre.name,
        'genre_slug': genre.name,
        'artists': artists,
    })

def artist_detail(request, artist_id):
    artist = get_object_or_404(Artist, id=artist_id)
    albums = artist.albums.prefetch_related("songs").all()

    return render(request, "core/artist_detail.html", {
        "artist": artist,
        "albums": albums,
    })

def artist_network_data(request, artist_id):
    artist = Artist.objects.get(id=artist_id)

    influences = artist.influences.select_related('to_artist')
    influenced_by = artist.influenced_by.select_related('from_artist')
    listens_to = artist.listens_to.select_related('listening_to')
    listened_by = artist.listened_by.select_related('listener')

    def artist_node(a):
        return {
            "id": a.id,
            "label": a.name,
            "url": reverse("artist_detail", args=[a.id]),
            "image": a.image_url if a.image_url else None,
        }

    nodes = {artist.id: artist_node(artist)}
    links = []

    for rel in influences:
        nodes[rel.to_artist.id] = artist_node(rel.to_artist)
        links.append({"source": artist.id, "target": rel.to_artist.id, "type": "influenced"})

    for rel in influenced_by:
        nodes[rel.from_artist.id] = artist_node(rel.from_artist)
        links.append({"source": rel.from_artist.id, "target": artist.id, "type": "influenced"})

    for rel in listens_to:
        nodes[rel.listening_to.id] = artist_node(rel.listening_to)
        links.append({"source": artist.id, "target": rel.listening_to.id, "type": "listens_to"})

    for rel in listened_by:
        nodes[rel.listener.id] = artist_node(rel.listener)
        links.append({"source": rel.listener.id, "target": artist.id, "type": "listens_to"})

    return JsonResponse({
        "nodes": list(nodes.values()),
        "links": links,
    })



def set_language(request):
    """Handles language selection from the settings page."""
    if request.method == "POST":
        lang = request.POST.get("language", "en")  # Default to English
        response = redirect("settings")  # Redirect back to settings page
        response.set_cookie("language", lang, max_age=31536000)  # Store for 1 year
        return response
    return HttpResponse("Invalid request", status=400)

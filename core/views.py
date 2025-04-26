from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.urls import reverse
from django.db.models import Q
from core.models import Artist, ArtistConnection, Genre
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
    # Get all parent genres
    parent_genres = Genre.objects.filter(parent__isnull=True).order_by("name")

    genre_map = {}

    for parent in parent_genres:
        # Include the parent genre and its subgenres
        related_genres = Genre.objects.filter(Q(id=parent.id) | Q(parent=parent))
        artists = (
            Artist.objects.filter(genres__in=related_genres)
            .distinct()
            .order_by("-followers")[:10] 
        )

        if artists.exists():
            genre_map[parent] = artists

    sorted_genre_map = dict(
        sorted(
            genre_map.items(),
            key=lambda item: sum(artist.followers or 0 for artist in item[1]),
            reverse=True,
        )
    )
    
    return render(request, "core/genres.html", {
        "genre_map": sorted_genre_map,
    })

def genre_detail_view(request, genre):
    """Displays all artists under a genre and its subgenres."""
    genre = get_object_or_404(Genre, name=unquote(genre))

    all_related_genres = Genre.objects.filter(Q(id=genre.id) | Q(parent=genre))
    artists = Artist.objects.filter(genres__in=all_related_genres).distinct().order_by("name")

    return render(request, "core/genre_detail.html", {
        "genre": genre.name,
        "genre_slug": genre.name,
        "artists": artists,
    })

def artist_detail(request, artist_id):
    artist = get_object_or_404(Artist, pk=artist_id)

    connections = ArtistConnection.objects.filter(
        Q(from_artist=artist) | Q(to_artist=artist)
    ).select_related("from_artist", "to_artist").prefetch_related("sources")

    # Flatten the connection view for fallback rendering
    display_connections = []
    for conn in connections:
        if conn.from_artist == artist:
            other = conn.to_artist
        else:
            other = conn.from_artist

        display_connections.append({
            "other": other,
            "connection_type": conn.get_connection_type_display(),
            "sources": conn.sources.all(),
        })

    albums = artist.albums.prefetch_related("songs")

    context = {
        "artist": artist,
        "albums": albums,
        "connections": connections,  # for JS rendering
        "display_connections": display_connections,  # for fallback HTML
    }
    return render(request, "core/artist_detail.html", context)

def artist_network_data(request, artist_id):
    artist = get_object_or_404(Artist, id=artist_id)

    def artist_node(a):
        return {
            "id": a.id,
            "label": a.name,
            "url": reverse("artist_detail", args=[a.id]),
            "image": a.image_url if a.image_url else None,
        }

    nodes = {artist.id: artist_node(artist)}
    links = []

    # ✅ Also prefetch sources here (future-proofing if you want to show all URLs)
    connections = ArtistConnection.objects.filter(
        Q(from_artist=artist) | Q(to_artist=artist)
    ).select_related("from_artist", "to_artist").prefetch_related("sources")

    for conn in connections:
        nodes[conn.from_artist.id] = artist_node(conn.from_artist)
        nodes[conn.to_artist.id] = artist_node(conn.to_artist)

        # For now, we still use only one hyperlink for D3; update later if needed
        first_url = conn.sources.first().url if conn.sources.exists() else ""

        links.append({
            "source": conn.from_artist.id,
            "target": conn.to_artist.id,
            "type": conn.connection_type,
            "url": first_url,
        })

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

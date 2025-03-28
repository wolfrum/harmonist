from django.urls import path
from core.admin import admin_site
from .views import (
    home_view, settings_view, about_view, blog_view, explore_view, set_language,
    genres_view, genre_detail_view, artist_detail,
)

urlpatterns = [
    path("", home_view, name="home"),
    path("settings/", settings_view, name="settings"),
    path("about/", about_view, name="about"),
    path("blog/", blog_view, name="blog"),
    path("explore/", explore_view, name="explore"),
    path("set-language/", set_language, name="set_language"),
    path("genres/", genres_view, name="genres"),
    path('genres/<str:genre>/', genre_detail_view, name='genre_detail'),
    path('artists/<int:artist_id>/', artist_detail, name='artist_detail'),

    
]

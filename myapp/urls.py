from django.urls import path
from .views import home_view, settings_view, about_view, blog_view, explore_view, set_language

urlpatterns = [
    path("", home_view, name="home"),
    path("settings/", settings_view, name="settings"),
    path("about/", about_view, name="about"),
    path("blog/", blog_view, name="blog"),
    path("explore/", explore_view, name="explore"),
    path("set-language/", set_language, name="set_language"),
]

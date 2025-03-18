from django.shortcuts import render, redirect
from django.http import HttpResponse

def home_view(request):
    return render(request, "index.html")

def settings_view(request):
    return render(request, "settings.html")

def about_view(request):
    return render(request, "about.html")

def blog_view(request):
    return render(request, "blog.html")

def explore_view(request):
    return render(request, "explore.html")

def set_language(request):
    """Handles language selection from the settings page."""
    if request.method == "POST":
        lang = request.POST.get("language", "en")  # Default to English
        response = redirect("settings")  # Redirect back to settings page
        response.set_cookie("language", lang, max_age=31536000)  # Store for 1 year
        return response
    return HttpResponse("Invalid request", status=400)

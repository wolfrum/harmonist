import json
import os
from django.conf import settings

def load_json_file(lang="en"):
    """Loads and returns the JSON content for the selected language."""
    json_file = os.path.join(settings.BASE_DIR, "i18n", f"{lang}.json")
    
    # Fallback to English if the selected file doesn't exist
    if not os.path.exists(json_file):
        json_file = os.path.join(settings.BASE_DIR, "i18n", "en.json")

    with open(json_file, "r", encoding="utf-8") as file:
        return json.load(file)

def json_texts(request):
    """Context processor to load JSON texts and inject them into all templates."""
    lang = request.COOKIES.get("language", "en")  # Get language from cookies (default: en)
    return load_json_file(lang)

def breadcrumbs_context(request):
    if hasattr(request, "breadcrumbs"):
        # Use manually set breadcrumbs from view
        return {"breadcrumbs": request.breadcrumbs}

    # Fallback: build from path segments
    path = request.path
    segments = [segment for segment in path.strip('/').split('/') if segment]
    breadcrumbs = []
    url = '/'

    for segment in segments:
        url += segment + '/'
        breadcrumbs.append({
            'label': segment.replace('-', ' ').replace('_', ' ').title(),
            'url': url
        })

    return {
        'breadcrumbs': breadcrumbs
    }

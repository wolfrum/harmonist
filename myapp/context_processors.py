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

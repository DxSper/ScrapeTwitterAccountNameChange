import json
import os

# Chemin du fichier où les URLs seront stockées
URLS_FILE = 'urls.json'

def load_urls():
    """Charge les URLs depuis le fichier JSON."""
    if os.path.exists(URLS_FILE):
        with open(URLS_FILE, 'r') as file:
            return json.load(file)
    return []  # Retourne une liste vide si le fichier n'existe pas

def save_urls(urls):
    """Sauvegarde les URLs dans le fichier JSON."""
    with open(URLS_FILE, 'w') as file:
        json.dump(urls, file)

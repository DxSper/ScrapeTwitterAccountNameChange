import requests
import discord
from discord.ext import commands
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager as CM
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import threading
import time
from urls import load_urls, save_urls  # Importer les fonctions pour charger et sauvegarder les URLs
from config import *

# Fonction pour envoyer un message au webhook Discord
def send_discord_message(message):
    data = {
        "content": message
    }
    requests.post(WEBHOOK_URL, json=data)

# Liste des URLs à vérifier
# Charger les URLs depuis le fichier
urls = load_urls()
threads = []  # Liste pour stocker les threads actifs
stop_event = threading.Event()  # Événement pour arrêter les threads

# Créer le bot Discord
bot = commands.Bot(intents=discord.Intents.default())

@bot.event
async def on_ready():
    print(f'Bot connecté en tant que {bot.user}')
    await bot.change_presence(activity=discord.Game(name="en train de scraper"))
    start_monitoring()  # Démarrer la surveillance

def start_monitoring():
    global threads, stop_event
    # Arrêter les threads existants
    stop_event.set()  # Signaler aux threads de s'arrêtera
    for thread in threads:
        thread.join(timeout=1)  # Attendre que le thread se termine
    threads.clear()  # Réinitialiser la liste des threads
    stop_event = threading.Event()  # Réinitialiser l'événement

    # Démarrer un nouveau thread pour chaque URL
    for url in urls:
        thread = threading.Thread(target=check_account, args=(url,))
        thread.start()
        threads.append(thread)  # Stocker le thread dans la liste

@bot.slash_command(
    name="help",
    description="Affiche la liste des commandes disponibles.",
    guild_ids=GUILD_ID  # Remplacez par votre ID de serveur
)
async def help_command(ctx):
    help_message = (
        "Voici les commandes disponibles :\n"
        "/seturls <url> : Ajoute un url à la liste des URLs à surveiller.\n"
        "/removeurl <url> : Supprime une URL de la liste.\n"
        "/listurls : Affiche la liste des URLs surveillées.\n"
        "/help : Affiche cette liste d'aide."
    )
    await ctx.respond(help_message)

@bot.slash_command(
    name="seturls",
    description="Met à jour la liste des URLs à surveiller.",
    guild_ids=GUILD_ID  # Remplacez par votre ID de serveur
)
async def set_urls(ctx, new_urls: str):
    global urls
    urls.append(new_urls)
    save_urls(urls)
    await ctx.respond(f"Liste des URLs mise à jour : {', '.join(urls)}")
    start_monitoring()  # Redémarrer la surveillance

@bot.slash_command(
    name="removeurl",
    description="Supprime une URL de la liste.",
    guild_ids=GUILD_ID  # Remplacez par votre ID de serveur
)
async def remove_url(ctx, url_to_remove: str):
    global urls
    if url_to_remove in urls:
        urls.remove(url_to_remove)
        save_urls(urls)  # Sauvegarder les URLs mises à jour dans le fichier JSON
        await ctx.respond(f"L'URL {url_to_remove} a été supprimée de la liste.")
        
        # Arrêter tous les threads
        start_monitoring()  # Redémarrer la surveillance
    else:
        await ctx.respond(f"L'URL {url_to_remove} n'est pas dans la liste.")

@bot.slash_command(
    name="listurls",
    description="Affiche la liste des URLs surveillées.",
    guild_ids=GUILD_ID  # Remplacez par votre ID de serveur
)
async def list_urls(ctx):
    if urls:
        await ctx.respond(f"Liste des URLs surveillées : {', '.join(urls)}")
    else:
        await ctx.respond("Aucune URL n'est actuellement surveillée.")

def check_account(url):
     # Configurer les options pour le mode headless
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Activer le mode headless
    chrome_options.add_argument("--no-sandbox")  # Nécessaire pour certains environnements Linux
    chrome_options.add_argument("--disable-dev-shm-usage")  # Éviter les problèmes de mémoire partagée
    chrome_options.add_argument("--disable-gpu") 
    chrome_options.add_argument('log-level=3')
    service = Service(executable_path=CM().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)  
    account_exists = True

    while account_exists:
        # Vérifiez si l'événement d'arrêt a été déclenché
        if stop_event.is_set():
            print(f"Arrêt de la surveillance pour {url}.")
            driver.quit()
            break

        driver.get(url)

        # Attendre 5 secondes tout en vérifiant l'état de stop_event
        for _ in range(5):
            if stop_event.is_set():
                print(f"Arrêt de la surveillance pour {url}.")
                driver.quit()
                return
            time.sleep(1)  # Attendre 1 seconde à la fois

        if "login" in driver.current_url:
            print(f"Le compte {url} n'a pas changé de nom... Surveillance en cours")
            account_exists = True
        else:
            try:
                error_message = driver.find_element(By.XPATH, "//*[@id='react-root']/div/div/div[2]/main/div/div/div/div[1]/div/div[3]/div/div/div[2]/div/div[1]/span")
                # si error message contient attention ou caution alors return :
                # Obtenir le texte de l'élément
                error_message_text = error_message.text

                # Vérifier si le message d'erreur contient "attention" ou "caution"
                if "attention" in error_message_text.lower() or "caution" in error_message_text.lower():
                    print("Compte X restreint mais existant pour " + url)
                    return
                
                if error_message:
                    send_discord_message(f"Le compte de {url} a changé de nom. @everyone " + x_account_following_target)
                    # L'alerte a ete envoyer donc supprimer l'url pour ne pas envoyer d'autre alerte
                    global urls
                    urls.remove(url)
                    save_urls(urls)
                    # Arrêter ce thread
                    account_exists = False
                    driver.quit()
                    return
            except Exception as e:
                print(f"Le compte {url} n'a pas changé de nom... Surveillance en cours")
                account_exists = True

        # Attendre 8 secondes tout en vérifiant l'état de stop_event
        for _ in range(8):
            if stop_event.is_set():
                print(f"Arrêt de la surveillance pour {url}.")
                driver.quit()
                return
            time.sleep(1)  # Attendre 1 seconde à la fois

    driver.quit()

# Démarrer le bot
bot.run(TOKEN_BOT)

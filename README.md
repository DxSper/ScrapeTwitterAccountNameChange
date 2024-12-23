# Discord URL Monitor Bot

Ce bot Discord surveille une liste d'URLs x.com (twitter) et envoie des notifications via un webhook Discord lorsque des changements sont détectés. Il utilise Selenium pour accéder aux pages web et vérifier les changements.

## Fonctionnalités

- Surveille une liste d'URLs pour détecter les changements de nom de compte.
- Envoie des notifications sur Discord lorsqu'un changement est détecté.
- Permet de mettre à jour la liste des URLs à surveiller via des commandes slash.
- Affiche la liste actuelle des URLs surveillées.
- Supprime des URLs de la liste de surveillance.

## Prérequis

- Python 3.7 ou supérieur
- Bibliothèques Python externe :
  - `py-cord`
  - `selenium`
  - `requests`
  - `webdriver-manager`
  - `json`

## Instalation

- Assurez-vous d'avoir Python et Chrome installé sur votre machine.
- Modifier les valeurs dans config.py avec vos tokens, id et compte
- Modifier vos cibles dans urls.json
- Ouvrir un terminal dans le dossier du programme.
- Tapez les commandes suivantes :
```bash
pip install -r requirements.txt
python main.py
```

## Commandes du bot
- /seturls <url> : Ajoute un url à la liste des URLs à surveiller.
- /removeurl <url> : Supprime une URL de la liste.
- /listurls : Affiche la liste des URLs surveillées.
- /help : Affiche cette liste d'aide.

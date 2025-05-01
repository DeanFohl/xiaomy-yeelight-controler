# Yeelight et OpenRGB Controller

Ce projet est un script Python permettant de contrôler des ampoules Yeelight et des périphériques compatibles OpenRGB. Il permet de définir des couleurs, d'ajuster la luminosité, de lancer des animations et plus encore.

## Fonctionnalités

- Contrôle des ampoules Yeelight : allumage/extinction, réglage de la couleur, réglage de la luminosité.
- Contrôle des périphériques OpenRGB : réglage de la couleur.
- Lancement d'animations prédéfinies sur les ampoules Yeelight.
- Sélection de couleurs via un sélecteur de couleurs graphique.

## Prérequis

- Python 3.x

## Installation

1. Clonez ce dépôt sur votre machine locale :

    ```sh
    git clone https://github.com/DeanFohl/xiaomy-yeelight-controler
    cd votre-depot
    ```

2. Installez les dépendances nécessaires en utilisant le fichier `requirements.txt` :

    ```sh
    pip install -r requirements.txt
    ```

## Utilisation

Le script peut être exécuté en ligne de commande avec diverses options. Voici un aperçu des options disponibles :

```sh
usage: script.py [options]

Options:
  -h, --help            Affiche ce message d'aide.
  -i IP, --ip IP        Adresse IP de l'ampoule Yeelight.
  -a ACTION, --action ACTION
                        Action à effectuer : toggle, brightness+, brightness-, animation.
  -s SCENARIO, --scenario SCENARIO
                        Nom de l'animation à jouer.
  -l BRIGHTNESS, --brightness BRIGHTNESS
                        Niveau de luminosité (0-100).
  -c COLOR, --color COLOR
                        Couleur à définir (nom ou RGB).
  -n NAME, --name NAME  Nom de l'animation personnalisée.
  -d DURATION, --duration DURATION
                        Durée de l'animation en secondes.
  -p, --pc              Activer le contrôle des périphériques PC via OpenRGB.
  --cp                  Ouvrir le sélecteur de couleurs.

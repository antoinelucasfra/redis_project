# Projet Redis - Gestion de Stock de Sushis 🍣

Répertoire pour un projet de SGBD focalisé sur l'outil Redis.

**Auteurs :** @ChloéTellier, @OcéaneGuitton, @FlavieThévenard et @AntoineLucas

## 📋 Description

Ce projet démontre les capacités de Redis pour la gestion de stock en temps réel à travers un exemple de magasin de sushis. Il illustre :

- La création et manipulation de structures de données **hash** dans Redis
- L'utilisation de **transactions** (WATCH/MULTI/EXEC) pour des opérations atomiques
- Le **pipelining** pour des performances optimales
- La génération de 100 000 combinaisons de sushis avec 73 ingrédients différents

## 🚀 Installation

### Prérequis

- Python 3.9+
- Redis Server ([guide d'installation](https://redis.io/topics/quickstart))

### Installation des dépendances Python

```bash
# Cloner le projet
git clone https://github.com/antoinelucasfra/redis_project.git
cd redis_project

# Créer un environnement virtuel (recommandé)
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# ou .venv\Scripts\activate  # Windows

# Installer les dépendances
pip install -r requirements.txt
```

### Lancer Redis

```bash
# Linux
redis-server

# Vérifier la connexion
redis-cli ping  # Doit répondre "PONG"
```

## 📁 Structure du Projet

```
redis_project/
├── README.md
├── requirements.txt
├── redis_notebook.ipynb      # Notebook interactif avec explications
├── src/
│   ├── __init__.py
│   ├── config.py             # Configuration et constantes
│   └── sushi_store.py        # Logique métier principale
└── outputs/
    ├── redis_notebook.html   # Export HTML du notebook
    └── redis_notebook.py     # Export Python du notebook
```

## 💻 Utilisation

### Via le notebook Jupyter

Le notebook [`redis_notebook.ipynb`](https://github.com/antoinelucasfra/redis_project/blob/main/redis_notebook.ipynb) contient une démarche pédagogique complète.

```bash
jupyter notebook redis_notebook.ipynb
```

### Via le module Python

```python
from src import (
    get_redis_connection,
    generate_sushi_database,
    load_sushis_to_redis,
    buy_item,
    restock_item,
    get_inventory_info,
    find_sushis_with_ingredients,
)

# Connexion à Redis
r = get_redis_connection()

# Générer et charger les données
sushis = generate_sushi_database(count=1000)  # 1000 sushis pour un test rapide
load_sushis_to_redis(r, sushis)

# Acheter des sushis
buy_item(r, "sushi:5", 60)

# Restocker
restock_item(r, "sushi:9", 400)

# Trouver des sushis par ingrédients
from src import get_ingredients_info
ingredients_df = get_ingredients_info(r, len(sushis))
matching = find_sushis_with_ingredients(
    ingredients_df,
    ['saumon', 'avocat', 'wasabi']
)
```

## 📚 Documentation

### Fonctions principales

| Fonction | Description |
|----------|-------------|
| `generate_sushi_database()` | Génère N sushis avec ingrédients aléatoires |
| `load_sushis_to_redis()` | Charge les sushis dans Redis via pipeline |
| `buy_item()` | Achète des sushis (décrémente stock) |
| `restock_item()` | Réapprovisionne le stock |
| `get_inventory_info()` | Récupère stock et ventes en DataFrame |
| `find_sushis_with_ingredients()` | Recherche par ingrédients |

### Exceptions personnalisées

- `OutOfStockError` : Stock épuisé
- `TooMuchDemandError` : Demande > stock disponible
- `TooMuchStockError` : Stock déjà au maximum
- `NoPlaceAvailableError` : Restock partiel (max atteint)

## 🔗 Ressources

- [Documentation Redis](https://redis.io/documentation)
- [Redis Commands - Hash](https://redis.io/commands#hash)
- [Redis Pipelining](https://redis.io/topics/pipelining)
- [Tutoriel interactif Redis](https://try.redis.io/)

## 📄 Licence

Projet académique - Usage libre pour l'apprentissage.

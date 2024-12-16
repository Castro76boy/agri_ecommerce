# Agri E-commerce

Une plateforme de commerce électronique pour les produits agricoles, permettant aux agriculteurs de vendre directement aux consommateurs.

## Fonctionnalités

- 🌾 Catalogue de produits agricoles
- 🛒 Panier d'achat
- 👤 Gestion des profils (agriculteurs et clients)
- 📦 Système de commandes
- 💳 Paiement à la livraison
- 📱 Interface responsive

## Prérequis

- Python 3.8+
- PostgreSQL 13+
- Redis 6+
- Un compte AWS S3 (pour le stockage des médias)
- Un compte Sentry (pour le monitoring)

## Installation

1. Cloner le dépôt :
```bash
git clone [URL_DU_REPO]
cd agri_ecommerce
```

2. Créer un environnement virtuel :
```bash
python -m venv venv
source venv/bin/activate  # Sur Unix
venv\Scripts\activate     # Sur Windows
```

3. Installer les dépendances :
```bash
pip install -r requirements.txt
```

4. Configurer les variables d'environnement :
- Copier `.env.example` vers `.env`
- Remplir les variables dans `.env`

5. Initialiser la base de données :
```bash
python manage.py migrate
python manage.py createsuperuser
```

6. Lancer le serveur de développement :
```bash
python manage.py runserver
```

## Configuration de Production

1. Base de données :
- Installer PostgreSQL
- Créer une base de données
- Configurer les variables DB_* dans .env

2. Cache :
- Installer Redis
- Configurer REDIS_URL dans .env

3. Stockage :
- Créer un bucket AWS S3
- Configurer les variables AWS_* dans .env

4. Sécurité :
- Générer une nouvelle SECRET_KEY
- Configurer HTTPS
- Activer les paramètres de sécurité dans .env

5. Monitoring :
- Configurer Sentry
- Ajouter SENTRY_DSN dans .env

## Tests

Pour exécuter les tests :
```bash
python manage.py test
```

## Déploiement

1. Collecter les fichiers statiques :
```bash
python manage.py collectstatic
```

2. Appliquer les migrations :
```bash
python manage.py migrate
```

3. Lancer avec gunicorn :
```bash
gunicorn agri_ecommerce.wsgi:application
```

## Maintenance

- Sauvegarder régulièrement la base de données
- Surveiller les logs d'erreur via Sentry
- Mettre à jour les dépendances régulièrement
- Vérifier les performances avec les outils de monitoring

## Licence

Ce projet est sous licence [VOTRE_LICENCE]

## Contact

Pour toute question ou support, contactez [VOTRE_CONTACT]

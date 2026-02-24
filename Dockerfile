# Utiliser une image Python officielle comme base
FROM python:3.10-slim

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Copier les fichiers de dépendances et installer
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le reste des fichiers de l'application
COPY . .

# Exposer le port par défaut de Flask
EXPOSE 5000

# Commande par défaut pour lancer l'application
# 1. Générer la base de données (si elle n'existe pas)
# 2. Lancer le script principal qui démarre l'API
CMD python3 generate_data.py && python3 mock_bank_data.py
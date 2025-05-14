# Utiliser une image Python légère
FROM python:3.9-slim

# Définir une variable d'environnement pour que les logs Python s'affichent immédiatement
ENV PYTHONUNBUFFERED=1

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Copier le fichier des dépendances et les installer
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copier le script du producteur dans le répertoire de travail
COPY producer.py .

# Commande pour exécuter le script Python lorsque le conteneur démarre
CMD ["python", "producer.py"] 
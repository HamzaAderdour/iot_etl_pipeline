# Pipeline ETL pour Données de Capteurs IoT

## Objectif du Projet

Ce projet vise à implémenter un pipeline ETL (Extract, Transform, Load) complet pour la collecte, le traitement et l'analyse de données de capteurs IoT (température, humidité, pollution) provenant d'une ville intelligente. Les données sont traitées en temps réel, nettoyées, agrégées et rendues accessibles via une API. Le système permet également la consultation de données historiques.

## Technologies Utilisées

-   **Streaming de Données :** Apache Kafka
-   **Orchestration ETL :** Apache Airflow
-   **Traitement Distribué :** Celery avec Redis comme broker/backend
-   **Stockage de Données Agrégées :** Elasticsearch
-   **Exposition API :** FastAPI
-   **Conteneurisation :** Docker & Docker Compose
-   **Générateur de Données (Simulation) :** Python (à implémenter)

## Structure du Projet

Le projet est organisé en modules, chacun représentant un composant clé du pipeline. Chaque module aura son propre `Dockerfile` pour construire l'image Docker correspondante.

```
iot_etl_pipeline/
├── airflow/              # Configurations Airflow, DAGs, plugins
│   ├── dags/             # Contient les définitions des DAGs Airflow
│   ├── logs/             # (Généré par Airflow, généralement dans .gitignore)
│   ├── plugins/          # Plugins Airflow personnalisés
│   └── Dockerfile        # Dockerfile pour le service Airflow (webserver, scheduler, worker)
├── celery/               # Logique de traitement (workers Celery), tâches de nettoyage/agrégation
│   ├── tasks/            # Modules Python définissant les tâches Celery
│   └── Dockerfile        # Dockerfile pour les workers Celery
├── data_generator/       # Simulateur de capteurs IoT (producteur Kafka)
│   └── Dockerfile        # Dockerfile pour le service de génération de données
├── elasticsearch/        # Configuration Elasticsearch (ex: templates d'index, scripts d'init)
│                       # Souvent, une image officielle est utilisée directement dans docker-compose.yml,
│                       # mais ce dossier peut contenir des configurations spécifiques.
│   └── Dockerfile        # (Optionnel, si une image custom est nécessaire)
├── fastapi/              # Application API FastAPI pour l'accès aux données
│   ├── app/              # Code source de l'application FastAPI
│   └── Dockerfile        # Dockerfile pour le service FastAPI
├── kafka/                # Configuration Kafka (ex: scripts de création de topics)
│                       # Similaire à Elasticsearch, une image officielle est souvent suffisante.
│   └── Dockerfile        # (Optionnel, si une image custom est nécessaire)
├── .env                  # Variables d'environnement pour la configuration des services
├── .gitignore            # Fichiers et dossiers à ignorer par Git
├── docker-compose.yml    # Définition et orchestration des services Docker (À VENIR)
└── README.md             # Ce fichier
```

## Comment Lancer le Projet (Instructions Préliminaires)

Ce projet est conçu pour être entièrement exécuté avec Docker et Docker Compose.

1.  **Prérequis :**
    *   Docker installé ([https://www.docker.com/get-started](https://www.docker.com/get-started))
    *   Docker Compose installé (généralement inclus avec Docker Desktop).

2.  **Configuration :**
    *   Assurez-vous que le fichier `.env` à la racine du projet (`iot_etl_pipeline/.env`) est correctement configuré. Vous devrez notamment y ajouter une `AIRFLOW__CORE__FERNET_KEY` valide.
    *   Vérifiez que les ports définis dans `.env` (et qui seront utilisés dans `docker-compose.yml`) ne sont pas déjà utilisés sur votre machine.

3.  **Lancement (Instructions futures) :**
    Une fois le fichier `docker-compose.yml` et les `Dockerfile` créés, vous pourrez lancer l'ensemble des services avec :
    ```bash
    # Naviguer à la racine du projet iot_etl_pipeline/
    # cd iot_etl_pipeline

    # Construire les images et démarrer les conteneurs en mode détaché
    docker-compose up -d --build
    ```

4.  **Arrêt (Instructions futures) :**
    Pour arrêter tous les services :
    ```bash
    docker-compose down
    ```

## Étapes Suivantes

1.  **Définir les `Dockerfile`** pour chaque service dans leurs répertoires respectifs.
2.  **Créer le fichier `docker-compose.yml`** à la racine (`iot_etl_pipeline/`) pour orchestrer tous les services (Kafka, Zookeeper, Airflow (scheduler, webserver, worker), Celery worker, Redis, Elasticsearch, FastAPI, générateur de données).
3.  **Implémenter la logique métier** pour chaque composant :
    *   Scripts du générateur de données.
    *   DAGs Airflow pour l'orchestration.
    *   Tâches Celery pour le nettoyage et l'agrégation.
    *   Endpoints FastAPI pour l'exposition des données. 
# Pipeline ETL pour Données de Capteurs IoT

## Objectif du Projet

Ce projet vise à implémenter un pipeline ETL (Extract, Transform, Load) complet pour la collecte, le traitement et l'analyse de données de capteurs IoT (température, humidité, pollution) provenant d'une ville intelligente. Les données sont traitées en temps réel, nettoyées, agrégées et rendues accessibles via une API. Le système permet également la consultation de données historiques.

## Technologies Utilisées

-   **Streaming de Données :** Apache Kafka
-   **Orchestration ETL :** Apache Airflow (implémenté)
-   **Traitement Distribué :** Celery avec Redis comme broker/backend (prochaine étape)
-   **Stockage de Données Agrégées :** Elasticsearch (prochaine étape)
-   **Exposition API :** FastAPI (prochaine étape)
-   **Conteneurisation :** Docker & Docker Compose
-   **Générateur de Données (Simulation) :** Python (implémenté)

## Structure du Projet

Le projet est organisé en modules, chacun représentant un composant clé du pipeline. Chaque module aura son propre `Dockerfile` pour construire l'image Docker correspondante.

```
iot_etl_pipeline/
├── airflow/              # Configurations Airflow, DAGs, plugins
│   ├── dags/             # Contient les définitions des DAGs Airflow
│   ├── logs/             # (Généré par Airflow, généralement dans .gitignore)
│   ├── plugins/          # Plugins Airflow personnalisés
│   └── Dockerfile        # Dockerfile pour le service Airflow
├── celery/               # Logique de traitement (workers Celery), tâches de nettoyage/agrégation
│   ├── tasks/            # Modules Python définissant les tâches Celery
│   └── Dockerfile        # Dockerfile pour les workers Celery - À VENIR
├── data_generator/       # Simulateur de capteurs IoT (producteur Kafka)
│   ├── producer.py
│   ├── requirements.txt
│   └── Dockerfile
├── elasticsearch/        # Configuration Elasticsearch
│   └── Dockerfile        # (Optionnel, si une image custom est nécessaire) - À VENIR
├── fastapi/              # Application API FastAPI pour l'accès aux données
│   ├── app/              # Code source de l'application FastAPI
│   └── Dockerfile        # Dockerfile pour le service FastAPI - À VENIR
├── kafka/                # Configuration Kafka
│   └── Dockerfile        # (Optionnel, si une image custom est nécessaire)
├── .env                  # Variables d'environnement pour la configuration des services
├── .gitignore            # Fichiers et dossiers à ignorer par Git
├── docker-compose.yml    # Définition et orchestration des services Docker
└── README.md             # Ce fichier
```

## État Actuel du Projet

Les composants suivants sont configurés et fonctionnels :
-   **Zookeeper & Kafka :** Pour le streaming des données.
-   **Data Generator :** Un producteur Python qui simule des données de capteurs IoT pour la ville de Casablanca et les envoie au topic Kafka `iot_sensor_data`.
-   **Airflow :** Orchestration du pipeline ETL avec un DAG qui s'exécute toutes les 10 minutes.

## Orchestration avec Airflow

Le pipeline ETL est orchestré par Apache Airflow, qui exécute un DAG toutes les 10 minutes. Le DAG comprend trois tâches principales :

1. **extract_data_from_kafka :**
   - Lit les messages du topic Kafka `iot_sensor_data`
   - Utilise un consumer Kafka pour récupérer les données
   - Gère les timeouts et les erreurs de connexion

2. **send_to_celery_for_transformation :**
   - Envoie les données brutes à Celery pour traitement
   - Utilise Redis comme broker pour Celery
   - Gère les cas où aucun message n'est disponible

3. **load_to_elasticsearch :**
   - Récupère les données transformées depuis Celery
   - Indexe les données dans Elasticsearch
   - Crée des index journaliers pour une meilleure organisation

### Accès à l'Interface Airflow

1. L'interface web Airflow est accessible à l'adresse : `http://localhost:8080`
2. Identifiants par défaut :
   - Username : `airflow`
   - Password : `airflow`

### Monitoring et Logs

- Les logs des tâches sont disponibles dans l'interface web Airflow
- Les logs des conteneurs peuvent être consultés via :
  ```bash
  docker-compose logs -f airflow-webserver
  docker-compose logs -f airflow-scheduler
  docker-compose logs -f airflow-worker
  ```

## Comment Lancer le Projet

Ce projet est conçu pour être entièrement exécuté avec Docker et Docker Compose.

1.  **Prérequis :**
    *   Docker installé ([https://www.docker.com/get-started](https://www.docker.com/get-started))
    *   Docker Compose installé (généralement inclus avec Docker Desktop).

2.  **Configuration :**
    *   Assurez-vous que le fichier `.env` à la racine du projet (`iot_etl_pipeline/.env`) est correctement configuré.
    *   Vérifiez que les ports définis dans `.env` et `docker-compose.yml` ne sont pas déjà utilisés sur votre machine.

3.  **Lancement :**
    Naviguez à la racine du projet `iot_etl_pipeline/` et exécutez :
    ```bash
    # Construire les images (si nécessaire) et démarrer les conteneurs en mode détaché
    docker-compose up --build -d
    ```
    Cela lancera tous les services, y compris Airflow.

4.  **Vérification :**
    Pour voir les logs des services :
    ```bash
    docker-compose logs -f
    ```
    Accédez à l'interface Airflow à `http://localhost:8080` pour surveiller l'exécution du DAG.

5.  **Arrêt :**
    Pour arrêter tous les services :
    ```bash
    docker-compose down
    ```
    Pour arrêter et supprimer les volumes :
    ```bash
    docker-compose down -v
    ```

## Étapes Suivantes

Les prochaines étapes de développement se concentreront sur l'implémentation des composants restants du pipeline ETL :

1.  **Celery & Redis :**
    *   Mettre en place les workers Celery pour le nettoyage et l'agrégation des données.
    *   Configurer Redis comme broker pour Celery.
    *   Intégrer Celery avec Airflow.

2.  **Elasticsearch :**
    *   Configurer le service Elasticsearch.
    *   Développer les tâches pour charger les données agrégées dans Elasticsearch.

3.  **FastAPI :**
    *   Développer l'API pour exposer les données brutes et agrégées.

4.  **Affiner la logique métier** pour chaque composant (nettoyage plus poussé, types d'agrégations spécifiques, etc.). 
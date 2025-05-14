# Pipeline ETL pour Données de Capteurs IoT

## Objectif du Projet

Ce projet vise à implémenter un pipeline ETL (Extract, Transform, Load) complet pour la collecte, le traitement et l'analyse de données de capteurs IoT (température, humidité, pollution) provenant d'une ville intelligente. Les données sont traitées en temps réel, nettoyées, agrégées et rendues accessibles via une API. Le système permet également la consultation de données historiques.

## Technologies Utilisées

-   **Streaming de Données :** Apache Kafka
-   **Orchestration ETL :** Apache Airflow (prochaine étape)
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
│   └── Dockerfile        # Dockerfile pour le service Airflow (webserver, scheduler, worker) - À VENIR
├── celery/               # Logique de traitement (workers Celery), tâches de nettoyage/agrégation
│   ├── tasks/            # Modules Python définissant les tâches Celery
│   └── Dockerfile        # Dockerfile pour les workers Celery - À VENIR
├── data_generator/       # Simulateur de capteurs IoT (producteur Kafka)
│   ├── producer.py
│   ├── requirements.txt
│   └── Dockerfile
├── elasticsearch/        # Configuration Elasticsearch (ex: templates d'index, scripts d'init)
│                       # Souvent, une image officielle est utilisée directement dans docker-compose.yml,
│                       # mais ce dossier peut contenir des configurations spécifiques.
│   └── Dockerfile        # (Optionnel, si une image custom est nécessaire) - À VENIR
├── fastapi/              # Application API FastAPI pour l'accès aux données
│   ├── app/              # Code source de l'application FastAPI
│   └── Dockerfile        # Dockerfile pour le service FastAPI - À VENIR
├── kafka/                # Configuration Kafka (ex: scripts de création de topics)
│                       # Similaire à Elasticsearch, une image officielle est souvent suffisante.
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

## Comment Lancer le Projet

Ce projet est conçu pour être entièrement exécuté avec Docker et Docker Compose.

1.  **Prérequis :**
    *   Docker installé ([https://www.docker.com/get-started](https://www.docker.com/get-started))
    *   Docker Compose installé (généralement inclus avec Docker Desktop).

2.  **Configuration :**
    *   Assurez-vous que le fichier `.env` à la racine du projet (`iot_etl_pipeline/.env`) est correctement configuré. Les variables importantes pour l'étape actuelle sont `KAFKA_BROKERS`, `KAFKA_SENSOR_DATA_TOPIC`, `DATA_GENERATOR_INTERVAL_SECONDS`.
    *   (Optionnel) Pour que Kafka crée le topic automatiquement au démarrage, configurez `KAFKA_CREATE_TOPICS` dans le `.env` (ex: `KAFKA_CREATE_TOPICS="iot_sensor_data:1:1"`).
    *   Vous devrez toujours générer et ajouter une `AIRFLOW__CORE__FERNET_KEY` valide dans `.env` pour les futures étapes avec Airflow.
    *   Vérifiez que les ports définis dans `.env` et `docker-compose.yml` (ex: `2181` pour Zookeeper, `9093` pour l'accès externe à Kafka) ne sont pas déjà utilisés sur votre machine.

3.  **Lancement :**
    Naviguez à la racine du projet `iot_etl_pipeline/` et exécutez :
    ```bash
    # Construire les images (si nécessaire) et démarrer les conteneurs en mode détaché
    docker-compose up --build -d
    ```
    Cela lancera Zookeeper, Kafka, et le `data_generator`.

4.  **Vérification :**
    Pour voir les logs du générateur de données (et des autres services) :
    ```bash
    docker-compose logs -f data_generator
    # Ou pour tous les services
    docker-compose logs -f
    ```
    Vous devriez voir le `data_generator` envoyer des messages à Kafka.

5.  **Arrêt :**
    Pour arrêter tous les services :
    ```bash
    docker-compose down
    ```
    Pour arrêter et supprimer les volumes (si vous voulez repartir de zéro pour Kafka par exemple) :
    ```bash
    docker-compose down -v
    ```

## Étapes Suivantes

Les prochaines étapes de développement se concentreront sur l'implémentation des composants restants du pipeline ETL :

1.  **Airflow :**
    *   Configurer les services Airflow (scheduler, webserver, worker - si CeleryExecutor).
    *   Développer les DAGs pour orchestrer le flux de données depuis Kafka.
2.  **Celery & Redis :**
    *   Mettre en place les workers Celery pour le nettoyage et l'agrégation des données.
    *   Configurer Redis comme broker pour Celery (et pour le backend de résultats si besoin).
    *   Intégrer Celery avec Airflow (via `CeleryExecutor` ou `CeleryKubernetesExecutor` pour Airflow, ou des `PythonOperators` qui déclenchent des tâches Celery).
3.  **Elasticsearch :**
    *   Configurer le service Elasticsearch.
    *   Développer les tâches (probablement dans Celery/Airflow) pour charger les données agrégées dans Elasticsearch.
4.  **FastAPI :**
    *   Développer l'API pour exposer les données brutes (potentiellement depuis Kafka ou une base temporaire) et agrégées (depuis Elasticsearch).
5.  **Affiner la logique métier** pour chaque composant (nettoyage plus poussé, types d'agrégations spécifiques, etc.). 
FROM apache/airflow:2.8.1

USER root

# Installation des dépendances système
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

USER airflow

# Installation des dépendances Python
COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt

# Configuration des variables d'environnement
ENV AIRFLOW_HOME=/opt/airflow
ENV PYTHONPATH=/opt/airflow

# Création des dossiers nécessaires
RUN mkdir -p ${AIRFLOW_HOME}/dags \
    && mkdir -p ${AIRFLOW_HOME}/logs \
    && mkdir -p ${AIRFLOW_HOME}/plugins

# Copie des fichiers de configuration
COPY config/airflow.cfg ${AIRFLOW_HOME}/airflow.cfg

# Permissions
RUN chown -R airflow:root ${AIRFLOW_HOME} 
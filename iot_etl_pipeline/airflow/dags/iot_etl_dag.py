from datetime import datetime, timedelta
import os
import json
import logging
from typing import List, Dict, Any

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.models import Variable
from dotenv import load_dotenv

from kafka import KafkaConsumer
from celery import Celery
from elasticsearch import Elasticsearch

# Configuration du logging
logger = logging.getLogger(__name__)

# Chargement des variables d'environnement
load_dotenv()

# Configuration Celery
celery_app = Celery(
    'iot_etl',
    broker=os.getenv('CELERY_BROKER_URL', 'redis://redis:6379/0'),
    backend=os.getenv('CELERY_RESULT_BACKEND', 'redis://redis:6379/0')
)

# Configuration Elasticsearch
es = Elasticsearch(
    hosts=[os.getenv('ELASTICSEARCH_HOST', 'http://elasticsearch:9200')]
)

def extract_data_from_kafka(**context) -> List[Dict[str, Any]]:
    """
    Extrait les données du topic Kafka.
    """
    logger.info("Début de l'extraction des données depuis Kafka")
    
    consumer = KafkaConsumer(
        os.getenv('KAFKA_SENSOR_DATA_TOPIC', 'iot_sensor_data'),
        bootstrap_servers=os.getenv('KAFKA_BROKERS', 'kafka:9092'),
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id='airflow_consumer',
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )
    
    messages = []
    try:
        # Lecture des messages pendant 30 secondes maximum
        start_time = datetime.now()
        while (datetime.now() - start_time) < timedelta(seconds=30):
            msg = next(consumer, None)
            if msg is None:
                break
            messages.append(msg.value)
            logger.info(f"Message reçu: {msg.value}")
    except Exception as e:
        logger.error(f"Erreur lors de la lecture des messages Kafka: {str(e)}")
        raise
    finally:
        consumer.close()
    
    logger.info(f"Extraction terminée. {len(messages)} messages récupérés.")
    return messages

def send_to_celery_for_transformation(**context) -> str:
    """
    Envoie les données à Celery pour transformation.
    """
    logger.info("Envoi des données à Celery pour transformation")
    
    ti = context['ti']
    messages = ti.xcom_pull(task_ids='extract_data_from_kafka')
    
    if not messages:
        logger.warning("Aucun message à traiter")
        return "Aucun message à traiter"
    
    # Envoi de la tâche à Celery
    task = celery_app.send_task(
        'tasks.transform_sensor_data',
        args=[messages],
        queue='sensor_data'
    )
    
    logger.info(f"Tâche Celery créée avec l'ID: {task.id}")
    return task.id

def load_to_elasticsearch(**context) -> None:
    """
    Charge les données transformées dans Elasticsearch.
    """
    logger.info("Chargement des données dans Elasticsearch")
    
    ti = context['ti']
    task_id = ti.xcom_pull(task_ids='send_to_celery_for_transformation')
    
    if task_id == "Aucun message à traiter":
        logger.info("Aucune donnée à charger dans Elasticsearch")
        return
    
    # Récupération du résultat de la tâche Celery
    result = celery_app.AsyncResult(task_id)
    transformed_data = result.get(timeout=300)  # Timeout de 5 minutes
    
    if not transformed_data:
        logger.warning("Aucune donnée transformée à charger")
        return
    
    # Indexation dans Elasticsearch
    index_name = f"sensor_data_{datetime.now().strftime('%Y%m%d')}"
    
    try:
        for doc in transformed_data:
            es.index(
                index=index_name,
                document=doc,
                id=f"{doc['sensor_id']}_{doc['timestamp']}"
            )
        logger.info(f"Données chargées avec succès dans l'index {index_name}")
    except Exception as e:
        logger.error(f"Erreur lors du chargement dans Elasticsearch: {str(e)}")
        raise

# Définition du DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'iot_etl_pipeline',
    default_args=default_args,
    description='Pipeline ETL pour les données de capteurs IoT',
    schedule_interval='*/10 * * * *',  # Toutes les 10 minutes
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['iot', 'etl'],
)

# Définition des tâches
extract_task = PythonOperator(
    task_id='extract_data_from_kafka',
    python_callable=extract_data_from_kafka,
    provide_context=True,
    dag=dag,
)

transform_task = PythonOperator(
    task_id='send_to_celery_for_transformation',
    python_callable=send_to_celery_for_transformation,
    provide_context=True,
    dag=dag,
)

load_task = PythonOperator(
    task_id='load_to_elasticsearch',
    python_callable=load_to_elasticsearch,
    provide_context=True,
    dag=dag,
)

# Définition des dépendances
extract_task >> transform_task >> load_task 
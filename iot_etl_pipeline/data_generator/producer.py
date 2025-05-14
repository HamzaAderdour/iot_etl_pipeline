import os
import json
import time
import random
import uuid
from datetime import datetime, timezone
from kafka import KafkaProducer
from kafka.errors import KafkaError, NoBrokersAvailable

# Configuration depuis les variables d'environnement avec des valeurs par défaut
KAFKA_BROKERS = os.getenv('KAFKA_BROKERS', 'kafka:9092')
KAFKA_TOPIC = os.getenv('KAFKA_SENSOR_DATA_TOPIC', 'iot_sensor_data') # Utilisé depuis .env
GENERATION_INTERVAL = int(os.getenv('DATA_GENERATOR_INTERVAL_SECONDS', 10))

QUARTIERS_CASABLANCA = [
    'Maarif', 'Anfa', 'Sidi Bernoussi', 'Hay Hassani', 'Ain Sebaa', 
    'Derb Sultan', 'Hay Mohammadi', 'Gauthier', 'Oulfa', 'Sbata',
    'Roches Noires', 'Belvédère', 'Ain Chock', 'Mers Sultan', 'Bourgogne'
]
SENSORS_PER_QUARTIER = 2 # Nombre de capteurs simulés par quartier

def get_kafka_producer(brokers):
    """Tente de se connecter à Kafka avec des tentatives répétées."""
    while True:
        try:
            producer = KafkaProducer(
                bootstrap_servers=brokers.split(','),
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                retries=5,  # Nombre de tentatives d'envoi d'un message
                request_timeout_ms=30000, # Timeout pour une requête individuelle
                api_version_auto_timeout_ms=30000 # Timeout pour la découverte de la version de l'API
            )
            print(f"Connecté avec succès à Kafka: {brokers}")
            return producer
        except NoBrokersAvailable:
            print(f"Les brokers Kafka à {brokers} ne sont pas disponibles. Nouvelle tentative dans 10 secondes...")
            time.sleep(10)
        except Exception as e:
            print(f"Erreur inattendue lors de la connexion à Kafka: {e}. Nouvelle tentative dans 10 secondes...")
            time.sleep(10)

def generate_sensor_id(quartier, index):
    """Génère un ID de capteur unique."""
    quartier_slug = quartier.lower().replace(' ', '-')
    return f"sensor-{quartier_slug}-{uuid.uuid4().hex[:6]}-{index}"

def generate_realistic_value(base_value, normal_min, normal_max,
                             outlier_values=None, format_error_values=None,
                             overall_error_rate=0.05, 
                             null_rate_within_error=0.2, 
                             format_error_rate_within_error=0.2
                            ):
    """Génère une valeur réaliste, incluant des erreurs et des valeurs aberrantes."""
    if random.random() < overall_error_rate:
        # Cas d'erreur
        error_type_rand = random.random()
        if error_type_rand < null_rate_within_error and null_rate_within_error > 0:
            return None
        elif error_type_rand < (null_rate_within_error + format_error_rate_within_error) and \
             format_error_values and format_error_rate_within_error > 0:
            return random.choice(format_error_values)
        elif outlier_values: # Les erreurs restantes deviennent des valeurs aberrantes si possible
            return random.choice(outlier_values)
        else: # Fallback si pas de valeurs aberrantes définies mais c'est une erreur
            return None 
    else:
        # Valeur normale avec un peu de bruit (+-10% de la plage normale)
        noise_range = (normal_max - normal_min) * 0.10 
        value = base_value + random.uniform(-noise_range, noise_range)
        return round(max(normal_min, min(normal_max, value)), 2)

def simulate_sensor_data(sensor_id, quartier):
    """Simule un ensemble de données pour un capteur."""
    timestamp = datetime.now(timezone.utc).isoformat()

    # 2% de chance que le capteur soit hors ligne
    if random.random() < 0.02:
        return {
            "sensor_id": sensor_id,
            "quartier": quartier,
            "timestamp": timestamp,
            "temperature": None,
            "humidite": None,
            "pollution": None,
            "status": "offline"
        }

    # Température: base entre 15-30°C, plus variations
    base_temp = random.uniform(15, 30)  
    temperature = generate_realistic_value(base_temp, 10.0, 45.0,
                                           outlier_values=[-50.0, 1000.0],
                                           format_error_values=["chaud", "erreur_lecture_temp"],
                                           overall_error_rate=0.04, null_rate_within_error=0.25, format_error_rate_within_error=0.25)

    # Humidité: base entre 40-70%
    base_humidity = random.uniform(40, 70)
    humidity = generate_realistic_value(base_humidity, 20.0, 90.0,
                                        outlier_values=[0.0, 200.0],
                                        format_error_values=["tres_humide", "sec"],
                                        overall_error_rate=0.03, null_rate_within_error=0.3, format_error_rate_within_error=0.3)

    # Pollution (AQI): base entre 30-100
    base_pollution = random.uniform(30, 100)
    pollution = generate_realistic_value(base_pollution, 10, 200, # Plage normale
                                         outlier_values=[5, 500, 700], # Pics et erreurs
                                         format_error_values=["modere", "eleve", "inconnu"],
                                         overall_error_rate=0.04, null_rate_within_error=0.2, format_error_rate_within_error=0.2)
    if isinstance(pollution, float): # L'AQI est généralement un entier
        pollution = int(round(pollution))


    return {
        "sensor_id": sensor_id,
        "quartier": quartier,
        "timestamp": timestamp,
        "temperature": temperature,
        "humidite": humidity,
        "pollution": pollution,
        "status": "online"
    }

if __name__ == "__main__":
    print("Démarrage du producteur de données de capteurs...")
    print(f"KAFKA_BROKERS: {KAFKA_BROKERS}")
    print(f"KAFKA_TOPIC: {KAFKA_TOPIC}")
    print(f"GENERATION_INTERVAL: {GENERATION_INTERVAL} secondes")

    kafka_producer = get_kafka_producer(KAFKA_BROKERS)
    
    all_sensors = []
    for q in QUARTIERS_CASABLANCA:
        for i in range(SENSORS_PER_QUARTIER):
            all_sensors.append({"id": generate_sensor_id(q, i), "quartier": q})

    if not all_sensors:
        print("Erreur: Aucun capteur initialisé. Arrêt.")
        exit(1)
    
    print(f"Génération de données pour {len(all_sensors)} capteurs uniques.")

    try:
        while True:
            # Sélectionne un capteur au hasard pour envoyer des données
            selected_sensor_info = random.choice(all_sensors)
            
            data_payload = simulate_sensor_data(selected_sensor_info["id"], selected_sensor_info["quartier"])
            
            print(f"Envoi des données: {data_payload}")
            kafka_producer.send(KAFKA_TOPIC, value=data_payload)
            kafka_producer.flush() # S'assure que les messages sont envoyés

            # Simule des données dupliquées (1% de chance)
            if random.random() < 0.01:
                time.sleep(0.1) # Petite pause avant d'envoyer le duplicata
                print(f"Envoi DUPLICATA: {data_payload}")
                kafka_producer.send(KAFKA_TOPIC, value=data_payload)
                kafka_producer.flush()
            
            time.sleep(GENERATION_INTERVAL) # Attend avant d'envoyer la prochaine donnée

    except KeyboardInterrupt:
        print("Arrêt du producteur...")
    except Exception as e:
        print(f"Erreur critique dans la boucle principale: {e}")
    finally:
        if kafka_producer:
            print("Fermeture du producteur Kafka.")
            kafka_producer.close() 
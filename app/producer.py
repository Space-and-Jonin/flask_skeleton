import json
import loguru
from config import Config
from kafka import KafkaProducer
from kafka.errors import KafkaError

bootstrap_servers = Config.KAFKA_BOOTSTRAP_SERVERS.split("|")


def json_serializer(data):
    return json.dumps(data).encode("UTF-8")


def get_partition(key, all, available):
    return 0


def publish_to_kafka(topic, value):
    producer = KafkaProducer(
        bootstrap_servers=bootstrap_servers,
        value_serializer=json_serializer,
        partitioner=get_partition,
    )
    try:
        producer.send(topic=topic, value=value)
        return True
    except KafkaError as e:
        loguru.Logger.error(
            f"Failed to publish record on to Kafka broker with error {e}"
        )
        return False

import json
import os
from kafka import KafkaConsumer

KAFKA_SUBSCRIPTIONS = os.getenv("KAFKA_SUBSCRIPTIONS")
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS")
KAFKA_CONSUMER_GROUP_ID = os.getenv("KAFKA_CONSUMER_GROUP_ID")
subscriptions = KAFKA_SUBSCRIPTIONS.split("|")
bootstrap_servers = KAFKA_BOOTSTRAP_SERVERS.split("|")


consumer = KafkaConsumer(
    bootstrap_servers=bootstrap_servers,
    auto_offset_reset="earliest",
    group_id=KAFKA_CONSUMER_GROUP_ID,
)

consumer.subscribe(subscriptions)
print("starting consumer...")

for msg in consumer:
    print(msg.topic)
    data = json.loads(msg.value)

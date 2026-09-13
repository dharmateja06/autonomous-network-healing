import json

from kafka import KafkaProducer


KAFKA_SERVER = "localhost:19092"
TOPIC = "network-alarms"


producer = KafkaProducer(
    bootstrap_servers=[KAFKA_SERVER],
    value_serializer=lambda value: json.dumps(value).encode("utf-8"),
)


def publish_alarm(alarm):
    print("\nPublishing alarm to Kafka...")

    future = producer.send(
        TOPIC,
        value=alarm,
    )

    metadata = future.get(timeout=10)

    print(
        f"Alarm published successfully "
        f"to {metadata.topic} "
        f"partition {metadata.partition} "
        f"offset {metadata.offset}"
    )


if __name__ == "__main__":

    test_alarm = {
        "alarm_id": "ALM-KAFKA-TEST",
        "link": "R1-R2",
        "device": "r1",
        "interface": "eth1",
        "fault_type": "INTERFACE_DOWN",
        "severity": "CRITICAL",
        "status": "ACTIVE",
    }

    publish_alarm(test_alarm)

    producer.flush()
    producer.close()

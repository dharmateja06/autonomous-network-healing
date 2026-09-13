import json
import subprocess

from kafka import KafkaConsumer


KAFKA_SERVER = "localhost:19092"
TOPIC = "network-alarms"


consumer = KafkaConsumer(
    TOPIC,
    bootstrap_servers=[KAFKA_SERVER],
    auto_offset_reset="earliest",
    enable_auto_commit=True,
    group_id="anh-rca-final-test-001",
    value_deserializer=lambda value: json.loads(
        value.decode("utf-8")
    ),
)


print("========================================")
print("       KAFKA RCA CONSUMER")
print("========================================")
print(f"Listening to topic: {TOPIC}")
print("Waiting for network alarms...\n")


for message in consumer:

    alarm = message.value

    print("\n========================================")
    print("          ALARM RECEIVED")
    print("========================================")

    print(json.dumps(alarm, indent=2))

    link = alarm.get("link")

    if not link:
        print("ERROR: Alarm does not contain a link.")
        continue

    print(f"\nStarting RCA for: {link}")

    rca_result = subprocess.run(
        [
            "python",
            "rca/rca_engine.py",
            link,
        ],
        capture_output=True,
        text=True,
    )

    print(rca_result.stdout)

    if rca_result.returncode != 0:
        print(
            f"RCA FAILED: Could not confirm fault for {link}"
        )
        continue

    print(
        f"RCA SUCCESS: Root cause identified for {link}"
    )

    print("\nStarting Autonomous Healing...")

    healing_result = subprocess.run(
        [
            "python",
            "-m",
            "healing.healing_engine",
            link,
        ],
        text=True,
    )

    if healing_result.returncode == 0:

        print(
            f"\nAUTONOMOUS HEALING COMPLETED: {link}"
        )

    else:

        print(
            f"\nAUTONOMOUS HEALING FAILED: {link}"
        )

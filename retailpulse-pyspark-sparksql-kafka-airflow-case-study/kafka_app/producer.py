from __future__ import annotations

import json
from pathlib import Path

from confluent_kafka import Producer


def delivery_report(error, message) -> None:
    if error is not None:
        print(f"Delivery failed: {error}")
    else:
        key = message.key().decode("utf-8") if message.key() else None
        print(
            f"Delivered key={key} "
            f"to {message.topic()}[{message.partition()}] "
            f"offset={message.offset()}"
        )


def publish_events(
    input_file: str,
    bootstrap_servers: str,
    topic: str,
) -> int:
    input_path = Path(input_file)

    if not input_path.exists():
        raise FileNotFoundError(input_path)

    producer = Producer(
        {
            "bootstrap.servers": bootstrap_servers,
            "client.id": "retailpulse-summary-producer",
            "enable.idempotence": True,
            "acks": "all",
        }
    )

    sent = 0

    with input_path.open("r", encoding="utf-8") as source:
        for line_number, line in enumerate(source, start=1):
            line = line.strip()

            if not line:
                continue

            try:
                event = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"Invalid JSON on line {line_number}: {exc}"
                ) from exc

            if "event_id" not in event:
                raise ValueError(
                    f"Missing 'event_id' on line {line_number}"
                )

            producer.produce(
                topic=topic,
                key=str(event["event_id"]).encode("utf-8"),
                value=json.dumps(event).encode("utf-8"),
                callback=delivery_report,
            )

            producer.poll(0)
            sent += 1

    remaining = producer.flush()

    if remaining > 0:
        raise RuntimeError(
            f"{remaining} Kafka messages were not delivered"
        )

    print(f"Published {sent} events to {topic}")

    return sent
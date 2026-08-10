from __future__ import annotations

import json
import time
from pathlib import Path

from confluent_kafka import Consumer, KafkaError


def consume_events(
    bootstrap_servers: str,
    topic: str,
    group_id: str,
    output_file: str,
    max_messages: int = 30,
    timeout_seconds: int = 30,
) -> int:
    consumer = Consumer(
        {
            "bootstrap.servers": bootstrap_servers,
            "group.id": group_id,
            "auto.offset.reset": "earliest",
            "enable.auto.commit": False,
        }
    )

    consumer.subscribe([topic])

    output_path = Path(output_file)

    count = 0
    started = time.time()

    try:
        with output_path.open("w", encoding="utf-8") as target:
            while count < max_messages:
                if time.time() - started > timeout_seconds:
                    print("Consumer timeout reached.")
                    break

                message = consumer.poll(1.0)

                if message is None:
                    continue

                if message.error():
                    if message.error().code() == KafkaError._PARTITION_EOF:
                        continue

                    raise RuntimeError(message.error())

                try:
                    event = json.loads(
                        message.value().decode("utf-8")
                    )
                except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                    raise ValueError(
                        f"Invalid JSON message at "
                        f"{message.topic()}[{message.partition()}]"
                        f"@{message.offset()}"
                    ) from exc

                print(json.dumps(event, indent=2))

                target.write(
                    json.dumps(event) + "\n"
                )

                count += 1

            # Commit only after successfully processing the messages.
            consumer.commit(asynchronous=False)

    finally:
        consumer.close()

    print(
        f"Consumed {count} events into {output_path}"
    )

    return count
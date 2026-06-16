---
id: stream_processing_kafka
version: 1.0.0
owners:
  - data_engineer
tags:
  - kafka
  - streaming
  - real-time
  - event-driven
when_to_use: "When building real-time data pipelines, event streaming systems, or processing high-throughput message streams with Kafka."
inputs:
  - topic schema
  - throughput requirements (msg/s)
  - consumer group design
  - retention policy
outputs:
  - Kafka topic design
  - producer/consumer code
  - schema registry setup
  - monitoring config
---

> "The stream is the system. Everything else is a view."

## Core Kafka Concepts

| Concept | Role |
|---------|------|
| Topic | Named, partitioned, ordered log |
| Partition | Unit of parallelism and ordering |
| Consumer Group | Horizontal scaling unit |
| Offset | Position in the partition log |

## Producer Pattern (Python)

```python
from confluent_kafka import Producer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer

# Schema registry for contract enforcement
sr_client = SchemaRegistryClient({"url": "http://schema-registry:8081"})
avro_serializer = AvroSerializer(sr_client, schema_str, to_dict=lambda obj, ctx: obj.__dict__)

producer = Producer({
    "bootstrap.servers": "kafka:9092",
    "acks": "all",                   # wait for all replicas
    "enable.idempotence": True,      # exactly-once semantics
    "compression.type": "lz4",
    "linger.ms": 5,                  # micro-batching
    "batch.size": 65536,
})

def delivery_report(err, msg):
    if err:
        logger.error(f"Delivery failed: {err}")
    else:
        logger.info(f"Delivered to {msg.topic()}[{msg.partition()}] @ {msg.offset()}")

producer.produce(
    topic="order.created",
    key=str(order.id).encode(),
    value=avro_serializer(order, SerializationContext("order.created", MessageField.VALUE)),
    on_delivery=delivery_report,
)
producer.flush()
```

## Consumer Pattern with Exactly-Once Processing

```python
from confluent_kafka import Consumer, KafkaError

consumer = Consumer({
    "bootstrap.servers": "kafka:9092",
    "group.id": "order-processor-v1",
    "auto.offset.reset": "earliest",
    "enable.auto.commit": False,     # manual commit for exactly-once
    "max.poll.interval.ms": 300000,
})

consumer.subscribe(["order.created"])

try:
    while True:
        msg = consumer.poll(timeout=1.0)
        if msg is None:
            continue
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                continue
            raise KafkaException(msg.error())

        try:
            process_order(deserialize(msg.value()))
            consumer.commit(asynchronous=False)  # commit only after successful processing
        except ProcessingError as e:
            send_to_dlq(msg, e)                  # dead-letter queue for poison pills
            consumer.commit(asynchronous=False)
finally:
    consumer.close()
```

## Topic Design Rules

```python
# Partition count: target 1-10 MB/s per partition
# Formula: partitions = ceil(target_throughput / partition_throughput)
# Example: 100 MB/s target, 10 MB/s per partition = 10 partitions

# Retention: match downstream SLA
# High-volume operational: 7 days
# Audit/compliance: 90 days
# Event sourcing: infinite (log compaction)

# Naming convention: <domain>.<entity>.<event>
# Good:  payments.transaction.created
# Bad:   transactions, paymentEvents
```

## Kafka Streams — Stateful Processing

```python
# Use Faust (Python Kafka Streams equivalent)
import faust

app = faust.App("order-aggregator", broker="kafka://kafka:9092")

orders_topic = app.topic("order.created", value_type=Order)
revenue_table = app.Table("revenue_by_region", default=float)

@app.agent(orders_topic)
async def process_orders(orders):
    async for order in orders.group_by(Order.region):
        revenue_table[order.region] += order.amount
```

## Anti-Patterns

- **Consumer per message** — batch with `poll()`, commit after batch
- **No schema registry** — schema drift breaks consumers silently
- **Single partition** — no parallelism; cannot scale consumer group
- **Synchronous producer with flush per message** — 100x throughput loss

## Monitoring (RED Metrics)

```yaml
# Key metrics to alert on
kafka_consumer_lag_sum > 10000      # consumers falling behind
kafka_producer_request_error_rate   # producer failures
kafka_broker_under_replicated_partitions > 0  # data loss risk
```

## Validation Checklist

- [ ] Schema registered in Schema Registry before first produce
- [ ] Consumer group ID is versioned (allows parallel old/new consumers during deploys)
- [ ] Dead-letter queue topic exists for poison pill messages
- [ ] Partition count set at topic creation (cannot reduce later)
- [ ] Consumer lag alert configured
- [ ] Idempotent producer enabled for exactly-once semantics

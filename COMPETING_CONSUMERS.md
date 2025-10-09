# Competing Consumers Pattern

All worker services in this project use the **Competing Consumers Pattern** for horizontal scalability and reliability.

## Key Principles

### 1. Pull-Based Subscriptions
- Workers **pull** messages from NATS JetStream
- Not push-based (which would send same message to all subscribers)

### 2. Durable Consumers
- Each service has a **named durable consumer**
- Multiple instances share the **same consumer**
- Example: `context-enricher-consumer`

### 3. Message Distribution
- Each message delivered to **ONLY ONE** instance
- Fair distribution across all running instances
- No duplicate processing

### 4. Acknowledgment
- **Success:** `msg.ack()` - Message removed from queue
- **Failure:** `msg.nak()` - Message requeued for retry
- **Timeout:** If no ack within `ack_wait`, message is retried

## Configuration

```python
from nats.js.api import ConsumerConfig, DeliverPolicy

config = ConsumerConfig(
    durable_name="service-name-consumer",
    deliver_policy=DeliverPolicy.ALL,  # Read all unacknowledged messages
    ack_wait=30,  # 30 seconds to process before retry
    max_deliver=3,  # Retry up to 3 times
    ack_policy=None  # Explicit ack required (default for pull)
)

psub = await js.pull_subscribe(
    subject="your.subject.here",
    durable="service-name-consumer",
    stream="stream-name",
    config=config
)
```

## Scaling Workers

### Start with 1 instance:
```bash
docker-compose up -d context-enricher
```

### Scale to 3 instances:
```bash
docker-compose up -d --scale context-enricher=3
```

### What happens:
- All 3 instances connect to the **same durable consumer**
- Messages are distributed evenly (round-robin)
- If one instance fails, others continue processing
- Failed messages are retried on other instances

## Message Flow

```
                     NATS JetStream
                     ┌─────────────┐
                     │   Message   │
                     │    Queue    │
                     └─────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
   ┌────────┐        ┌────────┐        ┌────────┐
   │Worker 1│        │Worker 2│        │Worker 3│
   └────────┘        └────────┘        └────────┘
        │                  │                  │
        ▼                  ▼                  ▼
      ACK                ACK                ACK
```

## Error Handling

### Success Path
1. Worker pulls message
2. Processes successfully
3. Calls `msg.ack()`
4. Message removed from queue

### Failure Path
1. Worker pulls message
2. Processing fails (exception)
3. Calls `msg.nak()`
4. Message goes back to queue
5. Another worker picks it up
6. After `max_deliver` attempts → needs DLQ handling

### Timeout Path
1. Worker pulls message
2. Processing takes > `ack_wait` seconds
3. No ack received
4. Message automatically requeued
5. Another worker picks it up

## Best Practices

### 1. Set Appropriate ack_wait
- Too short → messages retry even when processing normally
- Too long → delayed retries on failures
- **Recommendation:** 2-3x average processing time

### 2. Set Reasonable max_deliver
- Prevents infinite retry loops
- **Recommendation:** 3-5 attempts
- After max attempts → send to Dead Letter Queue

### 3. Batch Size = 1 for Fair Distribution
```python
msgs = await psub.fetch(batch=1, timeout=5)
```
- Ensures even distribution across instances
- Can increase for throughput if needed

### 4. Always Handle Exceptions
```python
try:
    await msg.ack()
    # Process message
    await enrich_context(request)
except Exception as e:
    logger.error(f"Error: {e}")
    await msg.nak()  # Retry on another instance
```

### 5. Idempotency
- Workers should be **idempotent**
- Safe to process same message multiple times
- Use database upserts, not inserts
- Check if work already done before processing

## Docker Compose Configuration

```yaml
context-enricher:
  build:
    context: ../
    dockerfile: src/context_enricher/Dockerfile
  # DON'T use container_name - allows multiple instances
  restart: unless-stopped
  environment:
    NATS_URL: nats://nats:4222
  deploy:
    replicas: 1  # Default, can override with --scale
```

## Monitoring

### Check running instances:
```bash
docker-compose ps context-enricher
```

### Watch logs from all instances:
```bash
docker-compose logs -f context-enricher
```

### Monitor specific instance:
```bash
docker logs -f deployment-context-enricher-2
```

## Services Using This Pattern

| Service | Consumer Name | Subject | Stream |
|---------|--------------|---------|--------|
| Context Enricher | `context-enricher-consumer` | `context.enrich.request` | `creative-context-stream` |
| Image Generator | TBD | `creative.generate.request` | `creative-generation-stream` |
| Copy Generator | TBD | `copy.generate.request` | `creative-copy-stream` |
| Brand Composer | TBD | `brand.compose.request` | `creative-composition-stream` |

## References

- [NATS JetStream Docs](https://docs.nats.io/nats-concepts/jetstream)
- [Pull Consumers](https://docs.nats.io/nats-concepts/jetstream/consumers#pull-consumers)
- [Work Queue Pattern](https://docs.nats.io/nats-concepts/jetstream/consumers#work-queue-streams)

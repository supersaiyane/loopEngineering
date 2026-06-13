---
id: async_job_queue_patterns
version: 1.0.0
owners: [backend_lead, senior_engineer_be]
tags: [job-queue, background-jobs, celery, bullmq, sidekiq, worker, retry, dlq]
when_to_use: |
  Any work that is too slow for a synchronous HTTP response:
  sending emails, processing uploads, generating reports, calling
  slow third-party APIs, running ML inference. Also for decoupling
  workloads and smoothing traffic spikes.
inputs:
  - job_types, latency_requirements, failure_tolerance, concurrency_needs
outputs:
  - "queue_design: queue topology + worker config + retry policy + DLQ strategy"
---

# Async Job Queue Patterns

> If it takes more than 200ms or can fail independently from the user request,
> put it in a queue. Return 202 Accepted. Let the worker handle it.

## Queue topology

```
Producer (API server)
    │
    ├── queue: emails (priority=low, concurrency=20)
    ├── queue: media-processing (priority=high, concurrency=5, timeout=10min)
    ├── queue: reports (priority=low, concurrency=2)
    └── queue: notifications (priority=high, concurrency=50)

Each queue has dedicated workers sized for that workload.
Never mix fast jobs (notifications) with slow jobs (media processing) in one queue.
```

## Job design

```python
# Good job: small, idempotent, single-responsibility
@celery.task(bind=True, max_retries=3, default_retry_delay=60)
def send_welcome_email(self, user_id: str):
    try:
        user = User.objects.get(id=user_id)
        email_service.send_welcome(user.email, user.name)
    except EmailDeliveryError as exc:
        raise self.retry(exc=exc, countdown=2 ** self.request.retries * 60)
    except User.DoesNotExist:
        # Don't retry — user was deleted
        logger.warning(f"User {user_id} not found, skipping email")

# Idempotency: safe to run twice
@celery.task
def charge_subscription(subscription_id: str):
    sub = Subscription.objects.get(id=subscription_id)
    if sub.billing_status == 'charged':
        return  # already done — idempotent check
    payment_service.charge(sub)
    sub.billing_status = 'charged'
    sub.save()
```

## Retry policy

```
Attempt 1: immediate
Attempt 2: +60s (exponential)
Attempt 3: +300s
Attempt 4: +1800s (30min)
After max retries: move to DLQ

Add jitter: countdown = 2^attempt * 60 + random(0, 30)
Prevents thundering herd when upstream recovers.
```

## Dead Letter Queue (DLQ)

Jobs that exhaust retries go to the DLQ.

```python
# BullMQ example
const queue = new Queue('emails', {
  defaultJobOptions: {
    attempts: 4,
    backoff: { type: 'exponential', delay: 60000 },
    removeOnComplete: 100,
    removeOnFail: false,   // keep failed jobs for inspection
  }
})

# Periodic DLQ review
# Alert when DLQ depth > 100
# Manual replay: worker.retryJobs({ state: 'failed' })
```

## Worker concurrency sizing

```
CPU-bound jobs (compression, PDF generation):
  concurrency = CPU cores

I/O-bound jobs (HTTP calls, DB queries):
  concurrency = 10-50 per worker (most time is waiting)

Memory-intensive (ML inference):
  concurrency = 1-2 (avoid OOM)
```

## Job scheduling (cron-style)

```python
# Celery Beat for recurring jobs
CELERYBEAT_SCHEDULE = {
    'daily-report': {
        'task': 'tasks.generate_daily_report',
        'schedule': crontab(hour=7, minute=0),  # 7am UTC
        'options': {'queue': 'reports'},
    },
    'cleanup-expired-sessions': {
        'task': 'tasks.cleanup_sessions',
        'schedule': crontab(minute='*/15'),  # every 15 min
    },
}
```

## Anti-patterns

- **Sharing one queue for fast and slow jobs**: slow jobs block fast jobs. Use dedicated queues.
- **No idempotency check**: if a job is enqueued twice (network retry), it runs twice. Charge twice.
- **Infinite retries**: fills the queue with permanently broken jobs. Always set max_retries.
- **Storing large payloads in the job**: enqueue IDs, not data. `process_image(image_id)` not `process_image(image_bytes)`.
- **No DLQ monitoring**: failed jobs silently disappear. Alert on DLQ depth.

## Validation

- [ ] Each job is idempotent (safe to run twice).
- [ ] Retry policy has exponential backoff + jitter.
- [ ] Max retries set. Failed jobs go to DLQ, not silently dropped.
- [ ] DLQ monitored with alert.
- [ ] Fast and slow jobs on separate queues.
- [ ] Job payload contains IDs, not large data blobs.

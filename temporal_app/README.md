# Temporal Integration

This directory contains Temporal workflows and activities for durable, long-running business processes.

## What is Temporal?

Temporal is a platform for building durable workflows. It's ideal for:
- Multi-step business processes (onboarding, payments)
- Long-running operations that survive server restarts
- Retries with exponential backoff
- Distributed workflows across services

## Structure

- `workflows.py`: Workflow definitions (orchestration logic)
- `activities.py`: Individual task definitions (business logic)
- `run_temporal_worker.py`: Worker process that executes workflows

## Running the Worker

```bash
# Ensure Temporal server is running
docker compose up temporal-ui

# Start the worker
python temporal_app/run_temporal_worker.py
```

## Registering Workflows

Workflows are auto-registered by importing them in `run_temporal_worker.py`.

## Example Usage

From your Django app:

```python
from temporalio.client import Client
from temporal_app.workflows import onboarding_workflow

async def trigger_onboarding(user_id: int, email: str):
    client = await Client.connect(
        os.environ.get('TEMPORAL_HOST', 'localhost:7233'),
    )
    
    result = await client.execute_workflow(
        onboarding_workflow,
        args=[user_id, email],
        id=f"onboarding-{user_id}",
        task_queue='my-api-project-task-queue',
    )
    
    return result
```

## Temporal UI

When the Temporal server is running, access the UI at:
- http://localhost:8088

This shows workflow history, execution details, and allows for replay/debugging.

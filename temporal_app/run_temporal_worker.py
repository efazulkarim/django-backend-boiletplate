"""Run Temporal worker."""
import asyncio
import os
from temporalio.client import Client
from temporalio.worker import Worker

# Import workflows to register them
from temporal_app.workflows import onboarding_workflow, payment_workflow


async def main():
    """Run the Temporal worker."""
    # Connect to Temporal server
    client = await Client.connect(
        os.environ.get('TEMPORAL_HOST', 'localhost:7233'),
        namespace=os.environ.get('TEMPORAL_NAMESPACE', 'default'),
    )
    
    # Create and start worker
    worker = Worker(
        client,
        task_queue='my-api-project-task-queue',
        workflows=[onboarding_workflow, payment_workflow],
    )
    
    print("Temporal worker started. Press Ctrl+C to stop.")
    await worker.run()


if __name__ == '__main__':
    asyncio.run(main())

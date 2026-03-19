"""Temporal workflows for async processing."""
from datetime import timedelta
from temporalio import workflow, activity


@activity.defn
def send_email(to: str, subject: str, body: str) -> str:
    """Send email activity."""
    # Integrate with your email service
    print(f"Sending email to {to}: {subject}")
    return f"Email sent to {to}"


@activity.defn
def process_report(user_id: int) -> str:
    """Process report activity."""
    # Integrate with your report processing logic
    print(f"Processing report for user {user_id}")
    return f"Report processed for user {user_id}"


@workflow.defn
def onboarding_workflow(user_id: int, email: str) -> str:
    """User onboarding workflow."""
    # Send welcome email
    result = yield activity.execute(
        send_email,
        args=[email, "Welcome!", "Welcome to My API Project"]
    )
    
    # Process initial report
    report_result = yield activity.execute(
        process_report,
        args=[user_id]
    )
    
    return f"Onboarding complete for user {user_id}: {result}"


@workflow.defn
def payment_workflow(user_id: int, amount: float) -> str:
    """Payment processing workflow."""
    # Validate payment
    # Process payment
    # Send confirmation
    # Handle retries
    
    return f"Payment of ${amount:.2f} processed for user {user_id}"

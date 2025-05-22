from django.shortcuts import get_object_or_404
from django.core.mail import EmailMessage
from django.conf import settings
from celery import shared_task
from main.models import CV


@shared_task(bind=True)
def send_cv_pdf_email_task(self, cv_id, recipient_email, pdf_content):
    """
    Emails a pre-generated PDF for a CV.
    """
    try:
        cv_instance = get_object_or_404(CV, pk=cv_id)

        cv_name = f"{cv_instance.firstname} {cv_instance.lastname}"
        print(
            f"Preparing to email PDF for CV: {cv_name} (ID: {cv_id}) to "
            f"{recipient_email}"
        )

        if not pdf_content:
            error_message = (
                f"No PDF content provided for CV ID {cv_id}. Email not sent."
            )
            print(error_message)
            return f"Failed to send email: {error_message}"

        print(f"Using pre-generated PDF for CV: {cv_name}")

        subject = f"CV: {cv_name}"
        body = (
            f"Dear user,\n\nHere's requested CV ({cv_name}) in PDF.\n\nBest"
            f" regards,\nCVProject"
        )
        from_email = settings.DEFAULT_FROM_EMAIL

        email = EmailMessage(
            subject,
            body,
            from_email,
            [recipient_email]
        )
        filename = (
            f"{cv_instance.firstname}_{cv_instance.lastname}_CV.pdf".replace(
                " ", "_"
            )
        )
        email.attach(filename, pdf_content, 'application/pdf')
        email.send()

        print(
            f"Email sent successfully to {recipient_email} for CV: {cv_name}"
        )
        return (
            f"Email for CV '{cv_name}' (ID: {cv_id}) sent to {recipient_email}"
        )

    except CV.DoesNotExist:
        print(f"CV with ID {cv_id} not found.")
        return f"Failed to send email: CV with ID {cv_id} not found."
    except Exception as e:
        print(
            f"Error in send_cv_pdf_email_task for CV ID {cv_id} to "
            f"{recipient_email}: {e}"
        )
        return f"Failed to send email for CV ID {cv_id}: {e}"

from django.shortcuts import render, get_object_or_404, redirect
from django.template.loader import render_to_string
from main.api.serializers import CVSerializer
from main.tasks import send_cv_pdf_email_task
from django.http import HttpResponse
from rest_framework import viewsets
from django.contrib import messages
from main.models import CV
from xhtml2pdf import pisa
from io import BytesIO


def _generate_cv_pdf_content(cv_instance):
    """
    Generates PDF content for a given CV instance.
    Returns PDF content as bytes, or None if generation fails.
    """
    context = {'cv': cv_instance}
    html_string = render_to_string('main/cv_detail_pdf.html', context)
    result_file = BytesIO()

    pdf_status = pisa.CreatePDF(
        src=html_string.encode('utf-8'),
        dest=result_file,
        encoding='utf-8'
    )

    if not pdf_status.err:
        pdf_content = result_file.getvalue()
        result_file.close()
        return pdf_content
    else:
        print(f"Error generating PDF for CV ID {cv_instance.id}. Pisa Error Code: {pdf_status.err}")
        for message in pdf_status.log:
            print(f"Pisa Log: Type={message.type}, Level={message.level}, Msg='{message.msg}', File='{message.filename}', Line={message.line}, Col={message.col}")
        result_file.close()
        return None


class CVViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows CVs to be viewed or edited.
    """
    queryset = CV.objects.prefetch_related(
        'skills', 'projects'
    ).all().order_by('id')
    serializer_class = CVSerializer


def cv_list_view(request):
    """Renders the main page displaying a list of all CVs.

    Retrieves all CV objects from the database, including their related
    skills and projects, using prefetch_related for efficiency.

    Args:
        request: The HttpRequest object.

    Returns:
        HttpResponse: The rendered HTML page displaying the list of CVs.
    """
    cvs = CV.objects.prefetch_related('skills', 'projects').all()
    context = {
        'cvs': cvs
    }
    return render(request, 'main/cv_list.html', context)


def cv_detail_view(request, cv_id):
    """Renders the detail page for a single CV.

    Retrieves a specific CV by its ID, including its related
    skills and projects, using prefetch_related for efficiency.
    If the CV is not found, a 404 error is raised.

    Args:
        request: The HttpRequest object.
        cv_id (int): The primary key of the CV to display.

    Returns:
        HttpResponse: The rendered HTML page displaying the details of the CV.
                      Raises Http404 if the CV with the given id is not found.
    """
    cv = get_object_or_404(
        CV.objects.prefetch_related('skills', 'projects'),
        pk=cv_id
    )
    context = {
        'cv': cv,
        'is_pdf_export': False
    }
    return render(request, 'main/cv_detail.html', context)


def cv_pdf_view(request, cv_id):
    """Generates a PDF version of a CV and serves it for download.

    This view retrieves a specific CV by its ID, fetches its related skills
    and projects efficiently using `prefetch_related`. It then renders the
    CV's details using a dedicated HTML template (`main/cv_detail_pdf.html`)
    designed for PDF output. The rendered HTML is converted to a PDF document
    in memory using the `xhtml2pdf` library (pisa).

    Args:
        request: The HttpRequest object.
        cv_id (int): The primary key of the CV to be converted to PDF.

    Returns:
        HttpResponse: An HttpResponse with `content_type='application/pdf'`
            containing the generated PDF data if successful. The
            `Content-Disposition` header is set to suggest a filename for
            download.
            Returns an HttpResponse with status 500 if PDF generation fails.
            Raises Http404 if the CV with the given `cv_id` is not found.
    """
    cv = get_object_or_404(
        CV.objects.prefetch_related('skills', 'projects'),
        pk=cv_id
    )

    pdf_content = _generate_cv_pdf_content(cv)

    if pdf_content:
        response = HttpResponse(
            pdf_content, content_type='application/pdf'
        )
        response[
            'Content-Disposition'
        ] = f'attachment; filename="{cv.firstname}_{cv.lastname}_CV.pdf"'
        return response
    else:
        return HttpResponse(
            "Sorry, there was an error generating the PDF.",
            status=500
        )


def trigger_send_cv_email_view(request, cv_id):
    cv_instance = get_object_or_404(
        CV.objects.prefetch_related('skills', 'projects'),
        pk=cv_id
    )

    if request.method == 'POST':
        recipient_email = request.POST.get('recipient_email')
        if recipient_email:
            pdf_content = _generate_cv_pdf_content(cv_instance)

            if pdf_content:
                send_cv_pdf_email_task.delay(
                    cv_instance.id, recipient_email, pdf_content
                )
                messages.success(
                    request,
                    f"{cv_instance.firstname} {cv_instance.lastname}'s CV was sent to {recipient_email}."
                )
            else:
                messages.error(
                    request,
                    "Failed to generate PDF for the CV. Email not sent."
                )
        else:
            messages.error(request, "Please enter recipient email.")

        return redirect('main:cv_detail', cv_id=cv_instance.id)
    return redirect('main:cv_detail', cv_id=cv_instance.id)

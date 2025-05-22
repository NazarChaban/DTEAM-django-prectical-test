from main.services.cv_utils import (
    generate_cv_pdf_content,
    serialize_cv_instance,
)
from django.shortcuts import render, get_object_or_404, redirect
from main.services.gemini_translate import translate_text
from django.template.loader import render_to_string
from main.api.serializers import CVSerializer
from main.tasks import send_cv_pdf_email_task
from django.http import HttpResponse
from rest_framework import viewsets
from django.contrib import messages
from main.models import CV


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

    pdf_content = generate_cv_pdf_content(cv)

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
            pdf_content = generate_cv_pdf_content(cv_instance)

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


def translate_cv_view(request, cv_id):
    if request.method != 'POST':
        return HttpResponse("Method not allowed", status=405)

    target_language = request.POST.get('language')
    if not target_language:
        return HttpResponse("No language selected.", status=400)

    cv_instance = get_object_or_404(
        CV.objects.prefetch_related('skills', 'projects'),
        pk=cv_id
    )

    original_data = serialize_cv_instance(cv_instance)

    translated_data = translate_text(original_data, target_language)
    if "error" in translated_data:
        return HttpResponse(translated_data["error"], status=500)

    html = render_to_string(
        'main/cv_translated_pdf.html', {'cv': translated_data}
    )
    pdf_content = generate_cv_pdf_content(html_string=html)

    if pdf_content:
        filename = (
            f"{translated_data['firstname']}_{translated_data['lastname']}"
            f"_{target_language}_CV.pdf"
        )
        response = HttpResponse(pdf_content, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

    return HttpResponse("Failed to generate PDF.", status=500)

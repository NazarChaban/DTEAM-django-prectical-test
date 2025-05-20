from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string
from django.http import HttpResponse
from main.models import CV
from xhtml2pdf import pisa
from io import BytesIO


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
    context = {
        'cv': cv,
    }

    html_string = render_to_string('main/cv_detail_pdf.html', context)
    result_file = BytesIO()

    pdf = pisa.CreatePDF(
        src=html_string.encode('utf-8'),
        dest=result_file,
        encoding='utf-8'
    )

    if not pdf.err:
        response = HttpResponse(
            result_file.getvalue(), content_type='application/pdf'
        )
        response[
            'Content-Disposition'
        ] = f'attachment; filename="{cv.firstname}_{cv.lastname}_CV.pdf"'
        return response
    else:
        print(f"Error generating PDF for CV ID {cv_id}. Pisa Error Code: {pdf.err}")
        for message in pdf.log:
            print(f"Pisa Log: Type={message.type}, Level={message.level}, Msg='{message.msg}', File='{message.filename}', Line={message.line}, Col={message.col}")
        return HttpResponse(
            "Sorry, there was an error generating the PDF.",
            status=500
        )
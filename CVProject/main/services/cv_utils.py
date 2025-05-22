from django.template.loader import render_to_string
from django.forms.models import model_to_dict
from main.models import CV
from xhtml2pdf import pisa
from io import BytesIO


def generate_cv_pdf_content(cv_instance=None, html_string=None):
    """
    Generates PDF content from a CV instance or from a provided HTML string.
    Returns PDF content as bytes, or None if generation fails.
    """
    if html_string is None:
        if not cv_instance:
            return None
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
        print(
            f"Error generating PDF for CV ID {cv_instance.id}. "
            f"Pisa Error Code: {pdf_status.err}"
        )
        for message in pdf_status.log:
            print(
                f"Pisa Log: Type={message.type}, Level={message.level}, "
                f"Msg='{message.msg}', File='{message.filename}', Line="
                f"{message.line}, Col={message.col}"
            )
        result_file.close()
        return None


def serialize_cv_instance(cv: CV):
    """Returns JSON from a CV instance."""
    data = model_to_dict(
        cv, fields=['firstname', 'lastname', 'bio', 'contacts']
    )
    data['skills'] = list(cv.skills.values_list('name', flat=True))
    data['projects'] = list(cv.projects.values('name', 'description', 'link'))
    return data

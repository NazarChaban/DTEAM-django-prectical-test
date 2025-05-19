from django.shortcuts import render, get_object_or_404
from .models import CV


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
        'cv': cv
    }
    return render(request, 'main/cv_detail.html', context)

from django.shortcuts import render
from audit.models import RequestLog


def recent_logs_view(request):
    """
    Handles displaying the most recent request logs.
    Retrieves the latest ten request log records from the database
    ordered by descending timestamp, and then renders them using the
    'audit/recent_logs.html' template.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response rendered with the recent logs.
    """
    logs = RequestLog.objects.order_by('-timestamp')[:10]
    context = {
        'logs': logs
    }
    return render(request, 'audit/recent_logs.html', context)


def display_settings_view(request):
    """
    Handles displaying the site settings.
    Retrieves the site settings from the Django settings module
    and renders them using the 'audit/display_settings.html' template.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response rendered with the site settings.
    """
    return render(request, 'audit/display_settings.html')

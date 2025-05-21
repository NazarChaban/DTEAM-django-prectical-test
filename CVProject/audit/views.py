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

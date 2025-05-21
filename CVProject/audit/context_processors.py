from django.conf import settings


def settings_context(request):
    """
    A context processor to add commonly used site settings to the template
    context.
    """
    return {
        'DEBUG': settings.DEBUG,
        'ALLOWED_HOSTS': settings.ALLOWED_HOSTS,
        'LANGUAGE_CODE': settings.LANGUAGE_CODE,
        'TIME_ZONE': settings.TIME_ZONE,
    }

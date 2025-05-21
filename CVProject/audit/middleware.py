from audit.models import RequestLog


class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            user = request.user if request.user.is_authenticated else None
            query_params = request.GET.urlencode()

            RequestLog.objects.create(
                method=request.method,
                path=request.path,
                query_string=query_params if query_params else None,
                ip_address=self.get_client_ip(request),
                user=user
            )
        except Exception:
            pass

        response = self.get_response(request)
        return response

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

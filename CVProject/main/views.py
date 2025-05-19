from django.shortcuts import render
from .models import CV


def cv_list_view(request):
    cvs = CV.objects.prefetch_related('skills', 'projects').all()
    context = {
        'cvs': cvs
    }
    return render(request, 'main/cv_list.html', context)

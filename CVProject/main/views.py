from django.shortcuts import render, get_object_or_404
from .models import CV


def cv_list_view(request):
    cvs = CV.objects.prefetch_related('skills', 'projects').all()
    context = {
        'cvs': cvs
    }
    return render(request, 'main/cv_list.html', context)


def cv_detail_view(request, cv_id):
    cv = get_object_or_404(
        CV.objects.prefetch_related('skills', 'projects'),
        pk=cv_id
    )
    context = {
        'cv': cv
    }
    return render(request, 'main/cv_detail.html', context)

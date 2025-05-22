from django.urls import path, include
from main import views

app_name = 'main'

urlpatterns = [
    path('', views.cv_list_view, name='cv_list'),
    path('cv/<int:cv_id>/', views.cv_detail_view, name='cv_detail'),
    path('cv/<int:cv_id>/pdf/', views.cv_pdf_view, name='cv_pdf'),
    path(
        'cv/<int:cv_id>/send-email/',
        views.trigger_send_cv_email_view,
        name='send_cv_email'
    ),
    path('api/', include('main.api.urls')),
]

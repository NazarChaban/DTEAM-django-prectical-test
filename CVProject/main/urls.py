from django.urls import path
from main import views

app_name = 'main'

urlpatterns = [
    path('', views.cv_list_view, name='cv_list'),
]

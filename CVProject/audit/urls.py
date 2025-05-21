from django.urls import path
from audit import views

app_name = 'audit'

urlpatterns = [
    path('logs/', views.recent_logs_view, name='recent_logs'),
    path('settings/', views.display_settings_view, name='display_settings'),
]

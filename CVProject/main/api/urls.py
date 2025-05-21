from rest_framework.routers import DefaultRouter
from django.urls import path, include
from ..views import CVViewSet

router = DefaultRouter()
router.register(r'cvs', CVViewSet, basename='cv-api')

urlpatterns = [
    path('', include(router.urls)),
]

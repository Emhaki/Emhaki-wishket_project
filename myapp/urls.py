from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AWSViewSet

router = DefaultRouter()
router.register('aws', AWSViewSet)

urlpatterns = [
    path('', include(router.urls))
]

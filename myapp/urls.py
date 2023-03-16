from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import lambda_handler
# from .views import AWSViewSet

# router = DefaultRouter()
# router.register('aws', AWSViewSet)

urlpatterns = [
    path('aws/usage/<int>/<int>/', lambda_handler())
]

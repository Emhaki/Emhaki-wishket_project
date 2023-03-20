from django.urls import path, include
from rest_framework.routers import DefaultRouter, SimpleRouter
from .views import AWSViewSet

urlpatterns = [
    path('aws/usage/<int:year>/<int:month>/', AWSViewSet.as_view({'get': 'usage'}), name='usage'),
    path('aws/bill/', AWSViewSet.as_view({'post': 'bill'}), name="bill")
]

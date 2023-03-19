from django.urls import path, include
from rest_framework.routers import DefaultRouter, SimpleRouter
from .views import AWSViewSet
from . import views

# router = DefaultRouter()
# router.register('aws', AWSViewSet, basename='usage')

# urlpatterns = [
#     path('', include(router.urls)),
#     # path('test/', views.usage_input)
# ]

from django.urls import path
from .views import AWSViewSet

urlpatterns = [
    path('aws/usage/<int:year>/<int:month>/', AWSViewSet.as_view({'get': 'list'}), name='usage'),
]

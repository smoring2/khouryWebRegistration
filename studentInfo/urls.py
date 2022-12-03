from django.urls import path
from studentInfo import api_views

urlpatterns = [
    path('api/advisor/approve', api_views.approvePendingRequest),
]

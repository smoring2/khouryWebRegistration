from django.urls import path
from studentInfo import views

urlpatterns = [
    path('api/advisor/approve', views.approvePendingRequest),
]

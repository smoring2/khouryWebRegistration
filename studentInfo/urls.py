from django.urls import path
from studentInfo import api_views

urlpatterns = [
    path('api/advisor/approve', api_views.approvePendingRequest),
    path('api/advisor/reject', api_views.rejectPendingRequest),

]

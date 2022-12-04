from django.urls import path
from studentInfo import api_views

urlpatterns = [
    path('api/advisor/approve', api_views.approvePendingRequest),
    path('api/advisor/reject', api_views.rejectPendingRequest),
    path('api/advisor/remove', api_views.removeOneApprovedCourse),
    path('api/advisor/add', api_views.addOneApprovedCourse),
    path('api/advisor/update_gpa', api_views.updateGPA),
    path('api/advisor/insert_student', api_views.insertStudent),
    path('api/advisor/update_hours', api_views.updateHours),
    path('api/advisor/update_phone', api_views.updatePhone)

]

"""khouryWebRegistration URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from studentInfo import views
from studentInfo import admin_view
from studentInfo import advisor_views
from studentInfo import student_views


urlpatterns = [
    # path('admin/', admin.site.urls),
    #student
    path('', views.testmysql),
    path('student/', student_views.StudentList.as_view(), name='student_list'),
    path('student/<int:pk>', student_views.StudentDetails.as_view(), name='student_profile'),
    path('student/home/<int:pk>', student_views.StudentHome.as_view(), name='student_home'),
    path('student/degreeAudit/<int:student_id>', student_views.getDegreeAudit, name='degree_audit'),
    path('student/courseRegistration/<int:student_id>', student_views.getRegistrationInfo, name='course_registration'),
    path('student/dropCourse/<int:student_id>', student_views.dropCourse, name='course_drop'),

    #admin
    path("admin/home/", admin_view.admin_home, name='admin_home'),
    path("advisor/add/", admin_view.add_advisor, name='add_advisor'),
    path("course/add/", admin_view.add_course, name='add_course'),
    path("student/add/", admin_view.add_student, name='add_student'),
    path("advisor/manage/", admin_view.manage_advisor, name='manage_advisor'),
    path("student/manage/", admin_view.manage_student, name='manage_student'),
    path("course/manage/", admin_view.manage_course, name='manage_course'),
    path("student/edit/<int:nuid>", admin_view.edit_student, name='edit_student'),
    path("course/edit/<int:course_id>", admin_view.edit_course, name='edit_course'),
    path("advisor/edit/<int:employee_id>", admin_view.edit_advisor, name='edit_advisor'),
    path("advisor/delete/<int:employee_id>",
         admin_view.delete_advisor, name='delete_advisor'),
    path("student/delete/<int:nuid>",
         admin_view.delete_student, name='delete_student'),
    path("course/delete/<int:course_id>",
         admin_view.delete_course, name='delete_course'),

    #advisor
    path('advisor/profile/<int:employee_id>', advisor_views.getAdvisorProfile, name = 'advisor_profile'),
    path('advisor/<int:advisor_id>', advisor_views.getAdvisorStatistics, name = 'advisor_statics'),
    path('advisor/requests/<int:advisor_id>', advisor_views.getAdvisorRequests, name = 'advisor_requests'),
    path('advisor/search/<int:advisor_id>', advisor_views.getAdvisorSearch, name = 'advisor_search'),
    path('advisor/search/details', advisor_views.getSearchDetails, name='search_details'),
    path('advisor/my_students/<int:advisor_id>', advisor_views.getMyStudentsList, name='advisor_students'),
    path('', include('studentInfo.urls')),
]

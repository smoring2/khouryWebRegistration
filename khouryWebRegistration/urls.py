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
from django.urls import path
from studentInfo import views
from studentInfo import admin_view

urlpatterns = [
    # path('admin/', admin.site.urls),
    #student
    path('', views.testmysql),
    path('student/', views.StudentList.as_view(), name = 'student_list'),
    path('student/<int:pk>', views.StudentDetails.as_view(), name = 'student_detail'),

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
         admin_view.delete_course, name='delete_course')
]

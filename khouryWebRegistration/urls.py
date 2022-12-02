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

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('', views.testmysql),
    path('student/', views.StudentList.as_view(), name = 'student_list'),
    path('student/<int:pk>', views.StudentDetails.as_view(), name = 'student_detail'),
    path('advisor/profile/<int:employee_id>', views.getAdvisorProfile, name = 'advisor_profile'),
    path('advisor/statics/<int:advisor_id>', views.getAdvisorStatics, name = 'advisor_statics'),
    path('advisor/notifications/<int:advisor_id>', views.getAdvisorNotifications, name = 'advisor_notifications'),
    path('advisor/search/<int:advisor_id>', views.getAdvisorSearch, name = 'advisor_search'),
    path('advisor/search/details', views.getSearchDetails, name='search_details'),

]

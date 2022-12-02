from django.shortcuts import render
from .models import Student
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

def testmysql(request):
    myStudent = Student.objects.all()
    context = {
        'student_nuid': myStudent[0].nuid,
        'student_name': myStudent[0].name,
    }
    return render(request, 'studentInfo.html', context)

# StudentList class should be deleted later on.
class StudentList(ListView):
    template_name= 'student/student_list.html'
    model = Student

# Student main page after logging in.
class StudentDetails(DetailView):
    template_name = 'student/student_mainpage.html'
    model = Student
from django.shortcuts import render
from .models import *
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.db import connection
cursor= connection.cursor()


def testmysql(request):
    myStudent = Student.objects.all()
    context = {
        'student_nuid': myStudent[0].nuid,
        'student_name': myStudent[0].name,
    }
    return render(request, 'studentInfo.html', context)
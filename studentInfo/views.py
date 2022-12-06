from django.shortcuts import render
from .models import *
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.db import connection
cursor= connection.cursor()


def testmysql(request):
    return render(request, 'home.html')
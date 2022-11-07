from django.shortcuts import render
from .models import Student
def testmysql(request):
    myStudent = Student.objects.all()
    context = {
        'student_nuid': myStudent[0].nuid,
        'student_name': myStudent[0].name,
    }
    return render(request, 'studentInfo.html', context)

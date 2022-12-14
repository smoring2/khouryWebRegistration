from django import forms

from .models import *


class AdvisorForm(forms.ModelForm):
    class Meta:
        model = Advisor
        fields = "__all__"
        employee_id = forms.IntegerField(required=True)
        name = forms.CharField(required=True)
        email = forms.EmailField(required=True)
        phone = forms.IntegerField(required=True)
        department = forms.IntegerField(widget=forms.Textarea)
        password = forms.CharField(widget=forms.PasswordInput)
        widget = {
            'password': forms.PasswordInput(),
        }
    

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = "__all__"
        nuid = forms.IntegerField(required=True)
        name = forms.CharField(required=True)
        email = forms.CharField(required=True)
        bdate = forms.DateField(required=True)
        campusid = forms.IntegerField(required=True)
        collegeid = forms.IntegerField(required=True)
        department = forms.IntegerField(required=True)
        phone = forms.IntegerField(required=True)
        advisor = forms.IntegerField(required=True)
        grade = forms.IntegerField(required=True)
        semesterhour = forms.IntegerField(required=True)
        password = forms.CharField(widget=forms.PasswordInput)
        widget = {
            'password': forms.PasswordInput(),
        }


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = "__all__"
        course_id = forms.IntegerField()
        course_name = forms.CharField(required=True)
        instructor = forms.CharField(required=True)
        meeting_time = forms.TimeField(required=True)
        max_num_of_students = forms.IntegerField(required=True)
        semester = forms.IntegerField(required=True)
        semester_hrs = forms.IntegerField(required=True)
        registered_num_of_stud = forms.IntegerField(required=True)
        department = forms.IntegerField(required=True)
        campusid = forms.IntegerField(required=True)
        building = forms.IntegerField(required=True)
        room = forms.IntegerField(required=True)
        date = forms.CharField(required=True)
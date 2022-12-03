from django.shortcuts import render
from django.http.response import JsonResponse
from rest_framework.parsers import JSONParser
from rest_framework import status
from rest_framework.decorators import api_view

from django.db import connection
cursor= connection.cursor()

SQL_REGISTRATION_APPROVAL = '''update registration set approved = true, pending = false
where nuid = %(nuid)s  and pending = true'''
@api_view(['GET'])
def approvePendingRequest(request):
    nuid = request.query_params.get('nuid')
    val = {'nuid': int(nuid)}
    cursor.execute(SQL_REGISTRATION_APPROVAL, val)
    return JsonResponse({"message": "succeed"}, safe=False)

SQL_REGISTRATION_REJECTION = '''update registration set rejected = true, pending = false
where nuid= %(nuid)s and pending = true'''
@api_view(['GET'])
def rejectPendingRequest(request):
    nuid = request.query_params.get('nuid')
    val = {'nuid': int(nuid)}
    cursor.execute(SQL_REGISTRATION_REJECTION, val)
    return JsonResponse({"message": "succeed"}, safe=False)

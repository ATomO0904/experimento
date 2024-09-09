from django.shortcuts import render
import requests
import json
from time import sleep
from .models import GroupExp, UserAnswer, TempUserAnswer
from .tables import TempUserAnswerTable
from django_tables2 import RequestConfig
from django.http import HttpResponse
import csv
from django_tables2.export.export import TableExport 
import tablib

# Create your views here.

def index(request):
    return render(request, 'core/index.html')

def control(request):
    users_answer = TempUserAnswer.objects.all()
    table = TempUserAnswerTable(users_answer)
    context = {
        'table': table, 
        'started': False,
    }
    return render(request, 'core/control.html', context)


def controlB(request):
    return render(request, 'core/controlB.html')

def groupA(request):
    context = {
        'stared': False,
    }
    return render(request, 'core/groupA.html')

def groupB(request):
    return render(request, 'core/groupB.html')

def online_groupA(request):
    group = GroupExp.objects.filter(group='groupA')
    users = group.users_
    context = {
        'group': 'A',
    }
    return render(request, 'core/partials/online_users.html', context)

def online_groupB(request):
    context = {
        'group': 'B',
    }
    return render(request, 'core/partials/online_users.html', context)

def start_quiz(request):
    pass

def results(request):
    users_answer = TempUserAnswer.objects.all()
    table = TempUserAnswerTable(users_answer)
    RequestConfig(request, paginate={'per_page': 4}).configure(table)
    context = {
        'table': table, 
    }
    return render(request, 'core/results.html', context)

def export_to_csv(request):
    users_answer = TempUserAnswer.objects.all()
    table = TempUserAnswerTable(users_answer)
    RequestConfig(request).configure(table)
    exporter = TableExport('csv', table)
    csv_data = exporter.export()
    response = HttpResponse(csv_data, content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="users_answer.csv"'
    return response
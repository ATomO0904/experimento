from django.shortcuts import render
import requests
import json

# Create your views here.

def index(request):
    return render(request, 'core/index.html')

def control(request):
    return render(request, 'core/control.html')

def groupA(request):
    return render(request, 'core/groupA.html')

def groupB(request):
    return render(request, 'core/groupB.html')

def start_quiz(request):
    pass




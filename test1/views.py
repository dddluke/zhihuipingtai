import os
import json
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django.shortcuts import render
from rest_framework.generics import GenericAPIView
from .serializers import *

def index(request):

    return render(request, 'index.html')



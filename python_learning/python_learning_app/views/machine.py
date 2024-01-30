from django.shortcuts import render, redirect
from python_learning_app.models.index import CustomUser
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import FileResponse
import random

def machine_learning(request):

    return render(request, 'machine/machine_learning.html')

def how_to(request):

    return render(request, 'machine/how_to.html')


def download(request, pk):
    file = ['practice1.zip']
    file_path = 'downloads/' + file[pk - 1]
    filename = file[pk - 1]
    return FileResponse(open(file_path, "rb"), as_attachment=True, filename=filename)
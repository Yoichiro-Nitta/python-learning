from django.shortcuts import render, redirect
from pythonL.models import CustomUser, IntroCourse, Basis, Quartet, Competition
from pythonL.forms import SignupForm, LoginForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
import random
import subprocess

# Create your views here.
def top_page(request):
    return render(request, 'pythonL/index.html')

def signup_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return render(request, 'user/signed.html')

    else:
        form = SignupForm()
    params = {
        'form': form
    }
    return render(request, 'user/signup.html', params)

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user:
                login(request, user)
                return render(request, 'user/loggedin.html')
    else:
        form = LoginForm()
    param = {
        'form': form}
    return render(request, 'user/login.html', param)

def login_req(request):
    return render(request, 'user/login_req.html')

def logout_view(request):
    logout(request)
    return render(request, 'user/logout.html')


def intro(request):
    introforewords = IntroCourse.objects.filter(order = 1)
    introforewords = introforewords.order_by('section')
    params ={"introforewords": introforewords}
    return render(request, 'pythonL/intro.html', params)

def intro_ex(request, pk):
    explanations = IntroCourse.objects.filter(section = pk)
    explanations = explanations.order_by('order')
    title = explanations.first().title
    n, p = pk + 1, pk - 1
    if request.method == 'POST':
        text = request.POST['text'] 
        backup = request.POST['backup'] 
        if text == '':
            text = backup
        with open('pythonL/intro.py', 'w') as f:
            f.write(text)
        op = subprocess.run('python pythonL/intro.py', shell=True, capture_output=True, text=True, timeout=3)
        out = op.stdout
        err = op.stderr
        err = err.split('",')[-1]
        params = {
        'text': text, 'out' : out, 'err': err, 
        "explanations": explanations, "title": title, "pk": pk, "n": n, "p": p}
        return render(request, 'pythonL/intro_ex.html', params)
    params = {"explanations": explanations, "title":title, "pk": pk, "n": n, "p": p}
    return render(request, 'pythonL/intro_ex.html', params)

def questions(request):
    un_last = Basis.objects.order_by('unit').last().unit
    unit_list = [Basis.objects.filter(unit = i+1, q_key = True).order_by('section') for i in range(un_last)]
    units ={}
    for i in range(un_last):
        units[unit_list[i].first().major_h] = unit_list[i]
    multiple5 = [ 5 * x for x in range(1,11) ]
    params = {"units": units, "un_last": un_last, "multiple5": multiple5}
    return render(request, 'pythonL/questions.html', params)


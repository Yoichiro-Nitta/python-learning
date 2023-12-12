from django.shortcuts import render, redirect
from .models import CustomUser, Basis, Quartet, Competition
from application import assist, pllist
from .forms import SignupForm, LoginForm
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
    return render(request, 'pythonL/intro.html')

def intro_ex(request, pk):
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
        'text': text, 'out' : out, 'err': err}
        return render(request, f'intro_ex/intro{pk}.html', params)
    return render(request, f'intro_ex/intro{pk}.html')

def questions(request):
    return render(request, 'pythonL/questions.html')

def practice(request):
    if request.method == 'POST':
        text = request.POST['text'] 
        backup = request.POST['backup'] 
        if text == '':
            text = backup
        with open('pythonL/practice.py', 'w') as f:
            f.write(text)
        op = subprocess.run('python pythonL/practice.py', shell=True, capture_output=True, text=True, timeout=3)
        out, err = op.stdout, op.stderr
        err = err.split('",')[-1]
        params = {
        'text': text, 'out' : out, 'err': err}
        return render(request, 'pythonL/practice.html', params)
    return render(request, 'pythonL/practice.html')

def practice_a(request):
    if request.method == 'POST':
        text = request.POST['text']
        backup = request.POST['backup']
        if text == '':
            text = backup
        with open('pythonL/practice.py', 'w') as f:
            f.write(text)
        op = subprocess.run('python pythonL/practice.py', shell=True, capture_output=True, text=True, timeout=3)
        out = op.stdout
        ans = "Hello, World!\n"
        if out == ans:
            collect = True
        else:
            collect = False
        params = {
        'text': text, 'out' : out, 'collect': collect}
        return render(request, 'pythonL/practice_a.html', params)
    return render(request, 'pythonL/practice_a.html')

@login_required
def basis(request, pk):
    if request.method == 'POST':
        text = request.POST['text'] 
        backup = request.POST['backup'] 
        data1 = request.POST['data1']
        data2 = request.POST['data2']
        q_title, q_sentence, pre_visual, post_visual = eval(data1)
        q_data, pre_code, post_code = eval(data2)
        ev = pre_visual.count("\n") * 1
        if text == '':
            text = backup
        text_c = assist.connect(pre_code, text, post_code)
        with open('pythonL/practice.py', 'w') as f:
            f.write(text_c)
        op = subprocess.run('python pythonL/practice.py', shell=True, capture_output=True, text=True, timeout=3)
        out, err = op.stdout, op.stderr
        err = err.split('",')[-1]
        if len(out) < len(err) and pre_code != '':
            err = assist.reduce(err, pre_code)
        params = {'text': text, 
                 'out' : out, 
                 'err': err, 
                 'q_title': q_title, 
                 'q_sentence': q_sentence, 
                 'q_data': q_data,
                 "pre_code": pre_code, 
                 "pre_visual": pre_visual, 
                "post_code": post_code,
                "post_visual": post_visual, 
                "data1": data1,
                "data2": data2,
                "pk": pk,  "ev": ev}
        return render(request, 'question/basis.html', params)
    
    question = Basis.objects.filter(section = pk)
    s = random.randint(0, len(question)-1)
    question = question[s]

    q_sentence = question.question
    pre_code, post_code = question.pre_code, question.post_code
    pre_visual, post_visual = question.pre_visual, question.post_visual

    if question.category % 2 == 0: #コードで入力
        if question.category % 4 == 0:
            if question.category % 8 == 0:
                c_out = question.c_output.split('\n')
                c_list = random.sample(eval(c_out[0]), int(c_out[1]))
            else:
                c_range = question.c_output.split('\n')
                c_list = [random.choice(eval(x)) for x in c_range]
            i_range = question.i_range
            for i in range(len(c_list)):
                i_range = i_range.replace(f'/gvc{i}/', str(c_list[i]))
            i_range = i_range.split('\n')
        else:
            i_range = question.i_range.split('\n')
        d_list = [random.choice(eval(x)) for x in i_range]
        q_data = question.q_data
        e_answer = question.e_answer
        for i in range(len(d_list)):
            q_sentence = q_sentence.replace(f'/radc{i}/', str(d_list[i]))
            pre_code = pre_code.replace(f'/radc{i}/', repr(d_list[i]))
            pre_visual = pre_visual.replace(f'/radc{i}/', str(d_list[i]))
            q_data = q_data.replace(f'/radc{i}/', str(d_list[i]))
            e_answer = e_answer.replace(f'/radc{i}/', repr(d_list[i]))
        e_answer = assist.connect(pre_code, e_answer, post_code)
        with open('pythonL/collect.py', 'w') as f:
            f.write(e_answer)
        op = subprocess.run('python pythonL/collect.py', shell=True, capture_output=True, text=True, timeout=3)
        c_output = op.stdout
    else: #直接入力
        q_data = question.q_data.split('\n/nct/')
        c_output = question.c_output.split('/nct/')
        e_answer = question.e_answer.split('\n/nct/')
        c = random.randint(0, len(q_data)-2)
        q_data, c_output, e_answer = q_data[c], c_output[c], e_answer[c]

    
    user = request.user
    user.s_output = c_output
    user.s_answer = e_answer
    user.save()
    ev = pre_visual.count("\n") * 1

    q_title = question.name
    data1 = str([q_title, q_sentence, pre_visual, post_visual])
    data2 = str([q_data, pre_code, post_code])

    params ={'q_title': q_title, 
             'q_sentence': q_sentence, 
             'q_data': q_data, 
             "pre_code": pre_code, 
             "pre_visual": pre_visual, 
             "post_code": post_code, 
             "post_visual": post_visual, 
             "data1": data1,
             "data2": data2,
             "pk": pk, "ev": ev}
    return render(request, 'question/basis.html', params)


@login_required
def basis_a(request, pk):
    last = Basis.objects.order_by('section').last().section
    if request.method == 'POST':
        text = request.POST['text'] 
        backup = request.POST['backup'] 
        data2 = request.POST['data2']
        q_data, pre_code, post_code = eval(data2)
        if text == '':
            text = backup
        text_c = assist.connect(pre_code, text, post_code)
        with open('pythonL/practice.py', 'w') as f:
            f.write(text_c)
        op = subprocess.run('python pythonL/practice.py', shell=True, capture_output=True, text=True, timeout=3)
        out = op.stdout
        user = request.user
        c_output = user.s_output
        e_answer = user.s_answer
        c_output = c_output.replace('\r', '')
        e_answer = e_answer.replace('\r', '')
        if out == c_output:
            collect = True
        else:
            collect = False
        n, p = pk + 1, pk - 1
        params = {'text_c': text_c, 
                 'out' : out, 
                 'c_output': c_output, 
                 'e_answer': e_answer,
                 "collect": collect,
                 "pre_code": pre_code, 
                "post_code": post_code,
                "last": last, 
                "n": n, "p": p}
        return render(request, 'question/basis_a.html', params)
    params ={'c_output': "", 
             'e_answer': ""}
    return render(request, 'question/basis_a.html', params)
from django.shortcuts import render, redirect
from .models import CustomUser, IntroCourse, Basis, Quartet, Competition
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
def drill(request, un, pk):
    if request.method == 'POST':
        text = request.POST['text'] 
        backup = request.POST['backup'] 
        data1 = request.POST['data1']
        data2 = request.POST['data2']
        q_title, q_sentence, pre_visual, post_visual = eval(data1)
        q_data, pre_code, post_code, role = eval(data2)
        ev = pre_visual.count("\n") 
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
                "un": un, "pk": pk,  "ev": ev}
        return render(request, 'question/drill.html', params)
    
    question = Basis.objects.filter(unit = un, section = pk)
    s = random.randint(0, len(question)-1)
    question = question[s]

    q_sentence, role = question.question, question.role_code
    pre_code, post_code = question.pre_code, question.post_code
    pre_visual, post_visual = question.pre_visual, question.post_visual
    e_answer = question.e_answer.replace('/space/', '    ')
    i_range = question.i_range

    if question.category % 2 == 0: #コードで入力
        if question.category % 4 == 0:
            if question.category % 8 == 0:
                c_bbcl, c_out = question.c_output.split('\n/bbcl/')
                c_out, c_mrcl = c_out.split('\n/mrcl/')
                c_out = c_out.split('\n')
                c_list = random.sample(eval(c_out[0]), int(c_out[1]))
                if len(c_list) != 0:
                    c_list.append(random.choice(c_list))
                c_list = eval(c_bbcl) + c_list + eval(c_mrcl)
            else:
                c_range = question.c_output.split('\n')
                c_list = [random.choice(eval(x)) for x in c_range]
            for i in range(len(c_list)):
                i_range = i_range.replace(f'/gvc{i}/', str(c_list[i]))
            i_range = i_range.split('\n')
        else:
            i_range = i_range.split('\n')
        d_list = [random.choice(eval(x)) for x in i_range]
        q_data = question.q_data
        for i in range(len(d_list)):
            q_sentence = q_sentence.replace(f'/radc{i}/', str(d_list[i]))
            pre_code = pre_code.replace(f'/radc{i}/', repr(d_list[i]))
            pre_visual = pre_visual.replace(f'/radc{i}/', str(d_list[i]))
            post_code = post_code.replace(f'/radc{i}/', repr(d_list[i]))
            post_visual = post_visual.replace(f'/radc{i}/', str(d_list[i]))
            role = role.replace(f'/radc{i}/', repr(d_list[i]))
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
        e_answer = e_answer.split('\n/nct/') 
        c = random.randint(0, len(q_data)-2)     
        q_data, c_output, e_answer = q_data[c], c_output[c], e_answer[c]
        if pre_code != '':
            pre_code, pre_visual = pre_code.split('\n/nct/'), pre_visual.split('\n/nct/')
            pre_code, pre_visual = pre_code[c], pre_visual[c]
        if post_code != '':
            post_code, post_visual = post_code.split('\n/nct/'), post_visual.split('\n/nct/')
            post_code, post_visual = post_code[c], post_visual[c]

    
    if question.category % 3 == 0:
        pre_visual = assist.font(pre_visual)
        post_visual = assist.font(post_visual)
        if question.category % 9 == 0:
            pre_visual = assist.font_p(pre_visual)
            post_visual = assist.font_p(post_visual)
    
    user = request.user
    user.s_output = c_output
    user.s_answer = e_answer
    user.save()
    ev = pre_visual.count("\n") 

    q_title = question.title.split('/')[0]
    data1 = str([q_title, q_sentence, pre_visual, post_visual])
    data2 = str([q_data, pre_code, post_code, role])

    params ={'q_title': q_title, 
             'q_sentence': q_sentence, 
             'q_data': q_data, 
             "pre_code": pre_code, 
             "pre_visual": pre_visual, 
             "post_code": post_code, 
             "post_visual": post_visual, 
             "data1": data1,
             "data2": data2,
             "un": un, "pk": pk, "ev": ev}
    return render(request, 'question/drill.html', params)


@login_required
def drill_a(request, un, pk):
    un_last = Basis.objects.order_by('unit').last().unit
    pk_last = Basis.objects.filter(unit = un).order_by('section').last().section
    if un >=2:
        pu_last = Basis.objects.filter(unit = un - 1).order_by('section').last().section
    else:
        pu_last = 1
    if request.method == 'POST':
        text = request.POST['text'] 
        backup = request.POST['backup'] 
        data2 = request.POST['data2']
        q_data, pre_code, post_code, role = eval(data2)
        if text == '':
            text = backup
        text_c = assist.connect(pre_code, text, post_code)
        with open('pythonL/practice.py', 'w') as f:
            f.write(text_c)
        op = subprocess.run('python pythonL/practice.py', shell=True, capture_output=True, text=True, timeout=3)
        drill_a.out = op.stdout
        user = request.user
        c_output = user.s_output
        e_answer = user.s_answer
        c_output = c_output.replace('\r', '')
        e_answer = e_answer.replace('\r', '')
        if drill_a.out == c_output:
            drill_a.collect = True
        else:
            drill_a.collect = False
        exec(role)
        nu, pu = un + 1, un - 1
        np, pp = pk + 1, pk - 1
        params = {'text_c': text_c, 
                 'out' : drill_a.out, 
                 'c_output': c_output, 
                 'e_answer': e_answer,
                 "collect": drill_a.collect,
                 "pre_code": pre_code, 
                "post_code": post_code,
                "un_last": un_last, "pk_last": pk_last, "pu_last": pu_last, 
                "un": un, "pk": pk, "nu": nu, "pu": pu, "np": np, "pp": pp}
        return render(request, 'question/drill_a.html', params)
    params ={'c_output': "", 
             'e_answer': "",
             "un_last": un_last, "pk_last": pk_last, "pu_last": pu_last, 
               "un": un, "pk": pk, "nu": nu, "pu": pu, "np": np, "pp": pp}
    return render(request, 'question/drill_a.html', params)
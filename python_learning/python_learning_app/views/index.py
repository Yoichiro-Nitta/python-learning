from django.shortcuts import render, redirect
from python_learning_app.models.index import CustomUser, IntroCourse
from python_learning_app.forms import SignupForm, LoginForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
import random
import subprocess

def top_page(request):
    return render(request, 'python_learning/index.html')

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
    param = {'form': form}
    
    return render(request, 'user/login.html', param)

def login_req(request):
    return render(request, 'user/login_req.html')

def logout_view(request):
    logout(request)
    return render(request, 'user/logout.html')


def intro(request):
    # データベースから各回の最初のデータを取得（第１回、第２回といった具合で、「回」で分類）
    introforewords = IntroCourse.objects.filter(order = 1)
    # sectionで昇順に並べ替え
    introforewords = introforewords.order_by('section')
    
    params ={"introforewords": introforewords}

    return render(request, 'python_learning/intro.html', params)

def intro_ex(request, pk):
    # データベースから回毎のデータを取得（第１回、第２回といった具合で、「回」で分類）
    explanations = IntroCourse.objects.filter(section = pk)
    explanations = explanations.order_by('order')

    # 各回の最初のデータにはタイトルが付与されているので、それを取得
    title = explanations.first().title

    # 前と後の回の数値を格納
    n, p = pk + 1, pk - 1

    # エディター使用時の処理
    if request.method == 'POST':
        text = request.POST['text'] 
        backup = request.POST['backup'] 

        # 入力内容に変化がない場合の対応
        if text == '':
            text = backup

        # pythonファイルに書き込み、出力を得る
        with open('sheet/intro.py', 'w') as f:
            f.write(text)
        op = subprocess.run('python sheet/intro.py', shell=True, capture_output=True, text=True, timeout=3)
        out, err  = op.stdout, op.stderr

        # 標準エラーの内容を「line~」以降に限定
        err = err.split('",')[-1]

        params = {
        'text': text, 'out' : out, 'err': err, 
        "explanations": explanations, "title": title, "pk": pk, "n": n, "p": p}

        return render(request, 'python_learning/intro_ex.html', params)
    
    params = {"explanations": explanations, "title":title, "pk": pk, "n": n, "p": p}

    return render(request, 'python_learning/intro_ex.html', params)






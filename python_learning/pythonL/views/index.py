from django.shortcuts import render, redirect
from pythonL.models import CustomUser, IntroCourse, Basis, Quartet, Competition
from pythonL.forms import SignupForm, LoginForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
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
    # データベースから各回の最初のデータを取得（第１回、第２回といった具合で、「回」で分類）
    introforewords = IntroCourse.objects.filter(order = 1)
    # sectionで昇順に並べ替え
    introforewords = introforewords.order_by('section')
    
    params ={"introforewords": introforewords}
    return render(request, 'pythonL/intro.html', params)

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
        with open('pythonL/intro.py', 'w') as f:
            f.write(text)
        op = subprocess.run('python pythonL/intro.py', shell=True, capture_output=True, text=True, timeout=3)
        out, err  = op.stdout, op.stderr

        # 標準エラーの内容を「line~」以降に限定
        err = err.split('",')[-1]

        params = {
        'text': text, 'out' : out, 'err': err, 
        "explanations": explanations, "title": title, "pk": pk, "n": n, "p": p}
        return render(request, 'pythonL/intro_ex.html', params)
    params = {"explanations": explanations, "title":title, "pk": pk, "n": n, "p": p}
    return render(request, 'pythonL/intro_ex.html', params)

def questions(request):
    # 問題の大区分数を取得
    un_last = Basis.objects.order_by('unit').last().unit

    # 大区分毎のクエリセットをリストに格納
    unit_list = [Basis.objects.filter(unit = i+1, q_key = True).order_by('section') for i in range(un_last)]

    # 大区分名をkey、大区分クエリセットをvalueとして辞書に格納
    units ={}
    for i in range(un_last):
        units[unit_list[i].first().major_h] = unit_list[i]
    
    # 5の倍数毎に２重線を引くために、5の倍数のリストを作成
    multiple5 = [ 5 * x for x in range(1,11) ]
    params = {"units": units, "un_last": un_last, "multiple5": multiple5}
    return render(request, 'pythonL/questions.html', params)

def p_like(request):
    # 例題（問題番号０）以外の問題を取得
    questions = Competition.objects.filter(section__gte = '1')
    # ページの分割
    paginator = Paginator(questions, 10)
    # クエリパラメーターからページ番号取得
    number = int(request.GET.get('p', 1))
    # 取得したページ番号のページを取得
    page_obj = paginator.page(number)

    params = {'page_obj' : page_obj}
    return render(request, 'pythonL/p_like.html', params)

def p_like_ex(request):
    return render(request, 'pythonL/p_like_ex.html')

def pe_study(request):
    python3_list = [("Pythonの基本", 1),
                    ("計算・文字列・リスト", 2),
                    ("制御構文", 3),]
    params = {"python3_list": python3_list}
    return render(request, 'pythonL/pe_study.html', params)

def p_study(request, un):
    # 大区分unの問題を取得
    questions = Quartet.objects.filter(unit = un)
    # ページの分割
    paginator = Paginator(questions, 10)
    # クエリパラメーターからページ番号取得
    number = int(request.GET.get('p', 1))
    # 取得したページ番号のページを取得
    page_obj = paginator.page(number)

    params = {'page_obj' : page_obj, "un": un}
    return render(request, 'pythonL/p_study.html', params)

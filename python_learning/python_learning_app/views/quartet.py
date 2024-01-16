from django.shortcuts import render, redirect
from python_learning_app.models.index import CustomUser
from python_learning_app.models.questions import Quartet
from django.contrib.auth.decorators import login_required
from Crypto.Cipher import AES
from django.core.paginator import Paginator
from application import key
import random

def pe_study(request):
    python3_list = [("Pythonの基本", 1),
                    ("計算・文字列・リスト", 2),
                    ("制御構文", 3),]
    params = {"python3_list": python3_list}

    return render(request, 'quartet/pe_study.html', params)

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

    return render(request, 'quartet/p_study.html', params)

def quartet(request, un, pk):
     #データベースからデータを取得
    question = Quartet.objects.get(unit= un, section = pk)
    title, sentence, code = question.title, question.question, question.question_code
    code = code.replace('____', '<span style="color: white;">____</span>')
    choices = [(question.choices1, 1), (question.choices2, 2), (question.choices3, 3), (question.choices4, 4)]
    shuffled = random.sample(choices, 4)
    pn = (pk - 1) // 10 + 1
    params = {"title": title, "sentence": sentence, "code": code, "shuffled": shuffled, 
              "un": un, "pk": pk, "pn": pn}
    
    return render(request, 'quartet/quartet.html', params)


def quartet_a(request, un, pk):
    # データベースからデータを取得
    question = Quartet.objects.get(unit= un, section = pk)
    title = question.title
    pn = (pk - 1) // 10 + 1
    if request.method == 'POST':
        choice = int(request.POST['choice'])
        if question.answer_idx == choice:
            judge = True
        else:
            judge = False
        params = {"title": title, "judge": judge, "un": un, "pk": pk, "pn": pn}

        return render(request, 'quartet/quartet_a.html', params) 
    params = {"title": title, "pk": pk, "pn": pn} 

    return render(request, 'quartet/quartet_a.html', params) 

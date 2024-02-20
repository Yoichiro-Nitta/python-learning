from django.shortcuts import render, redirect
from python_learning_app.models.index import CustomUser
from python_learning_app.models.questions import Quartet
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from application import key
import random

def chapter(request):
    python3_list = [("Pythonの基本", 1),
                    ("計算・文字列・リスト", 2),
                    ("制御構文", 3),]
    params = {"python3_list": python3_list}

    return render(request, 'quartet/chapter.html', params)

def q_list(request, un):
    # 大区分unの問題を昇順で取得
    questions = Quartet.objects.filter(unit = un).order_by('section')
    # ページの分割
    paginator = Paginator(questions, 10)
    # クエリパラメーターからページ番号取得
    number = int(request.GET.get('p', 1))
    # 取得したページ番号のページを取得
    page_obj = paginator.page(number)
    # ページ数のリストを取得
    page_range = [x for x in paginator.page_range]

    params = {'page_obj' : page_obj, "page_range": page_range, "un": un}

    return render(request, 'quartet/q_list.html', params)

def quartet(request, un, pk):
     #データベースからデータを取得
    question = Quartet.objects.get(unit= un, section = pk)
    title, sentence, code = question.title, question.question, question.question_code

    # アンダースコアを白色に変換する処理 
    code = code.replace('____', '<span style="color: white;">____</span>')
    choices = [question.choices1, question.choices2, question.choices3, question.choices4]
    choices = list(map(lambda x : x.replace('____', '<span style="color: white;">____</span>'), choices))

    # 選択肢をまとめる
    choices = [(y, x+1) for x, y in enumerate(choices)]
    shuffled = random.sample(choices, 4)
    pn = (pk - 1) // 10 + 1
    params = {"title": title, "sentence": sentence, "code": code, "shuffled": shuffled, 
              "frame": question.frame, "un": un, "pk": pk, "pn": pn}
    
    return render(request, 'quartet/quartet.html', params)


def quartet_a(request, un, pk):
    # データベースからデータを取得
    question = Quartet.objects.get(unit= un, section = pk)
    title = question.title
    # 問題のページ数を計算
    pn = (pk - 1) // 10 + 1

    num_of_series = len(Quartet.objects.filter(unit = un))

    pk_b, pk_a = pk - 1, pk + 1

    if request.method == 'POST':
        choice = int(request.POST['choice'])
        if question.answer_idx == choice:
            judge = True
        else:
            judge = False
        params = {"title": title, "judge": judge, "num_of_series": num_of_series,
                   "un": un, "pk": pk, "pk_b": pk_b, "pk_a": pk_a, "pn": pn}

        return render(request, 'quartet/quartet_a.html', params) 
    params = {"title": title, "num_of_series": num_of_series,
               "pk": pk, "pk_b": pk_b, "pk_a": pk_a, "pn": pn} 

    return render(request, 'quartet/quartet_a.html', params) 

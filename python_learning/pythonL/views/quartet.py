from django.shortcuts import render, redirect
from pythonL.models import CustomUser, IntroCourse, Quartet
from django.contrib.auth.decorators import login_required
from Crypto.Cipher import AES
from application import key
import random


def quartet(request, un, pk):
     #データベースからデータを取得
    question = Quartet.objects.get(unit= un, section = pk)
    title, sentence, code = question.title, question.question, question.question_code
    code = code.replace('____', '<span style="color: white;">____</span>')
    choices = [(question.choices1, 1), (question.choices2, 2), (question.choices3, 3), (question.choices4, 4)]
    shuffled = random.sample(choices, 4)
    pn = pk // 10 + 1
    params = {"title": title, "sentence": sentence, "code": code, "shuffled": shuffled, 
              "un": un, "pk": pk, "pn": pn}
    return render(request, 'question/quartet.html', params)


def quartet_a(request, un, pk):
    # データベースからデータを取得
    question = Quartet.objects.get(unit= un, section = pk)
    title = question.title
    pn = pk // 10 + 1
    if request.method == 'POST':
        choice = int(request.POST['choice'])
        if question.answer_idx == choice:
            judge = True
        else:
            judge = False
        params = {"title": title, "judge": judge, "un": un, "pk": pk, "pn": pn}
        return render(request, 'question/quartet_a.html', params) 
    params = {"title": title, "pk": pk, "pn": pn} 
    return render(request, 'question/quartet_a.html', params) 

from django.shortcuts import render, redirect
from python_learning_app.models.questions import IntroCourse, Basis
from django.contrib.auth.decorators import login_required
import subprocess



def intro(request):
    # データベースから各回の最初のデータを取得（第１回、第２回といった具合で、「回」で分類）
    introforewords = IntroCourse.objects.filter(order = 1)
    # sectionで昇順に並べ替え
    introforewords = introforewords.order_by('section')
    
    params ={"introforewords": introforewords}

    return render(request, 'intro/intro.html', params)


def intro_ex(request, pk):
    # データベースから回毎のデータを取得（第１回、第２回といった具合で、「回」で分類）
    explanations = IntroCourse.objects.filter(section = pk).order_by('order')

    # 基本問題をunit単位で取得
    Basis_questions = Basis.objects.filter(unit = pk, q_key = True).order_by('section')
    # unitに対応する基本問題のタイトルを取得
    questions_title = [q.title for q in Basis_questions]
    questions_title = list(map(lambda x : x.split('/')[0], questions_title))
    # 問題番号とタイトルをリストにまとめる
    questions_list = [(x + 1, y) for x, y in enumerate(questions_title)]

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
        'text': text, 'out' : out, 'err': err, "questions_list": questions_list, 
        "explanations": explanations, "title": title, "pk": pk, "n": n, "p": p}

        return render(request, 'python_learning/intro_ex.html', params)
    
    params = {"explanations": explanations, "title":title, "questions_list": questions_list,
              "pk": pk, "n": n, "p": p}

    return render(request, 'intro/intro_ex.html', params)

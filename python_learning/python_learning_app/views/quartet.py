from django.shortcuts import render
from python_learning_app.models.questions import Quartet, QuartetResult
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from application import key
import random

def chapter(request):
    """Python知識問題の章を表示するView"""

    python3_list = [("Pythonの基本", 1),
                    ("計算・文字列・リスト", 2),
                    ("制御構文", 3),
                     ("データ構造", 4),]
    params = {"python3_list": python3_list}

    return render(request, 'quartet/chapter.html', params)

def q_list(request, un):
    """Python知識問題各章の問題一覧を表示するView
    
    パラメーター説明

    page_obj:               Paginatorのオブジェクト
    questions_and_results:  page_obj、解答履歴をまとめたイテラブルオブジェクト
    page_range:             ページ番号のリスト（ページのリンクボタンで使用）
    un:                     章番号

    """

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

    results = [] # 挑戦履歴格納用リスト
    for question in page_obj:
        record = QuartetResult.objects.filter(user_id = request.user.id, connection_key = question.primary_key).exists()
        if record:
            result = QuartetResult.objects.get(user_id = request.user.id, connection_key = question.primary_key)
            results.append(result.result)
        else:
            results.append(None)
    
    # forloop用にまとめる
    questions_and_results = zip(page_obj, results)

    params = {'page_obj' : page_obj,'questions_and_results': questions_and_results, "page_range": page_range, "un": un}

    return render(request, 'quartet/q_list.html', params)

@login_required
def quartet(request, un, pk):
    """Python知識問題の解答入力View

    パラメーター説明

    title:                  問題タイトル
    sentence:               問題文
    code:                   Pythonコード
    shuffled:               シャッフル済みの選択肢一覧
    frame:                  選択肢がコードの場合 True
    un:                     章番号
    pk:                     問題番号
    pn:                     ページ番号

    """
     #データベースからデータを取得
    question = Quartet.objects.get(unit= un, section = pk)
    title, sentence, code, frame = question.title, question.question, question.question_code, question.frame

    # アンダースコアをスペースに変換する処理
    if code:
        code = "<pre>" + code + "</pre>"
    choices = [question.choices1, question.choices2, question.choices3, question.choices4]
    if frame:
        choices = list(map(lambda x : ("<pre>" + x + "</pre>"), choices))

    # 選択肢をまとめる
    choices = [(y, x+1) for x, y in enumerate(choices)]
    shuffled = random.sample(choices, 4)
    pn = (pk - 1) // 10 + 1
    params = {"title": title, "sentence": sentence, "code": code, "shuffled": shuffled, 
              "frame": question.frame, "un": un, "pk": pk, "pn": pn}
    
    return render(request, 'quartet/quartet.html', params)

@login_required
def quartet_a(request, un, pk):
    """Python知識問題の解答結果View

    パラメーター説明

    title:                  問題タイトル
    judge:                  judge
    num_of_series:          問題が属する章の問題数
    explanation:            解説
    un:                     章番号
    pk:                     問題番号
    pk_b:                   問題番号 - 1
    pk_a:                   問題番号 + 1
    pn:                     ページ番号

    """
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

        
        quartet_result, created = QuartetResult.objects.get_or_create(user_id = request.user.id, connection_key = question)

        if created:
            quartet_result.result = judge
        elif judge or quartet_result.result:
            quartet_result.result = True
        else:
            quartet_result.result = False
        
        quartet_result.save()

        explanation = question.explanation
            
        params = {"title": title, "judge": judge, "num_of_series": num_of_series,
                  "explanation": explanation, "un": un, "pk": pk, "pk_b": pk_b, "pk_a": pk_a, "pn": pn}

        return render(request, 'quartet/quartet_a.html', params) 
    
    params = {"title": title, "num_of_series": num_of_series,
               "pk": pk, "pk_b": pk_b, "pk_a": pk_a, "pn": pn} 

    return render(request, 'quartet/quartet_a.html', params) 

from django.shortcuts import render
from .drill_class import QuestionsListView, DrillView, DrillAnswerView
from python_learning_app.models.questions import IntroCourse, Basis
from django.contrib.auth.mixins import LoginRequiredMixin
from application import assist
import numpy as np
import random
import subprocess

# 問題モデルの一覧リスト
questions_list_urls = ['questions_beginner',
                       ]


class QuestionsBeginner(QuestionsListView):
    model = [Basis, 0]


def practice(request):

    model_num = int(request.GET.get('m'))

    question_index_url = "python_learning:" + questions_list_urls[model_num]

    if request.method == 'POST':
        text = request.POST['text'] 
        backup = request.POST['backup'] 
        # 入力内容に変化がない場合の対応
        if text == '':
            text = backup

        # 危険なコードが含まれている場合の変換処理
        text = assist.security(text)

        # pythonファイルに書き込み、出力を得る
        with open('sheet/practice.py', 'w') as f:
            f.write(text)
        op = subprocess.run('python sheet/practice.py', shell=True, capture_output=True, text=True, timeout=3)
        out, err = op.stdout, op.stderr
        # 標準エラーの内容を「line~」以降に限定
        err = err.split('",')[-1]
        params = {'text': text, 'out' : out, 'err': err, 
                  "model_num": model_num, "question_index_url": question_index_url}

        return render(request, 'drill/practice.html', params)
    
    params = {"model_num": model_num, "question_index_url": question_index_url}

    return render(request, 'drill/practice.html', params)

def practice_a(request):

    model_num = int(request.GET.get('m'))

    question_index_url = "python_learning:" + questions_list_urls[model_num]

    if request.method == 'POST':
        text = request.POST['text']
        backup = request.POST['backup']
        if text == '':
            text = backup
        
        # 危険なコードが含まれている場合の変換処理
        text = assist.security(text)

        with open('sheet/practice.py', 'w') as f:
            f.write(text)
        op = subprocess.run('python sheet/practice.py', shell=True, capture_output=True, text=True, timeout=3)
        out = op.stdout
        ans = "Hello, World!\n"

        # 提出されたコードによる正誤判定
        if out == ans:
            correct = True
        else:
            correct = False
        
        params = {'text': text, 'out' : out, 'correct': correct, "question_index_url": question_index_url}

        return render(request, 'drill/practice_a.html', params)
    
    return render(request, 'drill/practice_a.html', {"question_index_url": question_index_url})


# ーーーーーーーーーーーー↓ここから問題ページのView↓ーーーーーーーーーーーー




class DrillBeginner(LoginRequiredMixin, DrillView):
    model = Basis
    index_url_name = questions_list_urls[0]
    template_name = 'drill/drill_question.html'
    url_name = 'drill_beginner'
    course = IntroCourse


class DrillBeginnerSeries(LoginRequiredMixin, DrillView):
    model = Basis
    index_url_name = questions_list_urls[0]
    template_name = 'drill/drill_questions.html'
    url_name = 'drill_beginners'
    course = None

    def choose_question(self, **kwargs):
        qn = kwargs['qn']
        question = self.__class__.model.objects.all()
        if qn == 1: # 全問題からランダムで取得
            all_questions = [x for x in range(len(question))]
            # 問題をランダムで１０個選び、最初のインデックスに正解数を付与
            choosed_questions = random.sample(all_questions, 10)
            choosed_questions.insert(0,0)
            s = choosed_questions[qn]
            question = question[s]
            # クエリを生成
            query_list = list(map(lambda x : np.base_repr(x, 32), choosed_questions))
            query = 'X'.join(query_list)
        else: # クエリ情報から取得
            query = self.request.GET.get('query')
            query_list = query.split('X')
            query_list = list(map(lambda x : int(x, 32), query_list))
            s = query_list[qn]
            question = question[s]
        
        add_dict = {'query': query}
        urls = {**kwargs, **add_dict} 

        return question, urls
    
    def post_func(self, **kwargs):
        qn = kwargs['qn']
        query = self.request.GET.get('query')
        return {'urls': {'query': query, 'qn': qn}}


# ーーーーーーーーーーーー↓ここから解答ページのView↓ーーーーーーーーーーーー




class DrillBeginnerAnswer(LoginRequiredMixin, DrillAnswerView):
    model = Basis
    index_url_name = questions_list_urls[0]
    template_name = 'drill/drill_answer.html'
    url_name = 'drill_beginner'
        


class DrillBeginnerSeriesAnswer(LoginRequiredMixin, DrillAnswerView):
    model = Basis
    index_url_name = questions_list_urls[0]
    template_name = 'drill/drill_answers.html'
    url_name = 'drill_beginners'

    def pages(self, **kwargs):
        return None
    
    def outcome(self, correct, urls):
        query = self.request.GET.get('query')
        query_list = query.split('X')
        num_of_correct = int(query_list[0])
        if correct:
            num_of_correct += 1
            query_list[0] = str(num_of_correct)
            query = 'X'.join(query_list)
        qn = urls['qn']
        qn += 1
        urls['qn'] = qn
        add_query = {'query': query, 'num_of_correct': num_of_correct}
        urls = {**urls, **add_query}
        return correct, urls
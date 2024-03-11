from django.shortcuts import render
from django.views.generic import View
from python_learning_app.models.questions import IntroCourse, Basis
import subprocess
# ↓現状使用していないのでコメントアウト中
# from django.contrib.auth.decorators import login_required


def intro(request):
    """入門講座一覧のView"""
    
    # データベースから各回の最初のデータを取得（第１回、第２回といった具合で、「回」で分類）
    introforewords = IntroCourse.objects.filter(order = 1)
    # sectionで昇順に並べ替え
    introforewords = introforewords.order_by('section')
    
    params ={"introforewords": introforewords}

    return render(request, 'intro/intro.html', params)


class CourseView(View):

    """Python入門講座のViewのスーパークラス
    
    パラメーター説明

    text:                   ユーザーの入力内容
    out:                    出力結果(出力時)
    err:                    出力結果(エラー時)
    questions_list:         関連する基本問題の番号とタイトル
    explanations:           説明文のクエリセット
    title:                  関連する基本問題のタイトルのクエリセット
    pk:                     今回の講座番号
    next_num:               次回の講座番号
    previous_num:           前回の講座番号
    next_page:              次回講座の存在の有無
    
    """

    # 共有変数を定義
    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)

        # データベースから回毎のデータを取得（第１回、第２回といった具合で、「回」で分類）
        self.explanations = self.__class__.course.objects.filter(section = kwargs['pk']).order_by('order')

        # 基本問題をunit単位で取得
        questions = self.__class__.questions.objects.filter(unit = kwargs['pk'], q_key = True).order_by('section')

        # unitに対応する基本問題のタイトルを取得
        questions_title = [q.title for q in questions]
        questions_title = list(map(lambda x : x.split('/')[0], questions_title))

        # 問題番号とタイトルをリストにまとめる
        self.questions_list = [(x + 1, y) for x, y in enumerate(questions_title)]

        # 各回の最初のデータにはタイトルが付与されているので、それを取得
        self.title = self.explanations.first().title

        # 前と後の回の数値を格納
        self.next_num, self.previous_num = kwargs['pk'] + 1, kwargs['pk'] - 1

        # 次のページの存在を格納
        self.next_page = self.__class__.course.objects.filter(section = self.next_num).exists()
    
    def get(self, request, *args, **kwargs):

        params = {"explanations": self.explanations, "title":self.title,
                  "questions_list": self.questions_list, "pk": kwargs['pk'], 
                  "next_num": self.next_num, "previous_num": self.previous_num, "next_page": self.next_page}
        
        return render(request, self.__class__.template_name, params)
    
    def post(self, request, *args, **kwargs):
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

        params = {"text": text, "out" : out, "err": err, "questions_list": self.questions_list, 
                  "explanations": self.explanations, "title": self.title, "pk": kwargs['pk'], 
                  "next_num": self.next_num, "previous_num": self.previous_num, "next_page": self.next_page}
        
        return render(request, self.__class__.template_name, params)

class IntroCourseView(CourseView):

    course = IntroCourse
    questions = Basis
    template_name = 'intro/intro_ex.html'


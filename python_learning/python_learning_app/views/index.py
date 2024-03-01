from django.shortcuts import render, redirect
from python_learning_app.models.index import CustomUser, IntroCourse, News
from python_learning_app.models.questions import Basis
from python_learning_app.forms import SignupForm, LoginForm
from django.views.generic import FormView
from django.urls import reverse_lazy
from python_learning_app.forms import ContactForm
from django.contrib import messages
from django.core.mail import EmailMessage
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
import os
import json
import subprocess

# 本番環境でエラー表示する場合は以下をuncomment
"""
from django.views.decorators.csrf import requires_csrf_token
from django.http import HttpResponseServerError

@requires_csrf_token
def my_customized_server_error(request, template_name='500.html'):
    import sys
    from django.views import debug
    error_html = debug.technical_500_response(request, *sys.exc_info()).content
    return HttpResponseServerError(error_html)
"""


def top_page(request):
    news = News.objects.all().order_by('date').reverse()
    if len(news) < 3:
        recent = news[0:len(news)]
    else:
        recent = news[0:3]
    
    params = {'recent': recent}

    return render(request, 'python_learning/index.html', params)


def news_list(request):
    news = News.objects.all().order_by('date').reverse()
    # ページの分割
    paginator = Paginator(news, 10)
    # クエリパラメーターからページ番号取得
    number = int(request.GET.get('p', 1))
    # 取得したページ番号のページを取得
    page_obj = paginator.page(number)
    # ページ数
    last = paginator.num_pages
    # 現在のページ番号に応じて表示するページ数のリストを作成
    if last <= 5:
        page_range = [x for x in paginator.page_range]
    elif number <= 3:
        page_range = [1, 2, 3, 4, '…']
    elif last - number <= 2:
        page_range = ['…', last - 3, last - 2, last - 1, last]
    else:
        page_range = ['…', number - 1, number, number + 1, '…']

    params = {'page_obj' : page_obj, "page_range": page_range}

    return render(request, 'python_learning/news_list.html', params)

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


class ContactView(FormView):

    # テンプレート
    template_name = "python_learning/contact.html"
    
    # フォームクラス
    form_class = ContactForm

    # お問い合わせ送信成功後URL
    success_url = reverse_lazy("python_learning:contact")

    def form_valid(self, form):
        """お問い合わせ送信処理"""

        # パラメータ取得
        name = form.cleaned_data["name"]
        email = form.cleaned_data["email"]
        title = form.cleaned_data["title"]
        message_param = form.cleaned_data["message"]

        if "EMAIL_HOST" and "EMAIL_HOST_PASS" in os.environ:
            e_mail = os.environ["EMAIL_HOST"]
        else:
            with open("settings.json", "r", encoding="utf-8") as f:
                data = json.load(f)
            
            e_mail = data["EMAIL_HOST"]

        # お問い合わせメールの送信処理
        subject = f"お問い合わせ: {title}"
        message = f"名前: {name}\nメールアドレス: {email}\n\n{message_param}"
        from_email = e_mail  # 送信元のメールアドレス
        recipient_list = [e_mail]  # 受信者のメールアドレスリスト

        msg = EmailMessage(
            subject=subject, body=message, from_email=from_email, to=recipient_list
        )

        try:
            msg.send()
            messages.success(self.request, "送信完了しました。")
        except Exception as e:
            messages.error(self.request, f"送信に失敗しました。エラー：{e}")

        return super().form_valid(form)


def intro(request):
    # データベースから各回の最初のデータを取得（第１回、第２回といった具合で、「回」で分類）
    introforewords = IntroCourse.objects.filter(order = 1)
    # sectionで昇順に並べ替え
    introforewords = introforewords.order_by('section')
    
    params ={"introforewords": introforewords}

    return render(request, 'python_learning/intro.html', params)

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

    return render(request, 'python_learning/intro_ex.html', params)






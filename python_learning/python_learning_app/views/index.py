from django.shortcuts import render
from python_learning_app.models.index import News
from python_learning_app.forms import SignupForm, LoginForm
from django.views.generic import  TemplateView, FormView, CreateView
from django.urls import reverse_lazy
from python_learning_app.forms import ContactForm
from django.contrib import messages
from django.core.mail import EmailMessage
from django.contrib.auth import login, logout, authenticate
from django.core.paginator import Paginator
from config.settings import DEBUG
import os
import json

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
    
    params = {'recent': recent, "debug": DEBUG}

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

class SignupView(CreateView):
    """ ユーザー登録用ビュー """
    form_class = SignupForm # 作成した登録用フォームを設定
    template_name = "user/signup.html" 
    success_url = reverse_lazy("python_learning:signed_view") # ユーザー作成後のリダイレクト先ページ

    def form_valid(self, form):
        # ユーザー作成後にそのままログイン状態にする設定
        response = super().form_valid(form)
        account_id = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password1")
        user = authenticate(account_id=account_id, password=password)
        login(self.request, user)
        return response
    

class SignedView(TemplateView):
    """ 登録完了画面 """
    template_name = "user/signed.html"

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user:
                login(request, user)

                return render(request, 'user/loggedin.html')
            
        else:
            err_message = "ログインに失敗しました。ユーザー名とパスワードを確認してください。"
            form = LoginForm()
            param = {'form': form, "err_message": err_message}
            return render(request, 'user/login.html', param)
            
    else:
        form = LoginForm()

    err_message = ""
    param = {'form': form, "err_message": err_message}
    
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

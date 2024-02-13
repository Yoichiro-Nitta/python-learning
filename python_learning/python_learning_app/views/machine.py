from django.shortcuts import render, redirect
from python_learning_app.models.index import CustomUser
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import FileResponse
import random

def machine_learning(request):
    # タイトルのリスト
    title = ['Pandas基礎', '機械学習基礎', 'クラス分類演習']
    # 解説URLのリスト
    url1 = ['https://colab.research.google.com/drive/1U9Z0EhotAtg3FgGgCTGyTeTf4-N3Pcuy?usp=sharing',
           'https://colab.research.google.com/drive/1ODvvAs3RAyyJPTzkLTY4rx8lMGSZNcXR?usp=sharing',
           'https://colab.research.google.com/drive/1WWWLaQNZbLKMHcEZ60YIF3F3fAAk3Xa3?usp=sharing']
    # 演習URLのリスト
    url2 = ['https://colab.research.google.com/drive/1VncELpgIlwh3TQDKnL5EnKIvZ6BhrhSo?usp=sharing',
            '',
            'https://colab.research.google.com/drive/1U2KsqvntC-6Gh3DLIZ95A7qu3o68dG4j?usp=sharing']
    # ダウンロード番号のリスト
    num = [i+1 for i in range(len(url1))]
    # ダウンロードファイルのリスト
    file = ['Pandas_Basis.zip', 'practice.zip', 'machine_learning.zip']
    practice = zip(title, url1, url2, num, file)
    params = {'practice': practice}

    return render(request, 'machine/machine_learning.html', params)

def how_to(request):

    return render(request, 'machine/how_to.html')


def download(request, pk):
    file = ['Pandas_Basis.zip', 'practice.zip', 'machine_learning.zip']
    file_path = 'downloads/' + file[pk - 1]
    filename = file[pk - 1]
    return FileResponse(open(file_path, "rb"), as_attachment=True, filename=filename)
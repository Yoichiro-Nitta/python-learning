from django.shortcuts import render
from django.http import FileResponse
# ↓現状使用していないのでコメントアウト中
# from django.core.paginator import Paginator

def machine_learning(request):
    """機械学習一覧のView"""

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
    """Google Colaboratoryの使い方のView"""

    return render(request, 'machine/how_to.html')


def download(request, pk):
    """ダウンロード用のView"""
    file = ['Pandas_Basis.zip', 'practice.zip', 'machine_learning.zip']
    file_path = 'downloads/' + file[pk - 1]
    filename = file[pk - 1]
    return FileResponse(open(file_path, "rb"), as_attachment=True, filename=filename)
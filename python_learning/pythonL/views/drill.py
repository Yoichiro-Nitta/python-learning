from django.shortcuts import render, redirect
from pythonL.models import CustomUser, IntroCourse, Basis, Quartet, Competition
from django.contrib.auth.decorators import login_required
from Crypto.Cipher import AES
from application import assist, pllist, key
import random
import subprocess

def practice(request):
    if request.method == 'POST':
        text = request.POST['text'] 
        backup = request.POST['backup'] 
        # 入力内容に変化がない場合の対応
        if text == '':
            text = backup
        # pythonファイルに書き込み、出力を得る
        with open('pythonL/practice.py', 'w') as f:
            f.write(text)
        op = subprocess.run('python pythonL/practice.py', shell=True, capture_output=True, text=True, timeout=3)
        out, err = op.stdout, op.stderr
        # 標準エラーの内容を「line~」以降に限定
        err = err.split('",')[-1]
        params = {
        'text': text, 'out' : out, 'err': err}
        return render(request, 'pythonL/practice.html', params)
    return render(request, 'pythonL/practice.html')

def practice_a(request):
    if request.method == 'POST':
        text = request.POST['text']
        backup = request.POST['backup']
        if text == '':
            text = backup
        with open('pythonL/practice.py', 'w') as f:
            f.write(text)
        op = subprocess.run('python pythonL/practice.py', shell=True, capture_output=True, text=True, timeout=3)
        out = op.stdout
        ans = "Hello, World!\n"

        # 提出されたコードによる正誤判定
        if out == ans:
            collect = True
        else:
            collect = False
        
        params = {
        'text': text, 'out' : out, 'collect': collect}
        return render(request, 'pythonL/practice_a.html', params)
    return render(request, 'pythonL/practice_a.html')

@login_required
def drill(request, un, pk):
    if request.method == 'POST':
        text = request.POST['text'] 
        backup = request.POST['backup'] 
        data1 = request.POST['data1']
        data2 = request.POST['data2']

        # まとめられて送られた内容を再び展開
        q_title, q_sentence, pre_visual, post_visual = eval(data1)
        q_data, pre_code, post_code, role, ciphertext, tag = eval(data2)
        ev = pre_visual.count("\n") 
        if text == '':
            text = backup

        # 事前に与えられているコードと統合
        text_c = assist.connect(pre_code, text, post_code)

        with open('pythonL/practice.py', 'w') as f:
            f.write(text_c)
        op = subprocess.run('python pythonL/practice.py', shell=True, capture_output=True, text=True, timeout=3)
        out, err = op.stdout, op.stderr
        err = err.split('.py",')[-1]

        # エラー表示の際に、エディターの行数が表示されるように工夫
        if len(out) < len(err) and pre_code:
            err = assist.reduce(err, pre_code)
        params = {'text': text, 
                 'out' : out, 
                 'err': err, 
                 'q_title': q_title, 
                 'q_sentence': q_sentence, 
                 'q_data': q_data,
                 "pre_code": pre_code, 
                 "pre_visual": pre_visual, 
                "post_code": post_code,
                "post_visual": post_visual, 
                "data1": data1,
                "data2": data2,
                "un": un, "pk": pk,  "ev": ev}
        return render(request, 'question/drill.html', params)
    
    # 同じunit、sectionの問題をクエリセットとして取得し、その中から問題をランダムに選択
    question = Basis.objects.filter(unit = un, section = pk)
    s = random.randint(0, len(question)-1)
    question = question[s]

    # 問題のデータを取得
    q_sentence, role = question.question, question.role_code
    pre_code, post_code = question.pre_code, question.post_code
    pre_visual, post_visual = question.pre_visual, question.post_visual
    # 解答例のインデントが消去されてしまうので、/space/を入力しておいて、インデントに変換
    e_answer = question.e_answer.replace('/space/', '    ')
    i_range, g_range = question.i_range, question.g_range

    # 問題の種類によって（素因数2の数で分類）、異なるランダムアルゴリズムを使用
    if question.category % 2 == 0: # コードで入力
        if question.category % 4 == 0:
            if question.category % 8 == 0:
                g_origin, g_out = g_range.split('\r\n/separate/\r\n')
                g_out = g_out.split('\n')
                g_list = random.sample(eval(g_out[0]), int(g_out[1]))
                if len(g_list) != 0:
                    g_list.append(random.choice(g_list))
                g_list = eval(g_origin) + g_list
            else:
                g_range = g_range.split('\n')
                g_list = [random.choice(eval(x)) for x in g_range]
            for i in range(len(g_list)):
                i_range = i_range.replace(f'/gvc{i}/', str(g_list[i]))
            i_range = i_range.split('\n')
        else:
            i_range = i_range.split('\n')
        d_list = [random.choice(eval(x)) for x in i_range]
        q_data = question.q_data
        # 変数に代入する値が、str変換するものとrepr変換するもので分ける
        to_str = [q_sentence, pre_visual, post_visual, q_data]
        to_repr = [pre_code, post_code, role, e_answer]
        # データベースの変数(radc)にランダムに得られた値を代入
        for i in range(len(d_list)):
            to_str = list(map(lambda x : x.replace(f'/radc{i}/', str(d_list[i])), to_str))
            to_repr = list(map(lambda x : x.replace(f'/radc{i}/', repr(d_list[i])), to_repr))
        q_sentence, pre_visual, post_visual, q_data = to_str
        pre_code, post_code, role, e_answer = to_repr
        # 素因数2が含まれる問題は、解答例を使用して出力を得る
        e_answer = assist.connect(pre_code, e_answer, post_code)
        with open('pythonL/collect.py', 'w') as f:
            f.write(e_answer)
        op = subprocess.run('python pythonL/collect.py', shell=True, capture_output=True, text=True, timeout=3)
        c_output = op.stdout
    else: # 直接入力
        q_data = question.q_data.split('/Qend/\r\n')
        c_output = question.c_output.split('/Qend/\r\n')
        e_answer = e_answer.split('/Qend/\r\n') 
        c = random.randint(0, len(q_data)-1)     
        q_data, c_output, e_answer = q_data[c], c_output[c] + "\n", e_answer[c]
        if pre_code:
            pre_code, pre_visual = pre_code.split('/Qend/\r\n'), pre_visual.split('/Qend/\r\n')
            pre_code, pre_visual = pre_code[c], pre_visual[c]
        if post_code:
            post_code, post_visual = post_code.split('/Qend/\r\n'), post_visual.split('/Qend/\r\n')
            post_code, post_visual = post_code[c], post_visual[c]
    
    # 事前コードの表示テキストをエディターの色と同じになるように色付け
    # エディターの配色選択機能を追加予定のため、こちらも大きく修正予定。
    if question.category % 3 == 0:
        pre_visual = assist.font(pre_visual)
        post_visual = assist.font(post_visual)
        if question.category % 9 == 0:
            pre_visual = assist.font_p(pre_visual)
            post_visual = assist.font_p(post_visual)
        
    # 要求される出力と解答例を暗号化
    private_info = c_output + "///" + e_answer
    cipher = AES.new(key.key, AES.MODE_EAX, nonce=key.nonce)
    ciphertext, tag = cipher.encrypt_and_digest(private_info.encode("utf-8"))

    # 事前コード（赤枠）の(行数−１)を計算 
    ev = pre_visual.count("\n") 

    # データベース管理のための情報を削除
    q_title = question.title.split('/')[0]

    # postメソッドと解答結果ページに送る内容をまとめる
    data1 = str([q_title, q_sentence, pre_visual, post_visual]) # postメソッドのみに送る内容
    data2 = str([q_data, pre_code, post_code, role, ciphertext, tag]) # 両方に送る内容

    params ={'q_title': q_title, 
             'q_sentence': q_sentence, 
             'q_data': q_data, 
             "pre_code": pre_code, 
             "pre_visual": pre_visual, 
             "post_code": post_code, 
             "post_visual": post_visual, 
             "data1": data1, 
             "data2": data2, 
             "un": un, "pk": pk, "ev": ev}
    return render(request, 'question/drill.html', params)


@login_required
def drill_a(request, un, pk):
    # unitおよびsectionの最終番号を取得（前後の問題へのリンクの有無の判定用）
    un_last = Basis.objects.order_by('unit').last().unit
    pk_last = Basis.objects.filter(unit = un).order_by('section').last().section
    # １つ前のunitのsectionの最終番号を取得
    if un >=2:
        pu_last = Basis.objects.filter(unit = un - 1).order_by('section').last().section
    else:
        pu_last = 1
    
    if request.method == 'POST':
        text = request.POST['text'] 
        backup = request.POST['backup'] 
        data2 = request.POST['data2']

        # 問題ページから送られた内容を展開
        q_data, pre_code, post_code, role, ciphertext, tag = eval(data2)
        if text == '':
            text = backup
        text_c = assist.connect(pre_code, text, post_code)
        with open('pythonL/practice.py', 'w') as f:
            f.write(text_c)
        op = subprocess.run('python pythonL/practice.py', shell=True, capture_output=True, text=True, timeout=3)
        drill_a.out = op.stdout

        # 暗号化されていた文字列を復号化
        cipher_dec = AES.new(key.key, AES.MODE_EAX, key.nonce)
        dec_data = cipher_dec.decrypt_and_verify(ciphertext, tag)
        private_info = dec_data.decode()
        c_output = private_info.split("///")[0].replace('\r', '')
        e_answer = private_info.split("///")[1].replace('\r', '')

        # 提出されたコードによる正誤判定
        if drill_a.out == c_output:
            drill_a.collect = True
        else:
            drill_a.collect = False
        
        # 独自の正誤判定を用いる場合
        exec(role)

        # 前後のunitおよびsectionの番号を変数に格納
        nu, pu = un + 1, un - 1
        np, pp = pk + 1, pk - 1

        params = {'text_c': text_c, 
                 'out' : drill_a.out, 
                 'c_output': c_output, 
                 'e_answer': e_answer,
                 "collect": drill_a.collect,
                 "pre_code": pre_code, 
                "post_code": post_code,
                "un_last": un_last, "pk_last": pk_last, "pu_last": pu_last, 
                "un": un, "pk": pk, "nu": nu, "pu": pu, "np": np, "pp": pp}
        return render(request, 'question/drill_a.html', params)
    params ={'c_output': "", 
             'e_answer': "",
             "un_last": un_last, "pk_last": pk_last, "pu_last": pu_last, 
               "un": un, "pk": pk, "nu": nu, "pu": pu, "np": np, "pp": pp}
    return render(request, 'question/drill_a.html', params)
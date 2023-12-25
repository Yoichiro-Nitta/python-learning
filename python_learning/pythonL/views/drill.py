from django.shortcuts import render, redirect
from pythonL.models import CustomUser, IntroCourse, Basis, Quartet, Competition
from django.contrib.auth.decorators import login_required
from application import assist, pllist
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
        q_data, pre_code, post_code, role = eval(data2)
        ev = pre_visual.count("\n") 
        if text == '':
            text = backup

        # 事前に与えられているコードと統合
        text_c = assist.connect(pre_code, text, post_code)

        with open('pythonL/practice.py', 'w') as f:
            f.write(text_c)
        op = subprocess.run('python pythonL/practice.py', shell=True, capture_output=True, text=True, timeout=3)
        out, err = op.stdout, op.stderr
        err = err.split('",')[-1]

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
    e_answer = question.e_answer.replace('/space/', '    ')
    i_range = question.i_range

    # 問題の種類によって（素因数2の数で分類）、異なるランダムアルゴリズムを使用
    if question.category % 2 == 0: # コードで入力
        if question.category % 4 == 0:
            if question.category % 8 == 0:
                c_bbcl, c_out = question.c_output.split('\n/bbcl/')
                c_out, c_mrcl = c_out.split('\n/mrcl/')
                c_out = c_out.split('\n')
                c_list = random.sample(eval(c_out[0]), int(c_out[1]))
                if len(c_list) != 0:
                    c_list.append(random.choice(c_list))
                c_list = eval(c_bbcl) + c_list + eval(c_mrcl)
            else:
                c_range = question.c_output.split('\n')
                c_list = [random.choice(eval(x)) for x in c_range]
            for i in range(len(c_list)):
                i_range = i_range.replace(f'/gvc{i}/', str(c_list[i]))
            i_range = i_range.split('\n')
        else:
            i_range = i_range.split('\n')
        d_list = [random.choice(eval(x)) for x in i_range]
        q_data = question.q_data
        # データベースの変数(radc)にランダムに得られた値を代入
        for i in range(len(d_list)):
            q_sentence = q_sentence.replace(f'/radc{i}/', str(d_list[i]))
            pre_code = pre_code.replace(f'/radc{i}/', repr(d_list[i]))
            pre_visual = pre_visual.replace(f'/radc{i}/', str(d_list[i]))
            post_code = post_code.replace(f'/radc{i}/', repr(d_list[i]))
            post_visual = post_visual.replace(f'/radc{i}/', str(d_list[i]))
            role = role.replace(f'/radc{i}/', repr(d_list[i]))
            q_data = q_data.replace(f'/radc{i}/', str(d_list[i]))
            e_answer = e_answer.replace(f'/radc{i}/', repr(d_list[i]))
        # 素因数2が含まれる問題は、解答例を使用して出力を得る
        e_answer = assist.connect(pre_code, e_answer, post_code)
        with open('pythonL/collect.py', 'w') as f:
            f.write(e_answer)
        op = subprocess.run('python pythonL/collect.py', shell=True, capture_output=True, text=True, timeout=3)
        c_output = op.stdout
    else: # 直接入力
        q_data = question.q_data.split('\n/nct/')
        c_output = question.c_output.split('/nct/')
        e_answer = e_answer.split('\n/nct/') 
        c = random.randint(0, len(q_data)-2)     
        q_data, c_output, e_answer = q_data[c], c_output[c], e_answer[c]
        if pre_code:
            pre_code, pre_visual = pre_code.split('\n/nct/'), pre_visual.split('\n/nct/')
            pre_code, pre_visual = pre_code[c], pre_visual[c]
        if post_code:
            post_code, post_visual = post_code.split('\n/nct/'), post_visual.split('\n/nct/')
            post_code, post_visual = post_code[c], post_visual[c]
    
    # 事前コードの表示テキストをエディターの色と同じになるように色付け
    if question.category % 3 == 0:
        pre_visual = assist.font(pre_visual)
        post_visual = assist.font(post_visual)
        if question.category % 9 == 0:
            pre_visual = assist.font_p(pre_visual)
            post_visual = assist.font_p(post_visual)
    
    # 「求められる出力」と「解答例」をユーザーのデータベースに保存    
    user = request.user
    user.s_output = c_output
    user.s_answer = e_answer
    user.save()

    # 事前コード（赤枠）の(行数−１)を計算 
    ev = pre_visual.count("\n") 

    # データベース管理のための情報を削除
    q_title = question.title.split('/')[0]

    # postメソッドと解答結果ページに送る内容をまとめる
    data1 = str([q_title, q_sentence, pre_visual, post_visual]) # postメソッドのみに送る内容
    data2 = str([q_data, pre_code, post_code, role]) # 両方に送る内容

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
        q_data, pre_code, post_code, role = eval(data2)
        if text == '':
            text = backup
        text_c = assist.connect(pre_code, text, post_code)
        with open('pythonL/practice.py', 'w') as f:
            f.write(text_c)
        op = subprocess.run('python pythonL/practice.py', shell=True, capture_output=True, text=True, timeout=3)
        drill_a.out = op.stdout

        # ユーザーのデータベースに保存されていた「求められる出力」と「解答例」を取得
        user = request.user
        c_output = user.s_output
        e_answer = user.s_answer
        c_output = c_output.replace('\r', '')
        e_answer = e_answer.replace('\r', '')

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
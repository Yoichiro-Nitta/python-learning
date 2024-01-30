from django.shortcuts import render, redirect
from python_learning_app.models.index import CustomUser
from python_learning_app.models.questions import Basis
from django.contrib.auth.decorators import login_required
from Crypto.Cipher import AES
from application import assist, pllist, key
import random
import subprocess

def questions(request):
    # 問題の大区分数を取得
    un_last = Basis.objects.order_by('unit').last().unit

    # 大区分毎のクエリセットをリストに格納
    unit_list = [Basis.objects.filter(unit = i+1, q_key = True).order_by('section') for i in range(un_last)]

    # 大区分名をkey、大区分クエリセットをvalueとして辞書に格納
    units ={}
    for i in range(un_last):
        units[unit_list[i].first().major_h] = unit_list[i]
    
    # 5の倍数毎に２重線を引くために、5の倍数のリストを作成
    multiple5 = [ 5 * x for x in range(1,11) ]
    params = {"units": units, "un_last": un_last, "multiple5": multiple5}

    return render(request, 'drill/questions.html', params)

def practice(request):
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
        params = {'text': text, 'out' : out, 'err': err}

        return render(request, 'drill/practice.html', params)
    
    return render(request, 'drill/practice.html')

def practice_a(request):
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
            collect = True
        else:
            collect = False
        
        params = {
        'text': text, 'out' : out, 'collect': collect}

        return render(request, 'drill/practice_a.html', params)
    
    return render(request, 'drill/practice_a.html')

@login_required
def drill(request, un, pk):
    # エディター色をforloop用にまとめる
    color_text = ["ace/theme/vibrant_ink//vibrant_ink_", 
                  "ace/theme/monokai//monokai_", 
                  "ace/theme/cobalt//cobalt_", 
                  "ace/theme/solarized_light//solarized_light_", 
                  "ace/theme/crimson_editor//crimson_editor_"]
    editor_color = ["Vibrant Ink", "Monokai", "Cobalt", "Solarized Light", "Crimson Editor"]
    editor_colors = zip(color_text, editor_color)

    if request.method == 'POST':
        text = request.POST['text'] 
        backup = request.POST['backup'] 
        defalt_color = request.POST['defalt_color']
        data1 = request.POST['data1']
        data2 = request.POST['data2']

        # defalt_colorを色番号に変換
        color_dict = {"ace/theme/vibrant_ink": 1, 
                      "ace/theme/monokai": 2, 
                      "ace/theme/cobalt": 3, 
                      "ace/theme/solarized_light": 4, 
                      "ace/theme/crimson_editor": 5} 
        cn = color_dict[defalt_color]
        
        # エディター前後の指定入力欄をエディターの色と揃えるためのcssのclass名
        main_class = defalt_color.replace("ace/theme/", "") + "_main"
        side_class = defalt_color.replace("ace/theme/", "") + "_side"

        # まとめられて送られた内容を再び展開
        question_title, question_sentence, pre_visual, post_visual = eval(data1)
        question_data, pre_code, post_code, role, ciphertext, tag = eval(data2)
        ev = pre_visual.count("\n") 
        if text == '':
            text = backup

        # 事前に与えられているコードと統合
        text_connect = assist.connect(pre_code, text, post_code)
        
        # 危険なコードが含まれている場合の変換処理
        text_connect = assist.security(text_connect)

        with open('sheet/practice.py', 'w') as f:
            f.write(text_connect)
        op = subprocess.run('python sheet/practice.py', shell=True, capture_output=True, text=True, timeout=3)
        out, err = op.stdout, op.stderr
        err = err.split('.py",')[-1]

        # エラー表示の際に、エディターの行数が表示されるように工夫
        if len(out) < len(err) and pre_code:
            err = assist.reduce(err, pre_code)
        params = {'text': text, 'out' : out, 'err': err, 
                 'question_title': question_title, 
                 'question_sentence': question_sentence, 
                 'question_data': question_data,
                 "pre_code": pre_code, 
                 "pre_visual": pre_visual, 
                 "post_code": post_code,
                 "post_visual": post_visual, 
                 "data1": data1, "data2": data2,
                 "editor_colors": editor_colors, 
                 "cn": cn, "defalt_color": defalt_color, 
                 "main_class": main_class, "side_class": side_class, 
                 "un": un, "pk": pk,  "ev": ev}
        
        return render(request, 'drill/drill.html', params)
    
    # 同じunit、sectionの問題をクエリセットとして取得し、その中から問題をランダムに選択
    question = Basis.objects.filter(unit = un, section = pk)
    s = random.randint(0, len(question)-1)
    question = question[s]

    # 問題のデータを取得
    question_sentence, role = question.question, question.role_code
    pre_code, post_code = question.pre_code, question.post_code
    pre_visual, post_visual = question.pre_visual, question.post_visual
    # 解答例のインデントが消去されてしまうので、/space/を入力しておいて、インデントに変換
    example_answer = question.e_answer.replace('/space/', '    ')
    initio_range, general_range = question.i_range, question.g_range

    # 問題の種類によって（素因数2の数で分類）、異なるランダムアルゴリズムを使用
    if question.category % 2 == 0: # コードで入力
        if question.category % 4 == 0:
            if question.category % 8 == 0:
                general_origin, general_out = general_range.split('\r\n/separate/\r\n')
                general_out = general_out.split('\n')
                general_list = random.sample(eval(general_out[0]), int(general_out[1]))
                if len(general_list) != 0:
                    general_list.append(random.choice(general_list))
                general_list = eval(general_origin) + general_list
            else:
                general_range = general_range.split('\n')
                general_list = [random.choice(eval(x)) for x in general_range]
            for i in range(len(general_list)):
                initio_range = initio_range.replace(f'/gvc{i}/', str(general_list[i]))
            initio_range = initio_range.split('\n')
        else:
            initio_range = initio_range.split('\n')
        data_list = [random.choice(eval(x)) for x in initio_range]
        question_data = question.q_data
        # 変数に代入する値が、str変換するものとrepr変換するもので分ける
        to_str = [question_sentence, pre_visual, post_visual, question_data]
        to_repr = [pre_code, post_code, role, example_answer]
        # データベースの変数(radc)にランダムに得られた値を代入
        for i in range(len(data_list)):
            to_str = list(map(lambda x : x.replace(f'/radc{i}/', str(data_list[i])), to_str))
            to_repr = list(map(lambda x : x.replace(f'/radc{i}/', repr(data_list[i])), to_repr))
        question_sentence, pre_visual, post_visual, question_data = to_str
        pre_code, post_code, role, example_answer = to_repr
        # 素因数2が含まれる問題は、解答例を使用して出力を得る
        example_answer = assist.connect(pre_code, example_answer, post_code)
        with open('sheet/collect.py', 'w') as f:
            f.write(example_answer)
        op = subprocess.run('python sheet/collect.py', shell=True, capture_output=True, text=True, timeout=3)
        correct_output = op.stdout
    else: # 直接入力
        question_data = question.q_data.split('/Qend/\r\n')
        correct_output = question.c_output.split('/Qend/\r\n')
        example_answer = example_answer.split('/Qend/\r\n') 
        c = random.randint(0, len(question_data)-1)     
        question_data, correct_output, example_answer = question_data[c], correct_output[c] + "\n", example_answer[c]
        if pre_code:
            pre_code, pre_visual = pre_code.split('/Qend/\r\n'), pre_visual.split('/Qend/\r\n')
            pre_code, pre_visual = pre_code[c], pre_visual[c]
        if post_code:
            post_code, post_visual = post_code.split('/Qend/\r\n'), post_visual.split('/Qend/\r\n')
            post_code, post_visual = post_code[c], post_visual[c]
    
    # 事前コードの表示テキストをエディターの色と同じになるように色付け
    if question.category % 3 == 0:
        pre_visual = assist.font(pre_visual)
        post_visual = assist.font(post_visual)
    
    # editor色の初期値
    cn = 1
    defalt_color = "ace/theme/vibrant_ink"
    main_class = "vibrant_ink_main"
    side_class = "vibrant_ink_side"
        
    # 要求される出力と解答例を暗号化
    private_info = correct_output + "///" + example_answer
    cipher = AES.new(key.key, AES.MODE_EAX, nonce=key.nonce)
    ciphertext, tag = cipher.encrypt_and_digest(private_info.encode("utf-8"))

    # 事前コード（赤枠）の(行数−１)を計算 
    ev = pre_visual.count("\n") 

    # データベース管理のための情報を削除
    question_title = question.title.split('/')[0]

    # postメソッドと解答結果ページに送る内容をまとめる
    data1 = str([question_title, question_sentence, pre_visual, post_visual]) # postメソッドのみに送る内容
    data2 = str([question_data, pre_code, post_code, role, ciphertext, tag]) # 両方に送る内容

    params ={'question_title': question_title, 
             'question_sentence': question_sentence, 
             'question_data': question_data, 
             "pre_code": pre_code, 
             "pre_visual": pre_visual, 
             "post_code": post_code, 
             "post_visual": post_visual, 
             "data1": data1, "data2": data2, 
             "editor_colors": editor_colors, 
             "cn": cn, "defalt_color": defalt_color, 
             "main_class": main_class, "side_class": side_class, 
             "un": un, "pk": pk, "ev": ev}
    
    return render(request, 'drill/drill.html', params)


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
        question_data, pre_code, post_code, role, ciphertext, tag = eval(data2)
        if text == '':
            text = backup

        text_connect = assist.connect(pre_code, text, post_code)
        # 危険なコードが含まれている場合の変換処理
        text_connect = assist.security(text_connect)

        with open('sheet/practice.py', 'w') as f:
            f.write(text_connect)
        op = subprocess.run('python sheet/practice.py', shell=True, capture_output=True, text=True, timeout=3)
        drill_a.out = op.stdout

        # 暗号化されていた文字列を復号化
        cipher_dec = AES.new(key.key, AES.MODE_EAX, key.nonce)
        dec_data = cipher_dec.decrypt_and_verify(ciphertext, tag)
        private_info = dec_data.decode()
        correct_output = private_info.split("///")[0].replace('\r', '')
        example_answer = private_info.split("///")[1].replace('\r', '')

        # 提出されたコードによる正誤判定
        if drill_a.out == correct_output:
            drill_a.collect = True
        else:
            drill_a.collect = False
        
        # 独自の正誤判定を用いる場合
        exec(role)

        # 前後のunitおよびsectionの番号を変数に格納
        nu, pu = un + 1, un - 1
        np, pp = pk + 1, pk - 1

        params = {'text_connect': text_connect, 
                 'out' : drill_a.out, 
                 'correct_output': correct_output, 
                 'example_answer': example_answer,
                 "collect": drill_a.collect,
                 "pre_code": pre_code, 
                 "post_code": post_code,
                 "un_last": un_last, "pk_last": pk_last, "pu_last": pu_last, 
                 "un": un, "pk": pk, "nu": nu, "pu": pu, "np": np, "pp": pp}
        
        return render(request, 'drill/drill_a.html', params)
    
    params ={'correct_output': "", 
             'example_answer': "",
             "un_last": un_last, "pk_last": pk_last, "pu_last": pu_last, 
             "un": un, "pk": pk, "nu": nu, "pu": pu, "np": np, "pp": pp}
    
    return render(request, 'drill/drill_a.html', params)
from django.shortcuts import render, redirect
from pythonL.models import CustomUser, IntroCourse, Basis, Quartet, Competition
from django.contrib.auth.decorators import login_required
from Crypto.Cipher import AES
from application import key
import time
import random
import subprocess


@login_required
def compe(request, pk):
    #データベースからデータを取得
    question = Competition.objects.get(section = pk)
    title, sentence = question.title, question.question,
    expectation, condition = question.expectation, question.condition
    format_data, format_text = question.input_format.split("\r\n/separate/\r\n")
    
    #入力データ、出力データは取得後分割しリストに変換
    input_ex_list = question.input_ex.replace("\r", "").split("\n/separate/\n")
    output_ex_list = question.output_ex.replace("\r", "").split("\n/separate/\n")
    examples = zip(input_ex_list, output_ex_list)

    # エディター色とテストケースをforloop用にまとめる
    color_text = ["ace/theme/vibrant_ink", 
                  "ace/theme/monokai", 
                  "ace/theme/cobalt", 
                  "ace/theme/solarized_light", 
                  "ace/theme/crimson_editor"]
    editor_color = ["Vibrant Ink", "Monokai", "Cobalt", "Solarized Light","Crimson Editor"]
    editor_colors = zip(color_text, editor_color)
    testcases = [input_ex_list[i] + "//" + output_ex_list[i] + "//" + str(i + 1) for i in range(len(input_ex_list))]

    if request.method == 'POST':
        text = request.POST['text'] 
        backup = request.POST['backup'] 
        defalt_color = request.POST['defalt_color']
        data = request.POST['data'] 
        color_dict = {"ace/theme/vibrant_ink": 1, 
                      "ace/theme/monokai": 2, 
                      "ace/theme/cobalt": 3, 
                      "ace/theme/solarized_light": 4, 
                      "ace/theme/crimson_editor": 5} 
        cn = color_dict[defalt_color]
        # post時に選択されていたselectタグの値をint型で取得
        sn = int(request.POST['selected_n'] )
        n_input = input_ex_list[sn - 1] + "\n"
        if text == '':
            text = backup
        with open('pythonL/competition.py', 'w') as f:
                f.write(text)
        # selectタグの値によって入力値を自動で選択されるように工夫
        op = subprocess.run('python pythonL/competition.py',input=n_input, shell=True, capture_output=True, text=True, timeout=3)
        out, err = op.stdout, op.stderr
        err = err.split('",')[-1]
        params = {'text': text, 'out' : out, 'err': err, 
                  "title":title,"sentence": sentence, 
                "expectation": expectation, "condition": condition, 
                "format_data": format_data, "format_text": format_text, 
                "input_ex": input_ex_list[sn - 1], "output_ex": output_ex_list[sn - 1], 
                "examples": examples, "editor_colors": editor_colors, "testcases": testcases, 
                 "defalt_color": defalt_color, "data": data, "cn": cn, "sn": sn, "pk": pk}
        return render(request, 'question/compe.html', params)
    
    # editor色の初期値
    cn = 1
    # selectタグの初期値
    sn = 1

    defalt_color = "ace/theme/vibrant_ink"

    private_info = question.input_data + "///" + question.output_data + "///" + question.e_answer
    cipher = AES.new(key.key, AES.MODE_EAX, nonce=key.nonce)
    ciphertext, tag = cipher.encrypt_and_digest(private_info.encode("utf-8"))

    data = str([ciphertext, tag])

    params = {"title":title,"sentence": sentence, 
              "expectation": expectation, "condition": condition, 
              "format_data": format_data, "format_text": format_text, 
              "input_ex": input_ex_list[0], "output_ex": output_ex_list[0], 
              "examples": examples, "editor_colors": editor_colors, "testcases": testcases, 
              "defalt_color": defalt_color, "data": data, 
              "cn": cn, "sn": sn, "pk": pk}
    return render(request, 'question/compe.html', params)


@login_required
def compe_a(request, pk):
    #非公開の入力データ、出力データを再取得
    question = Competition.objects.get(section = pk)
    input_ex_list = question.input_ex.replace("\r", "").split("\n/separate/\n")
    output_ex_list = question.output_ex.replace("\r", "").split("\n/separate/\n")

    if request.method == 'POST':
        text = request.POST['text'] 
        backup = request.POST['backup'] 
        data = request.POST['data'] 
        ciphertext, tag = eval(data)
        if text == '':
            text = backup

        # 暗号化されていた情報を複合化        
        cipher_dec = AES.new(key.key, AES.MODE_EAX, key.nonce)
        dec_data = cipher_dec.decrypt_and_verify(ciphertext, tag)
        private_info = dec_data.decode()
        c_input = private_info.split("///")[0].replace('\r', '').split("\n/separate/\n")
        c_output = private_info.split("///")[1].replace('\r', '').split("\n/separate/\n")
        e_answer = private_info.split("///")[2].replace('\r', '')

        # 表示、非表示で分かれていた「入力値」「正解出力値」を統一
        q_input = input_ex_list + c_input
        q_output = output_ex_list + c_output
        q_input = list(map(lambda x : x + "\n", q_input))
        q_output = list(map(lambda x : x + "\n", q_output))
        # ユーザーの出力格納用リストを用意
        u_answer = []
        #　処理時間格納用リストを用意
        processing_time = []

        with open('pythonL/competition.py', 'w') as f:
            f.write(text)
        
        # 処理時間を計測しながらそれぞれの標準入力に対する処理を実行
        for i in range(len(q_input)):
            start = time.time()
            op = subprocess.run('python pythonL/competition.py',input= q_input[i], shell=True, capture_output=True, text=True, timeout=3)
            end = time.time()
            u_answer.append(op.stdout)
            time_diff = end - start
            processing_time.append(round(time_diff, 2))
        
        check = [] # テストケース毎の正誤を格納するリスト
        fade_in = [] # フェードイン用のcssクラスを格納するリスト
        for i in range(len(q_input)):
            check.append(u_answer[i] == q_output[i])
            fade_in.append(f'fadeIn_{i+1}')

        # for文でまわすためにzipオブジェクトを作成
        combine = zip(check, processing_time, fade_in)
        params = {"combine": combine, "text": text, "e_answer": e_answer }
        return render(request, 'question/compe_a.html', params)
    return render(request, 'question/compe_a.html')
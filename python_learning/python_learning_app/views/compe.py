from django.shortcuts import render, redirect
from python_learning_app.models.index import CustomUser
from python_learning_app.models.questions import Competition, CompeResult
from django.contrib.auth.decorators import login_required
from Crypto.Cipher import AES
from application import key
from django.core.paginator import Paginator
import time
import subprocess

def p_like(request):
    # 例題（問題番号０）以外の問題を取得
    questions = Competition.objects.filter(section__gte = '1').order_by('section')
    # ページの分割
    paginator = Paginator(questions, 10)
    # クエリパラメーターからページ番号取得
    number = int(request.GET.get('p', 1))
    # 取得したページ番号のページを取得
    page_obj = paginator.page(number)

    # 難易度とユーザーの挑戦履歴を取得
    level = [] # 難易度格納用リスト
    results = [] # 挑戦履歴格納用リスト
    for question in page_obj:
        level.append(question.level * '★')
        try:
            result = CompeResult.objects.get(user_id = request.user.id, connection_key = question)
            results.append(result.result)
        except:
            results.append(None)
    
    # forloop用にまとめる
    questions_and_results = zip(level, page_obj, results)

    params = {'page_obj' : page_obj, 'questions_and_results': questions_and_results}

    return render(request, 'compe/p_like.html', params)

def p_like_ex(request):
    return render(request, 'compe/p_like_ex.html')

@login_required
def compe(request, pk):
    # データベースからデータを取得
    question = Competition.objects.get(section = pk)
    title, sentence = question.title, question.question,
    expectation, condition = question.expectation, question.condition
    format_data, format_text = question.input_format.split("\r\n/separate/\r\n")
    
    # 入力データ、出力データは取得後分割しリストに変換
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
        with open('sheet/competition.py', 'w') as f:
                f.write(text)
        # selectタグの値によって入力値を自動で選択されるように工夫
        op = subprocess.run('python sheet/competition.py',input=n_input, shell=True, capture_output=True, text=True, timeout=3)
        out, err = op.stdout, op.stderr
        err = err.split('",')[-1]
        params = {'text': text, 'out' : out, 'err': err, 
                  "title":title,"sentence": sentence, 
                  "expectation": expectation, "condition": condition, 
                  "format_data": format_data, "format_text": format_text, 
                  "input_ex": input_ex_list[sn - 1], "output_ex": output_ex_list[sn - 1], 
                  "examples": examples, "editor_colors": editor_colors, "testcases": testcases, 
                  "defalt_color": defalt_color, "data": data, "cn": cn, "sn": sn, "pk": pk}
        
        return render(request, 'compe/compe.html', params)
    
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
    
    return render(request, 'compe/compe.html', params)


@login_required
def compe_a(request, pk):
    # 非公開の入力データ、出力データを再取得
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
        extra_input = private_info.split("///")[0].replace('\r', '').split("\n/separate/\n")
        extra_output = private_info.split("///")[1].replace('\r', '').split("\n/separate/\n")
        example_answer = private_info.split("///")[2].replace('\r', '')

        # 表示、非表示で分かれていた「入力値」「正解出力値」を統一
        question_input = input_ex_list + extra_input
        question_output = output_ex_list + extra_output
        question_input = list(map(lambda x : x + "\n", question_input))
        question_output = list(map(lambda x : x + "\n", question_output))
        # ユーザーの出力格納用リストを用意
        user_answer = []
        # 処理時間格納用リストを用意
        processing_time = []

        with open('sheet/competition.py', 'w') as f:
            f.write(text)
        
        # 処理時間を計測しながらそれぞれの標準入力に対する処理を実行
        for i in range(len(question_input)):
            start = time.time()
            op = subprocess.run('python sheet/competition.py',input= question_input[i], shell=True, capture_output=True, text=True, timeout=3)
            end = time.time()
            user_answer.append(op.stdout)
            time_diff = end - start
            processing_time.append(round(time_diff, 2))
        
        num_of_question = len(question_input) # 問題数
        check = [] # テストケース毎の正誤を格納するリスト
        fade_in = [] # フェードイン用のcssクラスを格納するリスト
        for i in range(num_of_question):
            check.append(user_answer[i] == question_output[i])
            fade_in.append(f'fadeIn_{i+1}')
        
        num_of_correct = sum(check) # 正答数
        last_fade_in = f'fadeIn_{num_of_question + 1}'

        perfect = ""
        # ユーザーの挑戦履歴を記録
        try:
            compe_result = CompeResult.objects.get(user_id = request.user.id, connection_key = question)
        except:
            compe_result = CompeResult()
            compe_result.user_id = request.user.id
        if compe_result.result:
            pass
        elif not False in check:
            compe_result.result = True
            perfect = "perfect達成!"
        else:
            compe_result.result = False
        compe_result.connection_key = question
        compe_result.save()

        pn = (pk - 1) // 10 + 1

        # for文でまわすためにzipオブジェクトを作成
        combine = zip(check, processing_time, fade_in)
        params = {"combine": combine, "text": text, "example_answer": example_answer, 
                  "num_of_question": num_of_question, "num_of_correct": num_of_correct, 
                  "last_fade_in": last_fade_in, "perfect": perfect, "pn": pn }

        return render(request, 'compe/compe_a.html', params)
    
    return render(request, 'compe/compe_a.html')
from django.shortcuts import render
from python_learning_app.models.questions import Competition, CompeResult
from django.contrib.auth.decorators import login_required
from Crypto.Cipher import AES
from application import key, assist
from django.core.paginator import Paginator
import time
import subprocess

def p_like(request):
    """Paiza形式問題一覧のView
    
    パラメーター説明

    page_obj:               Paginatorのオブジェクト
    page_range:             ページ番号のリスト（ページのリンクボタンで使用）
    number:                 クエリパラメータから取得した現在のページ番号
    questions_and_results:  問題レベル、page_obj、解答履歴をまとめたイテラブルオブジェクト

    """

    # 例題（問題番号０）以外の問題を取得
    questions = Competition.objects.filter(section__gte = '1').order_by('section')
    # ページの分割
    paginator = Paginator(questions, 10)
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

    # 難易度とユーザーの挑戦履歴を取得
    level = [] # 難易度格納用リスト
    results = [] # 挑戦履歴格納用リスト
    for question in page_obj:
        level.append(question.level * '★')
        if CompeResult.objects.filter(user_id = request.user.id, connection_key = question.primary_key).exists():
            result = CompeResult.objects.get(user_id = request.user.id, connection_key = question.primary_key)
            results.append(result.result)
        else:
            results.append(None)
    
    # forloop用にまとめる
    questions_and_results = zip(level, page_obj, results)

    params = {'page_obj' : page_obj, 'page_range': page_range, 
              'number': number, 'questions_and_results': questions_and_results}

    return render(request, 'compe/p_like.html', params)

def p_like_ex(request):
    """Paiza形式問題の説明ページのView
    
    パラメーター説明

    pn:               ページ番号

    """

    # クエリ情報の取得
    query = request.GET.get('p')

    # 問題一覧に戻るページ数を設定
    if query in ['1', None]:
        pn = 1
    else:
        pn = int(query)

    return render(request, 'compe/p_like_ex.html', {"pn": pn})

@login_required
def compe(request, pk):
    """Paiza形式問題ページのView
    
    パラメーター説明

    text:                   ユーザーの入力内容
    out:                    出力結果(出力時)
    err:                    出力結果(エラー時)
    title:                  問題のタイトル
    sentence:               問題文
    expectation:            期待される出力
    condition:              問題の条件
    format_data:            入力フォーマットのデータ部
    format_text:            入力フォーマットの説明部
    input_ex:               入力例の初期値(postメソッド時はpost時の値)
    output_ex:              出力例の初期値(postメソッド時はpost時の値)
    examples:               入力例と出力例をまとめたイテラブルオブジェクト
    editor_colors:          エディター配色のリスト
    testcases:              テストケース表示用リスト（javascriptに渡すためのデータ）
    default_color:          エディターの初期配色
    data:                   暗号化データ
    cn:                     カラー番号
    sn:                     セレクトタグの番号
    pk:                     問題番号
    pn:                     リンク元のページ番号

    """

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

    # エディター色と番号の辞書を作成
    color_numbers = [1, 2, 3, 4, 5]
    color_dict = dict(zip(color_text, color_numbers))

    # 練習問題（問題番号0）および各ページの問題から問題一覧ページに戻る際は元のページに戻るように設定
    if pk == 0:
        pn = request.GET.get('p')
    else:
        pn = (pk - 1) // 10 + 1
    

    if request.method == 'POST':
        text = request.POST['text'] 
        backup = request.POST['backup'] 
        default_color = request.POST['default_color']
        data = request.POST['data'] 
        cn = color_dict[default_color]
        # post時に選択されていたselectタグの値をint型で取得
        sn = int(request.POST['selected_n'] )
        n_input = input_ex_list[sn - 1] + "\n"
        if text == '':
            text = backup
        
        # 危険なコードが含まれている場合の変換処理
        text = assist.security(text)

        with open('sheet/competition.py', 'w') as f:
                f.write(text)
        # selectタグの値によって入力値を自動で選択されるように工夫
        op = subprocess.run('python sheet/competition.py',input=n_input, shell=True, capture_output=True, text=True, timeout=3)
        out, err = op.stdout, op.stderr
        err = err.split('",')[-1]
        params = {"text": text, "out" : out, "err": err, 
                  "title":title,"sentence": sentence, 
                  "expectation": expectation, "condition": condition, 
                  "format_data": format_data, "format_text": format_text, 
                  "input_ex": input_ex_list[sn - 1], "output_ex": output_ex_list[sn - 1], 
                  "examples": examples, "editor_colors": editor_colors, "testcases": testcases, 
                  "default_color": default_color, "data": data, "cn": cn, "sn": sn, "pk": pk, "pn": pn}
        
        return render(request, 'compe/compe.html', params)
    
    # editor色の初期値
    e_query = request.GET.get('e')
    if e_query:
        default_color = "ace/theme/" + e_query
        cn = color_dict[default_color]
    else:
        default_color = "ace/theme/vibrant_ink"
        cn = 1
    # selectタグの初期値
    sn = 1
    

    private_info = question.input_data + "///" + question.output_data + "///" + question.e_answer
    cipher = AES.new(key.key, AES.MODE_EAX, nonce=key.nonce)
    ciphertext, tag = cipher.encrypt_and_digest(private_info.encode("utf-8"))

    data = str([ciphertext, tag])

    params = {"title":title,"sentence": sentence, 
              "expectation": expectation, "condition": condition, 
              "format_data": format_data, "format_text": format_text, 
              "input_ex": input_ex_list[0], "output_ex": output_ex_list[0], 
              "examples": examples, "editor_colors": editor_colors, "testcases": testcases, 
              "default_color": default_color, "data": data, 
              "cn": cn, "sn": sn, "pk": pk, "pn": pn}
    
    return render(request, 'compe/compe.html', params)


@login_required
def compe_a(request, pk):
    """Paiza形式解答結果ページのView
    
    パラメーター説明

    combine:                解答の正誤、実行時間、フェードインのcssクラスをまとめたイテラブルオブジェクト
    text:                   ユーザーの入力内容
    default_color:          エディター色の初期値
    example_answer:         解答例
    num_of_question:        テストケース数
    num_of_correct:         正解ケース数
    last_fade_in:           正解ケース数/テストケース数をフェードインで表示するcssクラス
    perfect:                perfect達成の判定
    e_query:                クエリ文字列で渡すエディター色
    pk:                     問題番号
    pn:                     リンク元のページ番号

    """

    # 非公開の入力データ、出力データを再取得
    question = Competition.objects.get(section = pk)
    input_ex_list = question.input_ex.replace("\r", "").split("\n/separate/\n")
    output_ex_list = question.output_ex.replace("\r", "").split("\n/separate/\n")

    if request.method == 'POST':
        text = request.POST['text'] 
        default_color = request.POST['default_color']
        backup = request.POST['backup'] 
        data = request.POST['data'] 
        ciphertext, tag = eval(data)
        if text == '':
            text = backup
        
        # 危険なコードが含まれている場合の変換処理
        text = assist.security(text)

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
        
        if pk == 0:
            pn = request.GET.get('p')
        else:
            # ユーザーの挑戦履歴を記録
            compe_result, created = CompeResult.objects.get_or_create(user_id = request.user.id, connection_key = question)
        
            if compe_result.result:
                pass
            elif not False in check:
                compe_result.result = True
                perfect = "perfect達成!"
            else:
                compe_result.result = False
                
            compe_result.save()
            pn = (pk - 1) // 10 + 1

        # クエリ文字列で渡すエディター配色
        e_query = default_color.split("/")[-1]

        # for文でまわすためにzipオブジェクトを作成
        combine = zip(check, processing_time, fade_in)
        params = {"combine": combine, "text": text, "example_answer": example_answer, 
                  "default_color": default_color,"num_of_question": num_of_question,
                  "num_of_correct": num_of_correct, "last_fade_in": last_fade_in, 
                  "perfect": perfect, "e_query": e_query, "pn": pn, "pk": pk }

        return render(request, 'compe/compe_a.html', params)
    
    return render(request, 'compe/compe_a.html')
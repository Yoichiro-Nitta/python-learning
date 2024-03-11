from django.shortcuts import render
from django.views.generic import View
from Crypto.Cipher import AES
from application import assist, pllist, key
import random
import subprocess


class QuestionsListView(View):

    """Python基本問題一覧ページのViewのスーパークラス
    
    パラメーター説明

    units:                  {'大区分名': 大区分クエリセット}の辞書型オブジェクト
    un_last:                問題の大区分数
    multiple5:              5の倍数のリスト（問題大区分5の倍数でが2重線で区切るため）
    model_num:              使用するモデルのリストの番号（リストは drll.py の questions_list_urls）
    
    """

    def get(self, request):

        questions, model_num = self.__class__.model

        # 問題の大区分数を取得
        un_last =  questions.objects.order_by('unit').last().unit

        # 大区分毎のクエリセットをリストに格納
        unit_list = [questions.objects.filter(unit = i+1, q_key = True).order_by('section') for i in range(un_last)]

        # 大区分名をkey、大区分クエリセットをvalueとして辞書に格納
        units = {}
        for i in range(un_last):
            units[unit_list[i].first().major_h] = unit_list[i]

        # 5の倍数毎に２重線を引くために、5の倍数のリストを作成
        multiple5 = [ 5 * x for x in range(1,11) ]

        params = {"units": units, "un_last": un_last, "multiple5": multiple5, "model_num": model_num}

        return render(request, 'drill/questions.html', params)


class DrillView(View):

    """Python基本問題解答入力ページのViewのスーパークラス
    
    パラメーター説明

    text:                   ユーザーの入力内容
    out:                    出力結果(出力時)
    err:                    出力結果(エラー時)
    question_title:         問題タイトル
    question_sentence:      問題文
    question_data:          問題データ
    pre_code:               入力欄前の強制入力コード
    pre_visual:             pre_codeの表示内容
    post_code:              入力欄後の強制入力コード 
    post_visual:            post_codeの表示内容
    data1:                  自身のpostメソッドのみに送る内容のまとめ
    data2:                  自身のpostメソッドおよび解答ページに送る内容のまとめ
    editor_colors:          エディター色のリスト
    cn:                     エディター色のカラー番号
    default_color:          エディター色の初期値
    main_class:             強制入力欄のCSSクラス
    side_class:             強制入力部の行番号表示欄のCSSクラス 
    urls:                   問題区分の辞書型変数；{un: 大区分, pk: 小区分}
    ev:                     pre_codeの行数-1
    course_exist:           対応する講座の有無
    question_index_url:     問題一覧ページのURL(templateでurls.pyのnameを指定)
    question_url:           問題ページのURL(templateでurls.pyのnameを指定)
    answer_url:             解答ページのURL(templateでurls.pyのnameを指定)

    """

    # 共有変数を定義
    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        # エディター色をforloop用にまとめる
        color_text = ["ace/theme/vibrant_ink//vibrant_ink_", 
                      "ace/theme/monokai//monokai_", 
                      "ace/theme/cobalt//cobalt_", 
                      "ace/theme/solarized_light//solarized_light_", 
                      "ace/theme/crimson_editor//crimson_editor_"]
        editor_color = ["Vibrant Ink", "Monokai", "Cobalt", "Solarized Light", "Crimson Editor"]
        self.editor_colors = zip(color_text, editor_color)
        self.color_dict = {"ace/theme/vibrant_ink": 1, 
                           "ace/theme/monokai": 2, 
                           "ace/theme/cobalt": 3, 
                           "ace/theme/solarized_light": 4, 
                           "ace/theme/crimson_editor": 5} 
        self.question_index_url = 'python_learning:' + self.__class__.index_url_name
        self.question_url = 'python_learning:' + self.__class__.url_name
        self.answer_url = 'python_learning:' + self.__class__.url_name + '_answer'
        self.course = self.__class__.course
        # 講座と対応している場合、その講座の有無を取得
        if self.course:
            self.course_exist = self.course.objects.filter(section = kwargs['un']).exists()
        else:
            self.course_exist = None

    
    # getメソッドの動的変数のデフォルト値
    def get_func(self, **kwargs):
        return {}
    # postメソッドの動的変数のデフォルト値
    def post_func(self, **kwargs):
        return {}
    
    # 問題選択関数
    def choose_question(self, **kwargs):
        # 同じunit、sectionの問題をクエリセットとして取得し、その中から問題をランダムに選択
        question = self.__class__.model.objects.filter(unit = kwargs['un'], section = kwargs['pk'])
        s = random.randint(0, len(question)-1)
        question = question[s]
        return question, kwargs
    

    def get(self, request, *args, **kwargs):

        question, urls = self.choose_question(**kwargs)
            
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
            with open('sheet/correct.py', 'w') as f:
                f.write(example_answer)
            op = subprocess.run('python sheet/correct.py', shell=True, capture_output=True, text=True, timeout=3)
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
        e_query = self.request.GET.get('e')
        if e_query:
            default_color = "ace/theme/" + e_query
            cn = self.color_dict[default_color]
            main_class = e_query + "_main"
            side_class = e_query + "_side"
        else:
            default_color = "ace/theme/vibrant_ink"
            cn = 1
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

        params ={"question_title": question_title, 
                 "question_sentence": question_sentence, 
                 "question_data": question_data, 
                 "pre_code": pre_code, 
                 "pre_visual": pre_visual, 
                 "post_code": post_code, 
                 "post_visual": post_visual, 
                 "data1": data1, "data2": data2, 
                 "editor_colors": self.editor_colors, 
                 "cn": cn, "default_color": default_color, 
                 "main_class": main_class, "side_class": side_class, 
                 "urls": urls, "ev": ev, 
                 "course_exist": self.course_exist,
                 "question_index_url": self.question_index_url,
                 "question_url": self.question_url, 
                 "answer_url": self.answer_url}
        
        params = {**params, **self.get_func(**kwargs)}
    
        return render(request, self.__class__.template_name, params)
    
    def post(self, request, *args, **kwargs):
        urls = kwargs

        text = request.POST['text'] 
        backup = request.POST['backup'] 
        default_color = request.POST['default_color']
        data1 = request.POST['data1']
        data2 = request.POST['data2']

        # default_colorを色番号に変換
        cn = self.color_dict[default_color]
        
        # エディター前後の指定入力欄をエディターの色と揃えるためのcssのclass名
        main_class = default_color.replace("ace/theme/", "") + "_main"
        side_class = default_color.replace("ace/theme/", "") + "_side"

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
            
        params = {"text": text, "out" : out, "err": err, 
                 "question_title": question_title, 
                 "question_sentence": question_sentence, 
                 "question_data": question_data,
                 "pre_code": pre_code, 
                 "pre_visual": pre_visual, 
                 "post_code": post_code,
                 "post_visual": post_visual, 
                 "data1": data1, "data2": data2,
                 "editor_colors": self.editor_colors, 
                 "cn": cn, "default_color": default_color, 
                 "main_class": main_class, "side_class": side_class, 
                 "urls": urls,  "ev": ev,
                 "course_exist": self.course_exist, 
                 "question_index_url": self.question_index_url, 
                 "question_url": self.question_url, 
                 "answer_url": self.answer_url}
        
        params = {**params, **self.post_func(**kwargs)}
        
        return render(request, self.__class__.template_name, params)
    


class DrillAnswerView(View):

    """Python基本問題解答結果ページのViewのスーパークラス
    
    パラメーター説明
    
    text_connect:           ユーザー入力（＋強制入力）
    out:                    ユーザー出力
    correct_output:         正解出力
    example_answer:         解答例
    correct:                正解のbool値
    urls:                   問題区分の辞書型変数；{un: 大区分, pk: 小区分}
    pages:                  ページ関連の辞書型データ
    default_color:          エディター色の初期値
    e_query:                クエリ文字列で渡すエディター色
    question_index_url:     問題一覧ページのURL(templateでurls.pyのnameを指定)
    question_url:           問題ページのURL(templateでurls.pyのnameを指定)
    answer_url:             解答ページのURL(templateでurls.pyのnameを指定)

    """

    # 共有変数を定義
    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.question_index_url = 'python_learning:' + self.__class__.index_url_name
        self.question_url = 'python_learning:' + self.__class__.url_name
        self.answer_url = 'python_learning:' + self.__class__.url_name + '_answer'
    
    # getメソッドの動的変数のデフォルト値
    def get_func(self, **kwargs):
        return {}
    # postメソッドの動的変数のデフォルト値
    def post_func(self, **kwargs):
        return {}
        
    def pages(self, **kwargs):
        un = kwargs['un']
        pk = kwargs['pk']
        # unitおよびsectionの最終番号を取得（前後の問題へのリンクの有無の判定用）
        un_last = self.__class__.model.objects.order_by('unit').last().unit
        pk_last = self.__class__.model.objects.filter(unit = un).order_by('section').last().section
        # １つ前のunitのsectionの最終番号を取得
        if un >=2:
            pu_last = self.__class__.model.objects.filter(unit = un - 1).order_by('section').last().section
        else:
            pu_last = 1
        next_un, pre_un = un + 1, un - 1
        next_pk, pre_pk = pk + 1, pk - 1
        pages = {'un_last': un_last, 'pk_last': pk_last, 'pu_last': pu_last, 
                 'next_un': next_un, 'pre_un': pre_un, 'next_pk': next_pk, 'pre_pk': pre_pk}
        return pages
    
    def outcome(self, correct, urls):
        return correct, urls
    
    def post(self, request, *args, **kwargs):
        urls = kwargs
        text = request.POST['text'] 
        default_color = request.POST['default_color']
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
        out = op.stdout

        # 暗号化されていた文字列を復号化
        cipher_dec = AES.new(key.key, AES.MODE_EAX, key.nonce)
        dec_data = cipher_dec.decrypt_and_verify(ciphertext, tag)
        private_info = dec_data.decode()
        correct_output = private_info.split("///")[0].replace('\r', '')
        example_answer = private_info.split("///")[1].replace('\r', '')

        # 提出されたコードによる正誤判定
        if out == correct_output:
            correct = True
        else:
            correct = False
        
        # 独自の正誤判定を用いる場合
        if role and out:
            local_val = {'out': out, 'correct': correct, 'correct_output': correct_output}
            exec(role, globals(), local_val)
            correct = local_val['correct']
        
        correct, urls = self.outcome(correct, urls)

        # 前後のunitおよびsectionの番号を変数に格納
        pages = self.pages(**kwargs)

        # クエリ文字列で渡すエディター配色
        e_query = default_color.split("/")[-1]

        params = {"text_connect": text_connect, 
                 "out" : out, 
                 "correct_output": correct_output, 
                 "example_answer": example_answer,
                 "correct": correct,
                 "urls": urls, "pages": pages,
                 "default_color": default_color, "e_query" : e_query, 
                 "question_index_url": self.question_index_url, 
                 "question_url": self.question_url, 
                 "answer_url": self.answer_url}
        
        params = {**params, **self.get_func(**kwargs)}
        
        return render(request, self.__class__.template_name, params)
    
    def get(self, request, *args, **kwargs):
        urls = kwargs
        pages = self.pages(**kwargs)

        params ={"correct_output": "", 
                 "example_answer": "",
                 "urls": urls, "pages": pages, 
                 "default_color": "ace/theme/vibrant_ink", 
                 "question_index_url": self.question_index_url, 
                 "question_url": self.question_url, 
                 "answer_url": self.answer_url}
        
        params = {**params, **self.get_func(**kwargs)}
        
        return render(request, self.__class__.template_name, params)
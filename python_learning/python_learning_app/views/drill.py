from django.shortcuts import render, redirect
from django.views.generic import View
from python_learning_app.models.questions import Basis
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from Crypto.Cipher import AES
from application import assist, pllist, key
import numpy as np
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
            correct = True
        else:
            correct = False
        
        params = {
        'text': text, 'out' : out, 'correct': correct}

        return render(request, 'drill/practice_a.html', params)
    
    return render(request, 'drill/practice_a.html')


# ーーーーーーーーーーーー↓ここから問題ページのView↓ーーーーーーーーーーーー

class DrillView(View):

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
        self.question_url = 'python_learning:' + self.__class__.url_name
        self.answer_url = 'python_learning:' + self.__class__.url_name + '_answer'

    
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

        params ={"question_title": question_title, 
                 "question_sentence": question_sentence, 
                 "question_data": question_data, 
                 "pre_code": pre_code, 
                 "pre_visual": pre_visual, 
                 "post_code": post_code, 
                 "post_visual": post_visual, 
                 "data1": data1, "data2": data2, 
                 "editor_colors": self.editor_colors, 
                 "cn": cn, "defalt_color": defalt_color, 
                 "main_class": main_class, "side_class": side_class, 
                 "urls": urls, "ev": ev, 
                 "question_url": self.question_url, 
                 "answer_url": self.answer_url}
        
        params = {**params, **self.get_func(**kwargs)}
    
        return render(request, self.__class__.template_name, params)
    
    def post(self, request, *args, **kwargs):
        urls = kwargs

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
                 "cn": cn, "defalt_color": defalt_color, 
                 "main_class": main_class, "side_class": side_class, 
                 "urls": urls,  "ev": ev,
                 "question_url": self.question_url, 
                 "answer_url": self.answer_url}
        
        params = {**params, **self.post_func(**kwargs)}
        
        return render(request, self.__class__.template_name, params)


class DrillBeginner(LoginRequiredMixin, DrillView):
    model = Basis
    template_name = 'drill/drill_question.html'
    url_name = 'drill_beginner'


class DrillBeginnerSeries(LoginRequiredMixin, DrillView):
    model = Basis
    template_name = 'drill/drill_questions.html'
    url_name = 'drill_beginners'

    def choose_question(self, **kwargs):
        qn = kwargs['qn']
        question = self.__class__.model.objects.all()
        if qn == 1: # 全問題からランダムで取得
            all_questions = [x for x in range(len(question))]
            # 問題をランダムで１０個選び、最初のインデックスに正解数を付与
            choosed_questions = random.sample(all_questions, 10)
            choosed_questions.insert(0,0)
            s = choosed_questions[qn]
            question = question[s]
            # クエリを生成
            query_list = list(map(lambda x : np.base_repr(x, 32), choosed_questions))
            query = 'X'.join(query_list)
        else: # クエリ情報から取得
            query = self.request.GET.get('query')
            query_list = query.split('X')
            query_list = list(map(lambda x : int(x, 32), query_list))
            s = query_list[qn]
            question = question[s]
        
        add_dict = {'query': query}
        urls = {**kwargs, **add_dict} 

        return question, urls
    
    def post_func(self, **kwargs):
        qn = kwargs['qn']
        query = self.request.GET.get('query')
        return {'urls': {'query': query, 'qn': qn}}


# ーーーーーーーーーーーー↓ここから解答ページのView↓ーーーーーーーーーーーー

class DrillAnswerView(View):

    # 共有変数を定義
    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
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
            local_val = {'out': out, 'correct': correct}
            exec(role, globals(), local_val)
            correct = local_val['correct']
        
        correct, urls = self.outcome(correct, urls)

        # 前後のunitおよびsectionの番号を変数に格納
        pages = self.pages(**kwargs)

        params = {"text_connect": text_connect, 
                 "out" : out, 
                 "correct_output": correct_output, 
                 "example_answer": example_answer,
                 "correct": correct,
                 "pre_code": pre_code, 
                 "post_code": post_code,
                 "urls": urls, "pages": pages,
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
                 "question_url": self.question_url, 
                 "answer_url": self.answer_url}
        
        params = {**params, **self.get_func(**kwargs)}
        
        return render(request, self.__class__.template_name, params)


class DrillBeginnerAnswer(LoginRequiredMixin, DrillAnswerView):
    model = Basis
    template_name = 'drill/drill_answer.html'
    url_name = 'drill_beginner'
        


class DrillBeginnerSeriesAnswer(LoginRequiredMixin, DrillAnswerView):
    model = Basis
    template_name = 'drill/drill_answers.html'
    url_name = 'drill_beginners'

    def pages(self, **kwargs):
        return None
    
    def outcome(self, correct, urls):
        query = self.request.GET.get('query')
        query_list = query.split('X')
        num_of_correct = int(query_list[0])
        if correct:
            num_of_correct += 1
            query_list[0] = str(num_of_correct)
            query = 'X'.join(query_list)
        qn = urls['qn']
        qn += 1
        urls['qn'] = qn
        add_query = {'query': query, 'num_of_correct': num_of_correct}
        urls = {**urls, **add_query}
        return correct, urls
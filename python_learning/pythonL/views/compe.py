from django.shortcuts import render, redirect
from pythonL.models import CustomUser, IntroCourse, Basis, Quartet, Competition
from django.contrib.auth.decorators import login_required
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
    input_ex_list = question.input_ex.split("\r\n/separate/\r\n")
    output_ex_list = question.output_ex.split("\r\n/separate/\r\n")
    examples = zip(input_ex_list, output_ex_list)
    testcases = [input_ex_list[i] + "//" + output_ex_list[i] + "//" + str(i + 1) for i in range(len(input_ex_list))]
    if request.method == 'POST':
        text = request.POST['text'] 
        backup = request.POST['backup'] 
        sn = int(request.POST['selected_n'] )
        if text == '':
            text = backup
        with open('pythonL/competition.py', 'w') as f:
                f.write(text)
        op = subprocess.run('python pythonL/competition.py',input= input_ex_list[sn - 1], shell=True, capture_output=True, text=True, timeout=3)
        out, err = op.stdout, op.stderr
        err = err.split('",')[-1]
        params = {'text': text, 'out' : out, 'err': err, 
                  "title":title,"sentence": sentence, 
                "expectation": expectation, "condition": condition, 
                "format_data": format_data, "format_text": format_text, 
                "input_ex": input_ex_list[sn - 1], "output_ex": output_ex_list[sn - 1], 
                "examples": examples, "testcases": testcases, 
                "sn": sn, "pk": pk}
        return render(request, 'question/compe.html', params)
        
    sn = 1

    user = request.user
    user.s_input = question.input_data
    user.s_output = question.output_data
    user.s_answer = question.e_answer
    user.save()

    params = {"title":title,"sentence": sentence, 
              "expectation": expectation, "condition": condition, 
              "format_data": format_data, "format_text": format_text, 
              "input_ex": input_ex_list[0], "output_ex": output_ex_list[0], 
              "examples": examples, "testcases": testcases, 
              "sn": sn, "pk": pk}
    return render(request, 'question/compe.html', params)


@login_required
def compe_a(request, pk):
    question = Competition.objects.get(section = pk)
    input_ex_list = question.input_ex.split("\r\n/separate/\r\n")
    output_ex_list = question.output_ex.split("\r\n/separate/\r\n")
    if request.method == 'POST':
        text = request.POST['text'] 
        backup = request.POST['backup'] 
        if text == '':
            text = backup
        user = request.user
        c_input = user.s_input
        c_output = user.s_output
        e_answer = user.s_answer
        c_input = c_input.split("\r\n/separate/\r\n")
        c_output = c_output.split("\r\n/separate/\r\n")
        q_input = input_ex_list + c_input
        q_output = output_ex_list + c_output
        u_answer = []
        for i in range(len(q_input)):
            with open('pythonL/competition.py', 'w') as f:
                f.write(text)
            op = subprocess.run('python pythonL/competition.py',input= q_input[i], shell=True, capture_output=True, text=True, timeout=3)
            u_answer.append(op.stdout)
        check = []
        fade_in = []
        for i in range(len(q_input)):
            q_output[i] = q_output[i] + "\n"
            check.append(u_answer[i] == q_output[i])
            fade_in.append(f'fadeIn_{i+1}')
        combine = zip(check, fade_in)
        params = {"combine": combine, "text": text, "e_answer": e_answer }
        return render(request, 'question/compe_a.html', params)
    return render(request, 'question/compe_a.html')
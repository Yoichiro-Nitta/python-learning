import re

def connect(pre_code, text, post_code):
    e, o = len(pre_code), len(post_code)
    if e + o == 0:
        return text
    elif e * o != 0:
        return pre_code + "\n" + text + "\n" + post_code
    elif e > o:
        return pre_code + "\n" + text
    else:
        return text + "\n" + post_code
    

def reduce(err, pre_code):
    lines = pre_code.count('\n') + 1
    err_l = re.findall(r'[1-9][0-9]*',err)
    rep = str(int(err_l[0]) - lines)
    err = re.sub('line [1-9][0-9]*', 'line ' + rep, err)
    return err

def font(ww):
    ww = re.sub(r"([\[\{\( ])([0-9.]+)", r'\1<span class="vibrant_ink_num" data-color="num">\2</span>', ww)
    ww = re.sub(r"('[0-9A-Za-z ,!&~\-]+')", r'<span class="vibrant_ink_str" data-color="str">\1</span>', ww)
    ww = re.sub(r"print\(", r'<span class="vibrant_ink_print"  data-color="print">print</span>(', ww)
    ww = re.sub(r"\.([a-z\_]+)", r'.<span class="vibrant_ink_func" data-color="func">\1</span>', ww)
    ww = re.sub(r" ([<>=!]?=) ", r' <span class="vibrant_ink_print" data-color="print">\1</span> ', ww)
    ww = re.sub(r" ([\+\-\*/%]) ", r' <span class="vibrant_ink_print" data-color="print">\1</span> ', ww)
    ww = re.sub(r" // ", r' <span class="vibrant_ink_print" data-color="print">//</span> ', ww)
    ww = re.sub(r"class ([A-Za-z]+)", r'<span class="vibrant_ink_print" data-color="print">class</span> <span class="vibrant_ink_def" data-color="def">\1</span>', ww)
    ww = re.sub(r"def ([a-z\_]+)", r'<span class="vibrant_ink_print" data-color="print">def</span> <span class="vibrant_ink_def" data-color="def">\1</span>', ww)
    ww = ww.replace("<e>", '</span>')
    ww = ww.replace("<f>", '<span class="vibrant_ink_func" data-color="func">')
    ww = ww.replace("<p>", '<span class="vibrant_ink_print" data-color="print">')
    ww = ww.replace("<s>", '<span class="vibrant_ink_str" data-color="str">')
    ww = "<pre>" + ww + "</pre>"
    return ww

def security(text):
    judge = True
    judge *= not bool(re.search(r"import[a-zA-z0-9 _,\.]+os", text))
    judge *= not bool(re.search(r"import[a-zA-z0-9 _,\.]+Path", text))
    judge *= not bool(re.search(r"import[a-zA-z0-9 _,\.]+shutil", text))
    judge *= not bool(re.search(r"import[a-zA-z0-9 _,\.]+subprocess", text))
    judge *= not bool(re.search(r"from[a-zA-z0-9 _,\.]+django", text))
    judge *= not bool(re.search(r"from[a-zA-z0-9 _,\.]+pathlib", text))
    judge *= not bool(re.search(r"[_\.]+import", text))
    judge *= not bool(re.search(r"open\(", text))
    judge *= not bool(re.search(r"exec\(", text))
    judge *= not bool(re.search(r"eval\(", text))
    if judge:
        return text
    else:
        return 'print("使用できないコードが含まれています。")'

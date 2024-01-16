from decimal import Decimal, ROUND_HALF_UP
import random
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
    ww = ww.replace("____", '<span class="vibrant_ink_bg" data-color="bg">____</span>')
    return ww


def bbcl(func, i_range:str, n:int):
    i_str, r_str= i_range.split(f"\n/bbcl{n}/")
    n_str = str(list(map(func, eval(i_str))))
    a_str = n_str + "\n" + r_str
    return a_str
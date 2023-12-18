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
    ww = re.sub(r"([\[\{\( ])([0-9.]+)", r'\1<span style="color:#A783F8;">\2</span>', ww)
    ww = re.sub(r"('[0-9A-Za-z ,!&~\-]+')", r'<span style="color:#E4DC82;">\1</span>', ww)
    ww = re.sub(r"print\(", r'<span style="color:#E54073;">print</span>(', ww)
    ww = re.sub(r"\.([a-z\_]+)", r'.<span style="color:#84D7EC;">\1</span>', ww)
    ww = re.sub(r" ([<>=!]?=) ", r' <span style="color:#E54073;">\1</span> ', ww)
    ww = re.sub(r" ([\+\-\*/%]) ", r' <span style="color:#E54073;">\1</span> ', ww)
    ww = re.sub(r" // ", r' <span style="color:#E54073;">//</span> ', ww)
    ww = re.sub(r"class ([A-Za-z]+)", r'<span style="color:#E54073;">class</span> <span style="color:#AEE053;">\1</span>', ww)
    ww = re.sub(r"def ([a-z\_]+)", r'<span style="color:#E54073;">def</span> <span style="color:#AEE053;">\1</span>', ww)
    return ww

def font_p(xx):
    xx = xx.replace("int(", '<span style="color:#84D7EC;">int</span>(')
    xx = xx.replace("float(", '<span style="color:#84D7EC;">float</span>(')
    xx = xx.replace("str(", '<span style="color:#84D7EC;">str</span>(')
    xx = xx.replace("list(", '<span style="color:#84D7EC;">list</span>(')
    xx = xx.replace("len(", '<span style="color:#84D7EC;">len</span>(')
    xx = xx.replace("type(", '<span style="color:#84D7EC;">type</span>(')
    xx = xx.replace("map(", '<span style="color:#84D7EC;">map</span>(')
    xx = xx.replace("imput(", '<span style="color:#84D7EC;">imput</span>(')
    xx = xx.replace("range(", '<span style="color:#84D7EC;">range</span>(')
    xx = xx.replace("import ", '<span style="color:#E54073;">import</span> ')
    xx = xx.replace("for ", '<span style="color:#E54073;">for</span> ')
    xx = xx.replace("while ", '<span style="color:#E54073;">while</span> ')
    xx = xx.replace("if ", '<span style="color:#E54073;">if</span> ')
    xx = xx.replace("elif ", '<span style="color:#E54073;">elif</span> ')
    xx = xx.replace("else:", '<span style="color:#E54073;">else</span>:')
    xx = xx.replace(" in ", ' <span style="color:#E54073;">in</span> ')
    xx = xx.replace(" is ", ' <span style="color:#E54073;">is</span> ')
    xx = xx.replace("____", '<span style="color:#282722;">____</span>')
    return xx


def bbcl(func, i_range:str, n:int):
    i_str, r_str= i_range.split(f"\n/bbcl{n}/")
    n_str = str(list(map(func, eval(i_str))))
    a_str = n_str + "\n" + r_str
    return a_str
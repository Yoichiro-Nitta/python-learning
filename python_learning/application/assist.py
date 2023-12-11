from decimal import Decimal, ROUND_HALF_UP
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
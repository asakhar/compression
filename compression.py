# -*- coding: utf-8 -*-
"""
Created on Fri Nov  1 15:05:04 2019

@author: Lizerhigh
"""
from pandas import DataFrame
from pandas import read_json


def sk(val):
    return val[1]

def unpack(s):
    if not b'(' in s:
        return {s: b''}
    #print(s)
    se = []
    c = 0
    st = 0
    ret = {}
    for i in range(len(s)):
        if chr(s[i]) == '(':
            if not c:
                st = i
            c += 1
        elif chr(s[i]) == ')':
            c -= 1
            if not c:
                se.append((st, i))
    #print(se)
    for i in range(len(se)):
        for x, y in unpack(s[se[i][0]+1:se[i][1]]).items():
            if i+1 == len(se):
                ret[x] = y + (s[se[i][1]+1:])
            else:
                ret[x] = y + (s[se[i][1]+1:se[i+1][0]])
            #print(x, ret[x])
    return ret
    
def f_codes(d, base):
    if len(d) == 1:
        #print(list(d.keys()))
        return {k: v[::-1] for k, v in unpack(list(d.keys())[0]).items()}
    d = {k:v for k, v in sorted(list(d.items()), key=sk)}
    mins = b''
    mins_v = 0
    d_keys = list(d.keys())
    d_vals = list(d.values())
    #print(d_keys)
    for i in range(base):
        mins += b'('+d_keys[i]+b')'+enc(str(base-i-1))+b''
        mins_v += d[d_keys[i]]
    #print(mins)
    #d = {k: v for k, v in d.items() if not k in mins}
    d_tmp = {}
    for i in range(base, len(d)):
        d_tmp[d_keys[i]] = d_vals[i]
    d = d_tmp
    #print(d)
    d[mins] = mins_v
    #print(d)
    return f_codes(d, base)

def dec(s):
    return str(s, encoding='utf-8')

def enc(s):
    return bytes(s, encoding='utf-8')

def encf(s):
    tmp = hex(int(s, 2))[2:]
    tmp = '0'*(len(tmp) % 2) + tmp
    #print(f'tmp = {tmp}')
    return eval(f'b"\\x{tmp}"')

def p(arg):
    return len(arg[0])

def add_z(s):
    return b'0'*((8-(len(s)%8))%8)+s

def compress(file, blen, debug = False):
    f = open(file, 'rb')
    mes = b''.join(f.readlines())
    brackets = []
    for i in range(len(mes)):
        if mes[i] == 40:
            brackets.append(enc(str(i)))
            brackets.append(b'')
        if mes[i] == 41:
            brackets.append(enc(str(i)))
            brackets.append(b'1')
    mes = mes.replace(b'(', b'').replace(b')', b'')
    f.close()
    add_b = (blen-len(mes)%blen)%blen
    #print(add_b)
    mes = mes + b'0'*add_b
    mes = [mes[i*blen:(i+1)*blen] for i in range(len(mes)//blen)]
    if debug:
        print(f'Splitted message: {mes} - len = {len(mes)}')
    d = {}
    for x in mes:
        if x in d:
            d[x] += 1
        else:
            d[x] = 1
    if debug:
        print(f'Freq of block: {d}')
    d1 = {k: v for k, v in d.items()}
    d = f_codes(d, 2)
    if debug:
        print(f'Replace table: {d}')
    mes = b''.join([d[x] for x in mes])
    add_zero = (8-len(mes)%8)%8
    #print(add_zero)
    mes = b'0'*add_zero+mes
    if debug:
        print(f'Encoded message (bin): "{mes}" - len = {len(mes)}')
#    tmp = []
#    for i in range(len(mes)//8):
#        tmp.append(encf(mes[i*8:i*8+8]))
#    print(tmp)
    mes = b''.join(list(map(encf, [mes[i*8:i*8+8] for i in range(len(mes)//8)])))
    if debug:
        print(f'Encoded message (1byte): "{mes}" - len = {len(mes)}')
        #print(ord(mes[-1]))
    lines = [enc(str(blen)) + b'\n' + enc(str(add_b)) + b'\n' + enc(str(add_zero)) + b'\n' + b':'.join(brackets) + b'\n' + enc(str(len(d))) + b'\n']
    for i in d1:
        #print(d[i])            
        lines.append(i.replace(b'\n', b'\\n').replace(b'\r', b'\\r')+enc(str(d1[i]))+b'\n')
    lines.append(mes)
    f = open(f'{file}.arc', 'wb')
    f.writelines(lines)
    f.close()
    #df = DataFrame({'add_b': [add_b], 'd': [d], 'mes': [mes], 'add_z': add_zero})
    #df.to_json(f'{file}.arc')
    


def decompress(file):
    f = open(file, 'rb')
    lines = f.readlines()
    f.close()
    blen = int(lines[0][:-1])
    add_b = int(lines[1][:-1])
    add_zero = int(lines[2][:-1])
    brackets = lines[3][:-1].split(b':')
    #print(brackets)
    len_d = int(lines[4][:-1])
    d = {}
    for i in range(5, len_d+5):
        current = lines[i].replace(b'\\n', b'\n').replace(b'\\r', b'\r')
        d[current[:blen]] = int(current[blen:-1])
    d = f_codes(d, 2)
    d = {v: k for k, v in sorted(d.items(), key=p)}
    #print(d)
    mes = b''.join(lines[len_d+5:])
    #print(f'Encoded message (1byte): "{mes}" - len = {len(mes)}')
    mes = (b''.join([add_z(enc(bin(x)[2:])) for x in mes]))[add_zero:]
    #print(mes)
    ret = b''
    while mes:
        for i in d:
            if mes.startswith(i):
                ret += d[i]
                mes = mes[len(i):]

    ret = ret[:len(ret)-add_b]
    for i in range(0, len(brackets), 2):
        index = int(dec(brackets[i]))
        ret = ret[:index] + (b')' if brackets[i+1] else b'(') + ret[index:]
    f = open('dec_'+file.replace('.arc', ''), 'wb')
    f.writelines([ret]) 
    f.close()
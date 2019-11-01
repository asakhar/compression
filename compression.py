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
    if not '(' in s:
        return {s:''}
    se = []
    c = 0
    st = 0
    ret = {}
    for i in range(len(s)):
        if s[i] == '(':
            if not c:
                st = i
            c += 1
        elif s[i] == ')':
            c -= 1
            if not c:
                se.append((st, i))
    #print(se)
    for i in range(len(se)):
        for x, y in unpack(s[se[i][0]+1:se[i][1]]).items():
            if i+1 == len(se):
                ret[x] = y + str(s[se[i][1]+1:])
            else:
                ret[x] = y + str(s[se[i][1]+1:se[i+1][0]])
            #print(x, ret[x])
    return ret
    
def f_codes(d, base):
    if len(d) == 1:
        return {k: v[::-1] for k, v in unpack(list(d.keys())[0]).items()}
    d = {k:v for k, v in sorted(list(d.items()), key=sk)}
    mins = ''
    mins_v = 0
    d_keys = list(d.keys())
    for i in range(base):
        mins += '('+d_keys[i]+')'+str(base-i-1)+''
        mins_v += d[d_keys[i]]
    d = {k: v for k, v in d.items() if not k in mins}
    d[mins] = mins_v
    #print(d)
    return f_codes(d, base)

def dec(s):
    return str(s, encoding='utf-8')

def enc(s):
    return bytes(s, encoding='utf-8')

def encf(s):
    return chr(int(s, 2))

def compress(file, blen, debug = False):
    f = open(file, 'r')
    mes = ''.join(f.readlines()).replace('(', '').replace(')', '')
    f.close()
    add_b = (blen-len(mes)%blen)%blen
    mes = mes + '0'*add_b
    mes = [mes[i*blen:(i+1)*blen] for i in range(len(mes)//blen)]
    if debug:
        print(f'Splitted message: {mes} - len = {len(mes)}')
    d = {}
    for x in mes:
        if x in d:
            d[x] += 1
        else:
            d[x] = 1
    d = f_codes(d, 2)
    if debug:
        print(f'Replace table: {d}')
    mes = ''.join([d[x] for x in mes])
    add_zero = (8-len(mes)%8)%8
    mes = '0'*add_zero+mes
    if debug:
        print(f'Encoded message (bin): "{mes}" - len = {len(mes)}')
    mes = ''.join(list(map(encf, [mes[i*8:i*8+8] for i in range(len(mes)//8)])))
    if debug:
        print(f'Encoded message (2bytes): "{mes}" - len = {len(mes)}')
        print(len(mes))
        #print(ord(mes[-1]))
    df = DataFrame({'add_b': [add_b], 'd': [d], 'mes': [mes], 'add_z': add_zero})
    df.to_json(f'{file}.arc')
    
def p(arg):
    return len(arg[1])

def add_z(s):
    return '0'*((8-len(s)%8)%8)+s

def decompress(file):
    df = read_json(file)
    add_b = df.loc[0]['add_b']
    mes = df.loc[0]['mes']
    add_zero = df.loc[0]['add_z']
    d = {v: k for k, v in sorted(df.loc[0]['d'].items(), key=p)}
    #print(d)
    mes = (''.join([add_z(bin(ord(x))[2:]) for x in mes]))[add_zero:]
    ret = ''
    while mes:
        for i in d:
            if mes.startswith(i):
                ret += d[i]
                mes = mes[len(i):]
    ret = ret[:-add_b]
    f = open(file.replace('.arc', '.dec'), 'w')
    f.writelines(ret.split('\n'))
    f.close()
        
import itertools
import math
import operator
import re
import sys

digit = str.maketrans('₀₁₂₃₄₅₆₇₈₉', '0123456789')
sup = '⁰¹²³⁴⁵⁶⁷⁸⁹'
sub = '₀₁₂₃₄₅₆₇₈₉'
ARGV = itertools.cycle(sys.argv[2:])
cache = {}

def error(msg):
    print(msg, file = sys.stderr)
    sys.exit(1)

iterate = map

def map(function):
    def inner(array):
        if not isinstance(array, list):
            return function(array)
        
        ret = []
        for elem in array:
            ret.append(function(elem))
        return ret
    return inner

def output(array):
    if isinstance(array, list):
        print(*array)
    else:
        print(array)
    return array

def reduce(function):
    def inner(array):
        ret = array.pop(0)
        while array:
            ret = function(ret, array.pop(0))
        return ret
    return inner

def takeargv(amounts):
    if isinstance(amounts, list) and amounts:
        rep = amounts[0]
    elif isinstance(amounts, list):
        rep = 1
    else:
        rep = amounts

    return [tryeval(next(ARGV))for _ in range(rep)]

def takeinput(amounts):
    if isinstance(amounts, list) and amounts:
        rep = amounts[0]
    elif isinstance(amounts, list):
        rep = 1
    else:
        rep = amounts

    return [tryeval(input())for _ in range(rep)]

def tryeval(string):
    if all(x in sub for x in string):
        total = 0
        for p, e in enumerate(string):
            total += sub.index(e) * 10 ** p
        return total

    if all(x in sup for x in string):
        total = 0
        for p, e in enumerate(string):
            total += sup.index(e) * 10 ** p
        return 'ln:{}'.format(total - 1)
            
    try: return eval(string)
    except: return string

def interpreter(code):
    lines = list(filter(None, code.split('\n')))
    
    def transform(arg):
        if re.search(r'^ln:\d+$', str(arg)):
            ln = int(arg.split(':')[1])
            if ln in cache:
                return cache[ln]
            
            ret = execute(lines[ln])
            if isinstance(ret, list) and len(ret) == 1:
                ret = ret[0]
                
            if ln not in cache:
                cache[ln] = ret
            return ret
        return arg

    def execute(line):
        def inner():
            cmd, args = tokens.findall(line)[0]
            cmd = commands[cmd]
            trans = map(transform)
            args = list(trans(map(tryeval)(atkns.findall(args))))
            ret = cmd(args)
            return ret

        try:
            return inner()
        except KeyError as k:
            error('Unknown command: {}'.format(k))
        except IndexError as i:
            error('Unknown command: {}'.format(line.split()[0]))
            
        except Exception as e:
            print(' ' + str(e), repr(e), sep = '\n ', end = '\n\n')

    execute(lines[-1])

commands = {

    '+': sum,
    '×': reduce(operator.mul),
    '-': reduce(operator.sub),
    '÷': reduce(operator.truediv),
    ':': reduce(operator.floordiv),
    '*': reduce(pow),
    'π': map(lambda x: all(int(x%i)for i in range(2,x))and x>1),
    'O': output,
    'I': takeinput,
    '↔': lambda a: a,
    'A': takeargv,
    '⌊': map(math.floor),
    '⌈': map(math.ceil),

}

# ⁰¹²³⁴⁵⁶⁷⁸⁹₀₁₂₃₄₅₆₇₈₉

cmd_re = ''.join(commands.keys()).join('[]').replace('-', r'\-')
tkns_str = r'^(\c)([[ |\b][\p|["[.|\n]*?"]]]*)'
atkns_str = r'[\p|["[.|\n]*?"]]'
for old, new in [['[', '(?:'], [']', ')'], [r'\p', '[⁰¹²³⁴⁵⁶⁷⁸⁹₀₁₂₃₄₅₆₇₈₉]'], [r'\c', cmd_re]]:
    tkns_str = tkns_str.replace(old, new)
    atkns_str = atkns_str.replace(old, new)
tokens = re.compile(tkns_str)
atkns = re.compile(atkns_str)

if __name__ == '__main__':
    code = sys.argv[1]
    try: code = open(code, encoding = 'utf-8').read()
    except: code = code
    interpreter(code)

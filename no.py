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
    if re.search(r'no+', string):
        return string.count('o')

    elif re.search(r'No+', string):
        return chr(string.count('o'))

    elif re.search(r'n+\.*O+', string):
        return float('{}.{}{}'.format(string.count('n'), '0' * string.count('.'), string.count('O')))

    elif re.search(r'yes+', string):
        return 'ln:{}'.format(string.count('s') - 1)

    else:
        return eval(string)

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
            cmd = commands[cmd.count('O')]
            trans = map(transform)
            args = list(trans(map(tryeval)(atkns.findall(args))))
            ret = cmd(args)
            return ret

        return inner()

        try:
            return inner()
        except KeyError as k:
            error('Unknown command: {}'.format(k))
        except IndexError as i:
            error('Unknown command: {}'.format(line.split('?')[0]))
            
        except Exception as e:
            print(' ' + str(e), repr(e), sep = '\n ', end = '\n\n')

    execute(lines[-1])

commands = {

    1: sum,
    2: reduce(operator.mul),
    3: reduce(operator.sub),
    4: reduce(operator.truediv),
    5: reduce(operator.floordiv),
    6: reduce(pow),
    7: map(lambda x: all(int(x%i)for i in range(2,x))and x>1),
    8: output,
    9: takeinput,
    10: lambda a: a,
    11: takeargv,
    12: map(math.floor),
    13: map(math.ceil),
    14: reduce(operator.mod),
    15: ''.join,

}

tkns_str = r'^(NO+)(\?[\a][![\a]]*)?'
atkns_str = r'\a[!\a]*'
for old, new in [['[', '(?:'], [']', ')'], [r'\a', 'no+|yes+|n+\.*O+|No+']]:
    tkns_str = tkns_str.replace(old, new)
    atkns_str = atkns_str.replace(old, new)
tokens = re.compile(tkns_str)
atkns = re.compile(atkns_str)

if __name__ == '__main__':
    code = sys.argv[1]
    try: code = open(code, encoding = 'utf-8').read()
    except: code = code
    interpreter(code)

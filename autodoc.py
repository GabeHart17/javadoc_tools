"""
WARNING: use on text other than syntactically correct java may result in
undefined behavior.
"""

import sys
import os
from enum import Enum


class Scopes(Enum):
    GLOBAL = 0
    CLASS = 1
    FUNCTION = 2
    STATIC = 3


def find_functions(text):
    functions = []  # (start_index, end_index)
    curly_stack = 0
    last_transition = 0  # semicolon or scope change
    scope = Scopes.GLOBAL
    in_string = False
    escaped = False
    in_line_comment = False
    in_block_comment = False
    current_function = []

    for i in range(len(text)):
        c = text[i]
        prev = text[i - 1] if i > 0 else ''

        if in_line_comment:
            if c == '\n':
                in_line_comment = False
        elif in_block_comment:
            if c == '/' and prev == '*':
                in_block_comment = False
        elif in_string:
            if c == '\"' and not escaped:
                in_string = False
            elif c == '\\' and not escaped:
                escaped  = True
            else:
                escaped = False
        elif prev == '/':
            if c == '/':
                in_line_comment = True
            elif c == '*':
                in_block_comment = True
        elif scope == Scopes.GLOBAL:
            if c == '{':
                scope = Scopes.CLASS
        elif scope == Scopes.STATIC:
            if c == '{':
                curly_stack = max(0, curly_stack)
                curly_stack += 1
            elif c == '}':
                curly_stack -= 1
            if curly_stack == 0:
                scope = Scopes.CLASS
        elif scope == Scopes.CLASS:
            s = text[i:].split(maxsplit=1)
            if c == '}':
                scope = Scopes.GLOBAL
            elif s[0] == 'static' and s[1].startswith('{'):
                scope = Scopes.STATIC
                curly_stack = -1
            elif c == '{':
                scope = Scopes.FUNCTION
                current_function.append(last_transition + 1)
                curly_stack += 1
        elif scope == Scopes.FUNCTION:
            if c == '{':
                curly_stack += 1
            elif c == '}':
                curly_stack -= 1
            if curly_stack == 0:
                current_function.append(i + 1)
                functions.append(tuple(current_function))
                current_function = []
                scope = Scopes.CLASS

        if not (in_string or in_block_comment or in_line_comment) and c in '{};\n':
            last_transition = i

    return functions


def doc_function(fn):
    raw_params = fn.split('(', maxsplit=1)[1].split(')', maxsplit=1)[0].split(',')
    params = []
    if '' not in raw_params:
        params = [i.split()[-1].strip() for i in raw_params]
    throws = []
    returns = []

    in_string = False
    escaped = False
    in_line_comment = False
    in_block_comment = False

    for i in range(len(fn)):
        c = fn[i]
        prev = fn[i - 1] if i > 0 else ''

        if in_line_comment:
            if c == '\n':
                in_line_comment = False
        elif in_block_comment:
            if c == '/' and prev == '*':
                in_block_comment = False
        elif in_string:
            if c == '\"' and not escaped:
                in_string = False
            elif c == '\\' and not escaped:
                escaped  = True
            else:
                escaped = False
        elif prev == '/':
            if c == '/':
                in_line_comment = True
            elif c == '*':
                in_block_comment = True
        elif fn[i:].startswith('return'):
            ret_line = fn[i:].split(';', maxsplit=1)[0]
            returns.append(ret_line.split(maxsplit=1)[1].strip())
        elif fn[i:].startswith('throw'):
            thr_line = fn[i:].split(';', maxsplit=1)[0].split(maxsplit=1)[1].strip()
            if thr_line.split(maxsplit=1)[0].strip() == 'new':
                thr_line = thr_line.split(maxsplit=1)[1].strip()
            throws.append(thr_line.split('(', maxsplit=1)[0].strip())

    doc = '/**\n*'
    for i in params:
        doc += f'\n* @param {i}'
    for i in throws:
        doc += f'\n* @throws {i}'
    for i in returns:
        doc += f'\n* @return {i}'
    doc += '\n*/'
    return doc


def main():
    if len(sys.argv) < 2:
        print('specify file as first arg')
        sys.exit()
    with open(sys.argv[1]) as in_file:
        text = in_file.read()
    fns = find_functions(text)
    fns.reverse()
    for f in fns:
        d = doc_function(text[f[0]: f[1]])
        text = text[:f[0]] + f'\n{d}\n' + text[f[0]:]
    out_name = sys.argv[1]
    try:
        os.mkdir(os.path.join(os.path.dirname(sys.argv[1]), 'autodoc'))
    except FileExistsError:
        print('using existing autodoc folder')
    out_name = os.path.join(os.path.dirname(sys.argv[1]), 'autodoc', os.path.basename(sys.argv[1]))
    out_file = open(''.join(out_name), 'w')
    out_file.write(text)
    out_file.close()
    print('done')


if __name__ == '__main__':
    main()

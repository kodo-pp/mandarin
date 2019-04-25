#!/usr/bin/env python3

import os
import sys
import re
import itertools
import subprocess as sp


class GenerationError(Exception):
    pass


def safe_str(x):
    return str(x).replace('-', 'minus_').replace('.', '_point_')


def main():
    print('== Generating grammar.py')

    print('  -- [0/7] Reading Mandarin.lark')
    with open('Mandarin.lark') as f:
        in_data = f.read()

    print('  -- [1/7] Reading gen/keywords.txt')
    with open(os.path.join('gen', 'keywords.txt')) as f:
        keywords = [i for i in f.read().split('\n') if len(i) > 0]

    print('  -- [2/7] Reading gen/operators.txt')
    with open(os.path.join('gen', 'operators.txt')) as f:
        operator_lines = [i.split() for i in f.read().split('\n') if len(i) > 0]

    print('  -- [3/7] Reading operators.py.in')
    with open('operators.py.in') as f:
        operators_template = f.read()
    
    print('  -- [4/7] Writing operators.py')
    operators_dict = ',\n'.join((
        '{op}: Operator(data={op}, priority={prio})'.format(op=repr(op[1]), prio=op[0])
        for op in operator_lines
    ))

    with open('mandarin/operators.py', 'w') as f:
        f.write(operators_template.replace('# @@_operators_@@', operators_dict))

    print('  -- [5/7] Reading grammar.py.in')
    with open('grammar.py.in') as f:
        grammar_template = f.read()
    
    print('  -- [6/7] Writing grammar.py')
    grammar = in_data

    with open('mandarin/grammar.py', 'w') as f:
        f.write(grammar_template.replace('"@@_grammar_@@"', repr(grammar)))

    print('  -- [7/7] Done')

if __name__ == '__main__':
    try:
        main()
    except GenerationError as e:
        print('** Error: {} **'.format(str(e)))
        sys.exit(1)

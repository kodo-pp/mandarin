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

def make_op(s):
    result = []
    mapping = {
        '+': 'C_PLUS',
        '-': 'C_MINUS',
        '*': 'C_STAR',
        '/': 'C_SLASH',
        '%': 'C_PERCENT',
        '!': 'C_BANG',
        '~': 'C_TILDE',
        '=': 'C_EQUAL',
        '<': 'C_LESS',
        '>': 'C_GREATER',
        '.': 'C_DOT',
        '&': 'C_AMP',
        '|': 'C_PIPE',
    }
    for c in s:
        assert c in mapping
        result.append(mapping[c])
    return ' '.join(result)


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

    key_func = lambda op: -op['priority']
    operators = sorted([{'operator': op[1], 'priority': int(op[0])} for op in operator_lines], key=key_func)
    operator_groups = [(-k, list(vs)) for k, vs in itertools.groupby(operators, key=key_func)]

    greater_priority = {}
    operator_rules = []

    prev_k = None
    for k, vs in operator_groups:
        greater_priority[k] = prev_k
        prev_k = k

    for k, vs in operator_groups:
        current_operators = []
        for v in vs:
            current_operators.append(
                '{gp} ({op} {gp})*'.format(
                    gp = 'g__binop_{}'.format(safe_str(greater_priority[k]))
                        if greater_priority[k] is not None
                        else 'front_atomic_expression',
                    op = make_op(v['operator'])
                )
            )
        current_operators_str = ' | '.join(current_operators)
        operator_rules.append('?{}: {}'.format('g__binop_{}'.format(safe_str(k)), current_operators_str))
    operator_rules.append('?g__binop_toplevel: g__binop_{}'.format(safe_str(prev_k)))
    operator_rules_str = '\n'.join(operator_rules)

    with open('mandarin/operators.py', 'w') as f:
        f.write(operators_template.replace('# @@_operators_@@', operators_dict))

    print('  -- [5/7] Reading grammar.py.in')
    with open('grammar.py.in') as f:
        grammar_template = f.read()
    
    print('  -- [6/7] Writing grammar.py')
    grammar = in_data.replace('// @@_operators_@@', operator_rules_str)

    with open('mandarin/grammar.py', 'w') as f:
        f.write(grammar_template.replace('"@@_grammar_@@"', repr(grammar)))

    print('  -- [7/7] Done')

if __name__ == '__main__':
    try:
        main()
    except GenerationError as e:
        print('** Error: {} **'.format(str(e)))
        sys.exit(1)

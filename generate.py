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

    print('  -- [0/7] Reading Mandarin.lark.in')
    with open('Mandarin.lark.in') as f:
        in_data = f.read()

    print('  -- [1/7] Reading gen/keywords.txt')
    with open(os.path.join('gen', 'keywords.txt')) as f:
        keywords = [i for i in f.read().split('\n') if len(i) > 0]

    print('  -- [2/7] Generating keyword rules')
    keyword_rules = []
    for kw in keywords:
        if not re.match(r'[a-z_]+', kw):
            raise GenerationError('Invalid keyword: {}'.format(repr(kw)))
        keyword_rules.append('KW_{kw_name}: "{kw_value}"'.format(kw_name=kw.upper(), kw_value=kw));
    keyword_rules_str = '\n'.join(keyword_rules)

    print('  -- [3/7] Reading gen/operators.txt')
    with open(os.path.join('gen', 'operators.txt')) as f:
        operator_lines = [i for i in f.read().split('\n') if len(i) > 0]

    print('  -- [4/7] Generating operators rule')
    operators = []
    try:
        for op in operator_lines:
            op_tuple = op.split()
            priority = int(op_tuple[0])
            operator = op_tuple[1]
            operators.append({'priority': priority, 'operator': operator})
    except (TypeError, ValueError) as e:
        raise GenerationError(str(e))
    except IndexError as e:
        raise GenerationError('Invalid gen/operators.txt format')
    
    operators_rule_rhs = '\n    | '.join([
        '"{}"'.format(op['operator'].replace('\\', '\\\\').replace('"', '\\"'))
        for op in operators
    ])
    operators_rule = '{}: {}'.format('BINOP', operators_rule_rhs)

    print('  -- [5/7] Reading grammar.py.in')
    with open('grammar.py.in') as f:
        grammar_template = f.read()
    
    print('  -- [6/7] Writing grammar.py')
    data = in_data \
        .replace('// @@_operators_@@', operators_rule) \
        .replace('// @@_keywords_@@',  keyword_rules_str)

    with open('mandarin/grammar.py', 'w') as f:
        f.write(grammar_template.replace('"@@_grammar_@@"', repr(data)))

    print('  -- [7/7] Done')

if __name__ == '__main__':
    try:
        main()
    except GenerationError as e:
        print('** Error: {} **'.format(str(e)))
        sys.exit(1)

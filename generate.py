#!/usr/bin/env python3

import os
import sys
import re
import itertools


class GenerationError(Exception):
    pass


def main():
    print('== Generating Mandarin.g4')

    print('  -- [0/6] Reading Mandarin.g4.in')
    with open('Mandarin.g4.in') as f:
        in_data = f.read()

    print('  -- [1/6] Reading gen/keywords.txt')
    with open(os.path.join('gen', 'keywords.txt')) as f:
        keywords = [i for i in f.read().split('\n') if len(i) > 0]

    print('  -- [2/6] Generating keyword rules')
    keyword_rules = []
    for kw in keywords:
        if not re.match(r'[a-z_]+', kw):
            raise GenerationError('Invalid keyword: {}'.format(repr(kw)))
        keyword_rules.append("KW_{kw_name}: '{kw_value}';".format(kw_name=kw.upper(), kw_value=kw));
    keyword_rules_str = '\n'.join(keyword_rules)

    print('  -- [3/6] Reading gen/operators.txt')
    with open(os.path.join('gen', 'operators.txt')) as f:
        operator_lines = [i for i in f.read().split('\n') if len(i) > 0]

    print('  -- [4/6] Generating operator rules')
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
    
    key_func = lambda op: op['priority']
    operators.sort(key=key_func)
    operator_groups = [(k, list(vs)) for k, vs in itertools.groupby(operators, key=key_func)]

    less_priority = {}
    operator_rules = []
    
    prev_k = None
    for k, vs in operator_groups:
        less_priority[k] = prev_k
        prev_k = k

    for k, vs in operator_groups:
        current_operators = []
        for v in vs:
            current_operators.append(
                '{lp} ({op} {lp})*'.format(
                    lp = 'g__binop_{}'.format(less_priority[k])
                        if less_priority[k] is not None
                        else 'atomic_expression',
                    op = repr(v['operator'])
                )
            )
        current_operators_str = ' | '.join(current_operators)
        operator_rules.append('{}: {};'.format('g__binop_{}'.format(k), current_operators_str))
    operator_rules.append('g__operator_toplevel: g__binop_{};'.format(prev_k))
    operator_rules_str = '\n'.join(operator_rules)
    
    print('  -- [5/6] Writing Mandarin.g4')
    data = in_data \
        .replace('// @@_operators_@@', operator_rules_str) \
        .replace('// @@_keywords_@@',  keyword_rules_str)

    with open('Mandarin.g4', 'w') as f:
        f.write(data)

    print('  -- [6/6] Done')

if __name__ == '__main__':
    try:
        main()
    except GenerationError as e:
        print('** Error: {} **'.format(str(e)))
        sys.exit(1)

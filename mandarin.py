#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import src.tokens as tokens
import src.token_rules as token_rules
import src.expr as expr
import readline
import sys
import os


def main():
    if len(sys.argv) != 2:
        print('Usage: mandarin <file>')
        os._exit(1)
    with open(sys.argv[1]) as f:
        s = f.read()
    token_list = list(tokens.tokenize(s, token_rules.token_rules, token_rules.ignored_tokens))
    print(expr.parse_expression(token_list).dump())

if __name__ == '__main__':
    main()

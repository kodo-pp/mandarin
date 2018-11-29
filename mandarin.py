#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import src.tokens as tokens
import src.token_rules as token_rules
import readline
import sys
import os

def main():
    if len(sys.argv) != 2:
        print('Usage: mandarin <file>')
        os._exit(1)
    with open(sys.argv[1]) as f:
        expr = f.read()
    print(list(tokens.tokenize(expr, token_rules.token_rules, token_rules.ignored_tokens)))

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Mandarin compiler
# Copyright (C) 2018  Alexander Korzun
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

import readline
import sys
import os

import src.tokens as tokens
import src.token_rules as token_rules
import src.expr as expr
import src.fmt as fmt
import src.gen as gen
from src.exceptions import MandarinSyntaxError


def main():
    if len(sys.argv) != 2:
        print('Usage: mandarin <file>')
        os._exit(1)
    with open(sys.argv[1]) as f:
        s = f.read()
    try:
        token_list = list(
            tokens.tokenize(
                s,
                token_rules.token_rules,
                token_rules.ignored_tokens,
                filename=sys.argv[1]
            )
        )
        parser = expr.ExpressionParser(token_list)
        ast = parser.parse_expression()

        codegen = gen.CodeGenerator(ast)
        print(codegen.generate())
    except MandarinSyntaxError as e:
        print(fmt.error('Syntax error: ', fd=sys.stdout) + str(e))
        sys.exit(1)

if __name__ == '__main__':
    main()

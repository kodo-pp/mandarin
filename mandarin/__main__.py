#!/usr/bin/env python3
# Mandarin compiler
# Copyright (C) 2019  Alexander Korzun
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

import sys
import os


def run_parser(code):
    # Imports are inside the function because of their performance impact (it takes lark about 0.07 s to import
    # on my pc, effectively making the whole compiler startup time about 0.14 s, which is quite much)
    # However, if imported locally, this import time won't affect the overall startup time as
    # this function may not even get executed (e.g. when '--help' flag is used)
    from lark import Lark
    from . import postparser
    from . import grammar

    parser = Lark(grammar.GRAMMAR, start='code', parser='lalr', lexer='contextual')
    pre_ast = parser.parse(code)
    
    post_parser = postparser.PostParser()
    return post_parser.post_parse(pre_ast)


def main():
    if len(sys.argv) != 2:
        print('Usage: mandarin <file>')
        sys.exit(1)

    source_filename = sys.argv[1]
    with open(source_filename) as f:
        code = f.read()

    ast = run_parser(code)
    print(ast.pretty())


if __name__ == '__main__':
    main()

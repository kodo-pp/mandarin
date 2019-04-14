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

from lark import Lark

from . import grammar

def main():
    if len(sys.argv) != 2:
        print('Usage: mandarin <file>')
        sys.exit(1)

    source_filename = sys.argv[1]
    with open(source_filename) as f:
        code = f.read()

    parser = Lark(grammar.GRAMMAR, start='code')
    ast = parser.parse(code)
    print(ast.pretty())


if __name__ == '__main__':
    main()

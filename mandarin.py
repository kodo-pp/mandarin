#!/usr/bin/env python3
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

import sys
import os

import antlr4

import src.ast
import src.pretty
from antlr_out.MandarinLexer import MandarinLexer
from antlr_out.MandarinParser import MandarinParser

def main():
    if len(sys.argv) != 2:
        print('Usage: mandarin <file>')
        sys.exit(1)

    source_filename = sys.argv[1]
    source_stream   = antlr4.FileStream(source_filename)
    lexer           = MandarinLexer(source_stream)
    token_stream    = antlr4.CommonTokenStream(lexer)
    parser          = MandarinParser(token_stream)
    antlr_tree      = parser.code()
    ast_generator   = src.ast.AstGenerator()
    tree_walker     = antlr4.ParseTreeWalker()
    tree_walker.walk(ast_generator, antlr_tree)
    ast             = ast_generator.get_ast()
    ast_printer     = src.pretty.TreePrinter()
    ast_printer.print(ast)



if __name__ == '__main__':
    main()

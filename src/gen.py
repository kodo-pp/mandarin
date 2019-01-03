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


import src.expr as expr
from src.exceptions import MandarinSyntaxError
from src.posinfo import EofPosinfo


GLOBAL_PROLOGUE = '''#include <mandarin/mandarin.hpp>'''

GLOBAL_EPILOGUE = '''namespace mandarin::env
{
    int argc = 0;
    char** argv = nullptr;
}

int main(int argc, char** argv)
{
    mandarin::env::argc = argc;
    mandarin::env::argv = argv;
    mandarin::user::main();
}
'''


class FunctionRedefinitionError(MandarinSyntaxError):
    def __init__(self, *a, **k):
        super().__init__(*a, **k)


def get_function_name(func_node):
    return func_node.data[0]


class CodeGenerator:
    def __init__(self, ast):
        self.ast = ast
        self.code = ''

    def generate(self):
        self.emit_global_prologue()
        functions = self.find_functions()
        func_names = set()
        for i in functions:
            self.emit_function(i)
            fname = get_function_name(i)
            if fname in func_names:
                raise FunctionRedefinitionError('Function "{}" redifined', posinfo=EofPosinfo())    # TODO: find real posinfo
            func_names.add(fname)
        self.emit_global_epilogue()
        return self.code

    def emit_global_prologue(self):
        self.write_line(GLOBAL_PROLOGUE)

    def emit_global_epilogue(self):
        self.write_line(GLOBAL_EPILOGUE)

    def write_line(self, code):
        self.write(code + '\n')

    def write(self, code):
        self.code += code

    def find_functions(self):
        for node in self.ast.children:
            if isinstance(node, expr.FunctionDefinitionNode) \
                    or isinstance(node, expr.NativeFunctionDefinitionNode):
                yield node

    def emit_function(self, func):
        self.write_line('// function "{}"'.format(get_function_name(func)))

    def get_function_names(self):
        functions = self.find_functions()
        func_names = set()
        for i in functions:
            self.emit_function(i)
            fname = get_function_name(i)
            func_names.add(fname)
        return func_names

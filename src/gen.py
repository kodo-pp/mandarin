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
import src.tokens as tok
from src.exceptions import MandarinSyntaxError
from src.posinfo import EofPosinfo


GLOBAL_PROLOGUE = '''#include <mandarin/mandarin.hpp>\n'''

GLOBAL_EPILOGUE = '''
namespace mandarin::env
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


class Indentator:
    def __init__(self, indent_str='    '):
        self.indent_str = indent_str
        self.level = 0

    def __enter__(self, *args):
        self.level += 1
        return self

    def __exit__(self, *args):
        self.level -= 1

    def lvl(self):
        return self.level

    def str(self):
        return self.indent_str * self.level


class FunctionRedefinitionError(MandarinSyntaxError):
    def __init__(self, *a, **k):
        super().__init__(*a, **k)


def get_function_name(func_node):
    return func_node.data[0]


def get_function_args(func_node):
    return func_node.data[1]


def get_function_code(func_node):
    return func_node.data[2]


class CodeGenerator:
    def __init__(self, ast):
        self.ast = ast
        self.code = ''
        self.indent = Indentator()

    def generate(self):
        self.emit_global_prologue()

        # Emit all function declarations (with or without body)
        function_declarations = self.find_function_declarations()
        for i in function_declarations:
            self.emit_function_declaration(i)

        self.write_line('')

        # Emit all function definitions (only with body), additionally check for duplicate definitions
        function_definitions = self.find_function_definitions()
        func_def_names = set()
        for i in function_definitions:
            self.emit_function_definition(i)
            fname = get_function_name(i)
            if fname in func_def_names:
                raise FunctionRedefinitionError('Function "{}" redifined', posinfo=EofPosinfo())    # TODO: find real posinfo
            func_def_names.add(fname)

        self.emit_global_epilogue()
        return self.code

    def emit_global_prologue(self):
        self.write_line(GLOBAL_PROLOGUE, raw=True)

    def emit_global_epilogue(self):
        self.write_line(GLOBAL_EPILOGUE, raw=True)

    def write_line(self, code, raw=False):
        if raw:
            self.write(code + '\n')
        else:
            if '\n' in code:
                for line in code.split('\n'):
                    self.write_line(line, raw=raw)
            else:
                self.write(self.indent.str() + code + '\n')

    def write(self, code):
        self.code += code

    def find_function_declarations(self):
        for node in self.ast.children:
            if isinstance(node, expr.FunctionDefinitionNode) \
                    or isinstance(node, expr.NativeFunctionDefinitionNode):
                yield node

    def find_function_definitions(self):
        for node in self.ast.children:
            if isinstance(node, expr.FunctionDefinitionNode) \
                    and not isinstance(node, expr.NativeFunctionDefinitionNode):
                yield node

    def args_to_str(self, args):
        trans = []
        for i in args:
            typenode, varname = i.data
            if not isinstance(typenode, expr.PrimitiveTypeNode):
                # XXX: stub
                raise MandarinSyntaxError('STUB: expected primitive type node', posinfo=typenode.posinfo)
            typename = typenode.data
            if typename == 'var':
                type_str = 'const mandarin::core::Object&'
            elif typename == 'int':
                type_str = 'long'
            elif typename == 'float':
                type_str = 'double'
            else:
                type_str = 'const mandarin::core::StaticObject<mandarin::user::{}>&'.format(typename)
            trans.append('{} {}'.format(type_str, varname))
        return ', '.join(trans)

    def emit_function_declaration(self, func):
        # TODO: type inference
        func_name = get_function_name(func)
        args = get_function_args(func)
        function_decl_header = '{ret_type} mandarin::user::{func_name}({args_str});'.format(
            ret_type='mandarin::core::Object',
            func_name=func_name,
            args_str=self.args_to_str(args),
        )
        self.write_line(function_decl_header)

    def emit_function_definition(self, func):
        # TODO: type inference
        func_name = get_function_name(func)
        args = get_function_args(func)
        function_def_header = '{ret_type} mandarin::user::{func_name}({args_str})'.format(
            ret_type='mandarin::core::Object',
            func_name=func_name,
            args_str=self.args_to_str(args),
        )
        self.write_line(function_def_header)
        self.write_line('{')
        with self.indent:
            code = get_function_code(func)
            self.emit_code_block(code)
            #self.write_line('// Function body') # XXX: stub
        self.write_line('}')
        self.write_line('')

    def emit_code_block(self, code):
        for st in code.children:
            s = self.statement(st)
            self.write_line('{};'.format(s))

    def statement(self, st):
        if isinstance(st, expr.ExpressionNode):
            return self.expression(st)
        else:
            # XXX: stub
            return '/* statement */'
    
    def unescape(self, s):
        yield '"'
        i = 0
        while i < len(s):
            if s[i] == '\\':
                assert i + 1 < len(s)
                ctl = s[i+1]
                if ctl in 'rn0bvt':
                    yield '\\' + ctl + '" "'
                    i += 2
                    continue
                elif ctl == 'x':
                    if i + 3 >= len(s):
                        raise MandarinSyntaxError('Invalid escape sequence', posinfo=EofPosinfo())
                    hexcode = s[i+2:i+4]
                    for c in hexcode:
                        if c not in '0123456789abcdefABCDEF':
                            raise MandarinSyntaxError('Invalid escape sequence', posinfo=EofPosinfo())
                    yield '\\x' + hexcode.lower() + '" "'
                    i += 4
                    continue
                elif ctl == 'u':
                    if i + 5 >= len(s):
                        raise MandarinSyntaxError('Invalid escape sequence', posinfo=EofPosinfo())
                    hexcode = s[i+2:i+6]
                    for c in hexcode:
                        if c not in '0123456789abcdefABCDEF':
                            raise MandarinSyntaxError('Invalid escape sequence', posinfo=EofPosinfo())
                    yield '\\u' + hexcode.lower() + '" "'
                    i += 6
                    continue
                elif ctl == 'U':
                    if i + 9 >= len(s):
                        raise MandarinSyntaxError('Invalid escape sequence', posinfo=EofPosinfo())
                    hexcode = s[i+2:i+10]
                    for c in hexcode:
                        if c not in '0123456789abcdefABCDEF':
                            raise MandarinSyntaxError('Invalid escape sequence', posinfo=EofPosinfo())
                    yield '\\U' + hexcode.lower() + '" "'
                    i += 10
                    continue
                elif ctl == '"':
                    yield '\\"'
                    i += 2
                    continue
                elif ctl == "'":
                    yield "'"
                    i += 2
                    continue
                else:
                    raise MandarinSyntaxError('Invalid escape sequence', posinfo=EofPosinfo())
            else:
                yield s[i]
                i += 1
        yield '"'

    def string(self, s):
        if s[0] != s[-1] or s[0] not in {'"', "'"}:
            raise MandarinSyntaxError('String syntax error', posinfo=EofPosinfo())
        z = s[1:-1]
        return ''.join(self.unescape(z))

    def bin_operator(self, ex):
        op = ex.data.data.val
        if self.have_cxx_op(op):
            return '{} {} {}'.format(
                self.expression(ex.children[0]),
                self.get_cxx_op(op),
                self.expression(ex.children[1]),
            )
        else:
            return '{}({}, {})'.format(
                self.get_emulated_cxx_op(op),
                self.expression(ex.children[0]),
                self.expression(ex.children[1]),
            )

    def get_cxx_op(self, op):
        if op in '+ - * & | ^ && || << >> = <<= >>= += -= *= == < > <= >= != ! ~ &= |= ^='.split():
            return op
        else:
            raise KeyError(op)

    def have_cxx_op(self, op):
        try:
            self.get_cxx_op(op)
            return True
        except KeyError:
            return False

    def get_emulated_cxx_op(self, op):
        return {
            '/': 'mandarin::rt::divide',
            '%': 'mandarin::rt::modulo',
            '->': 'mandarin::rt::implies',
            '/=': 'mandarin::rt::divide_assign',
            '%=': 'mandarin::rt::modulo_assign',
            '..': 'mandarin::rt::half_range',
            '...': 'mandarin::rt::inclusive_range',
        }[op]

    def expression(self, ex):
        if type(ex) is expr.ExpressionNode:
            return '(' + self.expression(ex.children[0]) + ')'
        elif type(ex) is expr.AstCallOperatorNode:
            function = self.expression(ex.children[0])
            args = self.expression(ex.children[1])
            return function + args
        elif type(ex) is expr.OperandNode:
            return self.expression(ex.data)
        elif type(ex) is tok.Identifier:    # TODO: local/global scope
            return ex.val                   # STUB
        elif type(ex) is expr.FunctionCallNode:
            return '({})'.format(', '.join(map(self.expression, ex.children)))
        elif type(ex) is tok.String:
            return self.string(ex.val)
        elif type(ex) is tok.DecimalInteger:
            return ex.val
        elif type(ex) is expr.AstGenericBinaryOperatorNode:
            return self.bin_operator(ex)
        else:
            return '/* expression of type: {}, repr: {} */'.format(type(ex), repr(ex))

    def get_function_definition_names(self):
        functions = self.find_function_definitions()
        func_names = set()
        for i in functions:
            fname = get_function_name(i)
            func_names.add(fname)
        return func_names

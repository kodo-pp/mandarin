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


import lark


class Typename(object):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

    def __repr__(self):
        return 'Typename({})'.format(self.name)


class FunctionArgument(object):
    def __init__(self, name, type):
        self.name = name
        self.type = type

    def __repr__(self):
        return 'FunctionArgument(name: {}, type: {})'.format(self.name, self.type)


class FunctionDeclaration(object):
    def __init__(self, name, return_type, arguments):
        self.name = name
        self.return_type = return_type
        self.arguments = arguments

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return 'FunctionDeclaration(name: {}, returns: {}, arguments: {})'.format(
            repr(self.name),
            repr(self.return_type),
            repr(self.arguments),
        )


class FunctionDefiniton(object):
    def __init__(self, decl, body):
        self.decl = decl
        self.body = body

    def __str__(self):
        return repr(self)
    
    def __repr__(self):
        return 'FunctionDefiniton(decl: {}, body: {})'.format(repr(self.decl), repr(self.body))


class Analyzer(object):
    def __init__(self, ast):
        self.ast = ast

    def get_function_declarations(self):
        for node in self.ast.children:
            if isinstance(node, lark.tree.Tree) \
                    and node.data in ['native_function_declaration', 'function_definition']:
                yield self.parse_function_declaration(node)

    def get_function_definitions(self):
        for node in self.ast.children:
            if isinstance(node, lark.tree.Tree) and node.data == 'function_definition':
                yield self.parse_function_definition(node)

    def parse_function_definition(self, node):
        # function_definition: (0) KW_DEF (1) IDENTIFIER "(" (2) typed_arglist ")" (x) _NL (3) code_block_end
        # typed_arglist: (typed_arg ("," typed_arg)* ","?)?
        # typed_arg: typename? IDENTIFIER
        # code_block_end: code_statement* KW_END
        assert isinstance(node, lark.tree.Tree)
        assert len(node.children) == 4

        name = node.children[1].value
        arglist = node.children[2]
        arguments = list(self.parse_typed_arglist(arglist))
        code = node.children[3]
        body = self.parse_code_block(code)
        return_type = Typename('var') # STUB
        decl = FunctionDeclaration(name=name, return_type=return_type, arguments=arguments)
        return FunctionDefiniton(decl=decl, body=body)
    
    def parse_code_block(self, cb_node):
        # code_block_<***>: code_statement* KW_<***>
        # <***> in [end, else, elif]
        assert isinstance(cb_node, lark.tree.Tree)
        assert cb_node.data in ['code_block_end', 'code_block_elif', 'code_block_else']
        assert len(cb_node.children) >= 1
        end_keyword = cb_node.children[-1]
        assert isinstance(end_keyword, lark.lexer.Token)
        assert end_keyword.type == {
            'code_block_end': 'KW_END',
            'code_block_elif': 'KW_ELIF',
            'code_block_else': 'KW_ELSE',
        }[cb_node.data]

        statements = cb_node.children[:-1]
        return [self.parse_code_statement(st) for st in statements]

    def parse_code_statement(self, statement):
        # STUB
        return statement

    def parse_function_declaration(self, node):
        # native_function_declaration: (0) KW_DEF (1) KW_NATIVE (2) IDENTIFIER "(" (3) typed_arglist ")"
        # typed_arglist: (typed_arg ("," typed_arg)* ","?)?
        # typed_arg: typename? IDENTIFIER
        assert isinstance(node, lark.tree.Tree)
        assert len(node.children) == 4
        is_native = self.is_native(node)

        id_node = node.children[2 if is_native else 1]
        assert isinstance(id_node, lark.lexer.Token)
        assert id_node.type == 'IDENTIFIER'
        name = id_node.value
        arglist = node.children[3 if is_native else 2]
        arguments = list(self.parse_typed_arglist(arglist))
        return_type = Typename('var') # STUB
        return FunctionDeclaration(name=name, return_type=return_type, arguments=arguments)

    def is_native(self, node):
        return isinstance(node.children[1], lark.lexer.Token) and node.children[1].type == 'KW_NATIVE'

    def parse_typed_arglist(self, arglist):
        assert isinstance(arglist, lark.tree.Tree)
        for argnode in arglist.children:
            if isinstance(argnode, lark.tree.Tree) and argnode.data == 'typed_arg':
                if len(argnode.children) == 1:
                    # no typename
                    name, type = argnode.children[-1].value, Typename('var')
                else:
                    # with typename
                    name, type = argnode.children[-1].value, self.parse_typename(argnode.children[0])
                yield FunctionArgument(name=name, type=type)
    
    def parse_typename(self, node):
        assert isinstance(node, lark.tree.Tree)
        assert node.data == 'typename'
        assert len(node.children) == 1
        id_node = node.children[0]
        assert isinstance(id_node, lark.lexer.Token)
        assert id_node.type == 'IDENTIFIER'
        return Typename(id_node.value)

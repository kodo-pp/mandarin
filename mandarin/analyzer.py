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


class VariableAssignment(object):
    def __init__(self, varspec, operator, expr):
        self.varspec = varspec
        self.operator = operator
        self.expr = expr

    def __str__(self):
        return repr(self)
    
    def __repr__(self):
        return 'VarAssignment(var: {}, op: {}, expr: {})'.format(
            repr(self.varspec),
            repr(self.operator),
            repr(self.expr),
        )


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
        # ?code_statement: (expression
        #     | var_declaration
        #     | var_assignment
        #     | if_statement
        #     | for_statement
        #     | while_statement) _NL
        assert isinstance(statement, lark.tree.Tree)
        if statement.data == 'var_declaration':
            return self.parse_var_declaration(statement)
        elif statement.data == 'var_assignment':
            return self.parse_var_assignment(statement)
        elif statement.data == 'if_statement':
            return self.parse_if_statement(statement)
        elif statement.data == 'for_statement':
            return self.parse_for_statement(statement)
        elif statement.data == 'while_statement':
            return self.parse_while_statement(statement)
        elif statement.data == 'expression':
            return self.parse_expression(statement)
        else:
            assert False, 'Unknown code statement: {}'.format(statement.data)
            
    def parse_var_declaration(self, node):
        # STUB!
        return node
            
    def parse_var_assignment(self, node):
        # var_assignment: front_atomic_expression assignment_op expression
        assert isinstance(node, lark.tree.Tree)
        assert len(node.children) == 3
        varspec = self.parse_expression(node.children[0])
        operator = self.parse_operator(node.children[1])
        expr = self.parse_expression(node.children[2])
        return VariableAssignment(varspec=varspec, operator=operator, expr=expr)

    def parse_operator(self, node):
        assert isinstance(node, lark.tree.Tree)
        assert all([isinstance(x, lark.lexer.Token) for x in node.children]) or len(node.children) == 1
        if len(node.children) == 1 and isinstance(node.children[0], lark.tree.Tree):
            return self.parse_operator(node.children[0])
        return ''.join([x.value for x in node.children])

    def parse_if_statement(self, node):
        # STUB!
        return node
            
    def parse_for_statement(self, node):
        # STUB!
        return node
            
    def parse_while_statement(self, node):
        # STUB!
        return node
            
    def parse_expression(self, node):
        # STUB!
        return node

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

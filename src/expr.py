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

import weakref
import src.tokens as tok
from src.exceptions import MandarinSyntaxError

class UnexpecterTokenError(MandarinSyntaxError):
    def __init__(self, text):
        self.text = text


class Node:
    def __init__(self, data):
        self.data = data
        self.name = 'Node'
        self.children = []
        self.parent = None

    def add_child(self, child):
        if child.parent is not None:
            raise Exception('Node already has a parent')
        self.children.append(child)
        child.parent = weakref.ref(self)

    def remove_child(self, child):
        if child not in self.children:
            raise Exception('You are not my child! Go away!')
        child.parent = None
        self.children.remove(child)

    def __repr__(self):
        return '{}({})'.format(self.name, repr(self.data))

    def dump(self, nest=0):
        s = '{}({}) {{\n'.format(self.name, self.data)
        for i in self.children:
            s += '  ' * (nest + 1)
            s += i.dump(nest + 1)
        s += '  ' * nest + '}\n'
        return s


class TopLevelNode(Node):
    def __init__(self):
        super().__init__(None)
        self.name = 'TopLevelNode'


class TopLevelDeclarationNode(Node):
    def __init__(self, data):
        super().__init__(data)
        self.name = 'TopLevelDeclarationNode'
    

class FunctionDeclarationNode(Node):
    def __init__(self, func_name, args, definition):
        data = func_name, args, definition
        super().__init__(data)
        self.name = 'FunctionDeclarationNode'
        self.func_name, self.args, self.definition = func_name, args, definition


class TypeNode(Node):
    def __init__(self, data):
        super().__init__(data)
        self.name = 'ArrayTypeNode'


class PrimitiveTypeNode(Node):
    def __init__(self, data):
        super().__init__(data)
        self.name = 'PrimitiveTypeNode'


class ArrayTypeNode(TypeNode):
    def __init__(self, data):
        super().__init__(data)
        self.name = 'ArrayTypeNode'


class FunctionParameterNode(Node):
    def __init__(self, vartype, varname):
        data = vartype, varname
        self.vartype, self.varname = vartype, varname
        super().__init__(data)
        self.name = 'FunctionParameterNode'


def split_list_by(ls, by, allow_empty=True):
    last_index = 0
    for i, v in enumerate(ls):
        if isinstance(v, by):
            if ls[last_index:i] != [] or allow_empty:
                yield ls[last_index:i]
            last_index = i + 1
    if ls[last_index:] != [] or allow_empty:
        yield ls[last_index:]


class ExpressionParser():
    def __init__(self, tokens, offset=0):
        self.tokens = tokens
        self.offset = offset

    def expect(self, *expected, required=True):
        token = self.tokens[self.offset]
        for Type, name, val in expected:
            if type(Type) is type:
                if isinstance(token, Type) and (val is None or token.val == val):
                    self.offset += 1
                    return [token]
            else:
                length = Type(token, val)
                if length is not None:
                    self.offset += length
                    return tokens[:length]   
        names = ['{} ({})'.format(i[1], repr(i[2])) for i in expected]
        if required:
            raise UnexpecterTokenError('Expected one of these: {}; got {}'.format(', '.join(names), token))
        else:
            return None

    def read_typename(self):
        [base_typename_tok] = self.expect((tok.Identifier, 'typename identifier', None))
        base_typename = base_typename_tok.val
        modifiers = []
        while True:
            modifier_ls = self.expect(
                (tok.Bracket, 'opening square bracket', '['),
                required=False
            )
            if modifier_ls is None:
                break
            modifier_tok = modifier_ls[0]
            if isinstance(modifier_tok, tok.Bracket):
                self.expect((tok.Bracket, 'closing square bracket', ']'))
                modifiers.append(ArrayTypeNode)
            else:
                raise UnexpecterTokenError('Internal logic error: unexpected token: {}'.format(modifier_tok))
        typename = PrimitiveTypeNode(base_typename)
        for Type in modifiers:
            container = Type(data=None)
            container.add_child(typename)
            typename = container
        return typename

    def parse_expression(self):
        root = TopLevelNode()
        while self.offset < len(self.tokens):
            token = self.tokens[self.offset]
            if isinstance(token, tok.Keyword):
                kw = token.val
                if kw == 'def':
                    root.add_child(self.read_function_declaration())
                else:
                    raise UnexpecterTokenError('Unexpected keyword: {}'.format(kw))
            elif isinstance(token, tok.Newline):
                self.offset += 1
                continue
            else:
                raise UnexpecterTokenError('Unexpected token: {}'.format(token))
        return root

    def read_function_declaration(self):
        self.expect((tok.Keyword, 'keyword', 'def'))
        has_body = False
        [later_kw] = self.expect((tok.Keyword, 'keyword', 'later'), required=False)
        if later_kw is not None:
            has_body = False
        [func_name_tok] = self.expect((tok.Identifier, 'identifier', None))
        func_name = func_name_tok.val
        self.expect((tok.Parenthesis, 'opening parenthesis', '('))
        args = []
        while True:
            close_paren_ls = self.expect((tok.Parenthesis, 'closing parenthesis', ')'), required=False)
            if close_paren_ls is not None:
                break
            typename = self.read_typename()
            early_comma_ls = self.expect((tok.Comma, 'comma', ','), required=False)
            if early_comma_ls is not None:
                # If we met a comma right after the type name, then it was a variable name, not a type name
                # Then the typename shouldn't contain anything but an identifier
                if not isinstance(typename, PrimitiveTypeNode):
                    raise UnexpecterTokenError('Expected a variable name, got comma')
                varname = typename.data
                vartype = PrimitiveTypeNode('var')
                args.append(FunctionParameterNode(vartype, varname))
                continue
            else:
                early_paren_ls = self.expect((tok.Parenthesis, 'closing parenthesis', ')'), required=False)
                if early_paren_ls is not None:
                    # If we met a closing paren right after the type name, then it was the last variable name
                    if not isinstance(typename, PrimitiveTypeNode):
                        raise UnexpecterTokenError('Expected a variable name, got closing parenthesis')
                    varname = typename.data
                    vartype = PrimitiveTypeNode('var')
                    args.append(FunctionParameterNode(vartype, varname))
                    break
                # Ok, otherwise let's read the variable name
                vartype = typename
                [varname_tok] = self.expect((tok.Identifier, 'variable name', None))
                varname = varname_tok.val

                # And we should make sure there is a comma or a closing paren after this parameter
                [token] = self.expect((tok.Comma, 'comma', ','), (tok.Parenthesis, 'closing parenthesis', ')'))

                args.append(FunctionParameterNode(vartype, varname))

                # If it is a paren, that was the last parameter
                if isinstance(token, tok.Parenthesis):
                    break
                else:
                    continue
        self.expect((tok.Newline, 'newline', None))
        node = FunctionDeclarationNode(func_name, args, None)
        return node

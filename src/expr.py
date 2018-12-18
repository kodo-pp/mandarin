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

class UnexpectedTokenError(MandarinSyntaxError):
    def __init__(self, text, posinfo):
        super().__init__(text=text, posinfo=posinfo)


class Node:
    def __init__(self, data):
        self.data = data
        self.name = 'Node'
        self.children = []
        self.parent = None

    def add_child(self, child, adopt=False):
        if child.parent is not None and not adopt:
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

    # def dumb
    def dump(self, nest=0, nl=True):
        # TODO: Please delete this code
        if isinstance(self.data, list) or isinstance(self.data, tuple):
            s = '{}({}) {{\n'.format(
                self.name,
                '[' + ', '.join(
                    [i.dump(nest + 1) if isinstance(i, Node) else repr(i) for i in self.data]
                ) + ']'
            )
        else:
            s = '{}({}) {{\n'.format(
                self.name,
                self.data if self.data is not None else ''
            )
        if len(self.children) == 0:
            s = s[:-1] + '}\n'
        else:
            for i in self.children:
                s += '    ' * (nest + 1)
                s += i.dump(nest + 1, nl)
            s += '    ' * nest + '}' + '\n'
        return s


class TopLevelNode(Node):
    def __init__(self, **kwargs):
        super().__init__(data=None, **kwargs)
        self.name = 'TopLevelNode'


class TopLevelDeclarationNode(Node):
    def __init__(self, data, **kwargs):
        super().__init__(data=data, **kwargs)
        self.name = 'TopLevelDeclarationNode'


class FunctionDefinitionNode(Node):
    def __init__(self, func_name, args, definition, **kwargs):
        data = func_name, args, definition
        super().__init__(data=data, **kwargs)
        self.name = 'FunctionDefinitionNode'
        self.func_name, self.args, self.definition = func_name, args, definition
    

class NativeFunctionDefinitionNode(FunctionDefinitionNode):
    def __init__(self, func_name, args):
        super().__init__(func_name, args, None)
        self.name = 'NativeFunctionDefinitionNode'


class TypeNode(Node):
    def __init__(self, data, **kwargs):
        super().__init__(data=data, **kwargs)
        self.name = 'ArrayTypeNode'


class PrimitiveTypeNode(Node):
    def __init__(self, data, **kwargs):
        super().__init__(data=data, **kwargs)
        self.name = 'PrimitiveTypeNode'


class ArrayTypeNode(TypeNode):
    def __init__(self, data, **kwargs):
        super().__init__(data=data, **kwargs)
        self.name = 'ArrayTypeNode'


class FunctionParameterNode(Node):
    def __init__(self, vartype, varname, **kwargs):
        data = vartype, varname
        self.vartype, self.varname = vartype, varname
        super().__init__(data=data, **kwargs)
        self.name = 'FunctionParameterNode'


class CodeBlockNode(TypeNode):
    def __init__(self):
        super().__init__(data=None)
        self.name = 'CodeBlockNode'


class ExpressionNode(TypeNode):
    def __init__(self):
        super().__init__(data=None)
        self.name = 'ExpressionNode'


class OperatorTokenNode(Node):
    def __init__(self, data):
        super().__init__(data=data)
        self.name = 'OperatorTokenNode'


class OperandNode(Node):
    def __init__(self, data):
        super().__init__(data=data)
        self.name = 'OperandNode'


class IdentifierNode(OperandNode):
    def __init__(self, data):
        super().__init__(data=data)
        self.name = 'IdentifierNode'


class FunctionCallNode(Node):
    def __init__(self, data):
        super().__init__(data=data)
        self.name = 'FunctionCallNode'


class ConditionNode(Node):
    def __init__(self):
        super().__init__(data=None)
        self.name = 'ConditionNode'


class ForLoopNode(Node):
    def __init__(self):
        super().__init__(data=None)
        self.name = 'ForLoopNode'


class BranchNode(Node):
    def __init__(self, condition, block):
        super().__init__(data=None)
        self.name = 'BranchNode'
        self.add_child(condition)
        self.add_child(block)


# if CONDITION
class TrueBranchNode(BranchNode):
    def __init__(self, condition, block):
        super().__init__(condition=condition, block=block)
        self.name = 'TrueBranchNode'


# elif CONDITION
class AlternativeBranchNode(BranchNode):
    def __init__(self, condition, block):
        super().__init__(condition=condition, block=block)
        self.name = 'AlternativeBranchNode'


# else
class FalseBranchNode(BranchNode):
    def __init__(self, block):
        super().__init__(condition=Node(data=None), block=block)
        self.name = 'FalseBranchNode'


class AstOperatorNode(Node):
    def __init__(self, operands):
        super().__init__(data=None)
        self.name = 'AstOperatorNode'
        for i in operands:
            self.add_child(i, adopt = True)


class AstUnaryOperatorNode(AstOperatorNode):
    def __init__(self, op):
        super().__init__(operands=[op])
        self.name = 'AstUnaryOperatorNode'


class AstBinaryOperatorNode(AstOperatorNode):
    def __init__(self, lhs, rhs):
        super().__init__(operands=[lhs, rhs])
        self.name = 'AstBinaryOperatorNode'


class AstCallOperatorNode(AstBinaryOperatorNode):
    def __init__(self, func, args_node):
        super().__init__(lhs=func, rhs=args_node)
        self.name = 'AstCallOperatorNode'


class AstGenericUnaryOperatorNode(AstUnaryOperatorNode):
    def __init__(self, operator, operand):
        super().__init__(op=operand)
        self.name = 'AstGenericUnaryOperatorNode'
        self.data = operator


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
        if self.offset >= len(self.tokens):
            if required:
                raise UnexpectedTokenError('Unexpected EOF')
            else:
                return None
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
            raise UnexpectedTokenError(
                'Expected one of these: {}; got {}'.format(', '.join(names), token),
                posinfo=token.posinfo
            )
        else:
            return None

    def read_typename(self):
        [base_typename_tok] = self.expect((tok.Identifier, 'typename identifier', None))
        base_typename = base_typename_tok.val
        modifiers = []
        while True:
            modifier_ls = self.expect(
                (tok.Bracket, 'opening square bracket', '['),
                (tok.Parenthesis, 'opening parenthesis', '('),
                required=False
            )
            if modifier_ls is None:
                break
            modifier_tok = modifier_ls[0]
            if isinstance(modifier_tok, tok.Bracket):
                self.expect((tok.Bracket, 'closing square bracket', ']'))
                modifiers.append(ArrayTypeNode)
            elif isinstance(modifier_tok, tok.Parenthesis):
                raise exceptions.MandarinNotImplementedError('Templates are not implemented')
            else:
                raise UnexpectedTokenError('Internal logic error: unexpected token: {}'.format(modifier_tok))
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
                    root.add_child(self.read_function_definition())
                else:
                    raise UnexpectedTokenError('Unexpected keyword: {}'.format(kw))
            elif isinstance(token, tok.Newline):
                self.offset += 1
                continue
            else:
                raise UnexpectedTokenError('Unexpected token: {}'.format(token), posinfo=token.posinfo)
        return root

    def unget_tokens(self, n=1):
        if n > self.offset:
            raise Exception('Unable to unget {} tokens - only {} were read'.format(n, self.offset))
        self.offset -= n

    def read_code_block(self):
        node = CodeBlockNode()
        while True:
            statement = self.read_code_statement()
            if statement is None:
                break
            node.add_child(statement)
        return node

    def read_code_statement(self):
        while True:
            [what] = self.expect(
                (tok.Newline, 'newline', None),
                (tok.Keyword, 'keyword', 'end'),
                (tok.Keyword, 'keyword', 'else'),
                (tok.Keyword, 'keyword', 'if'),
                (tok.Keyword, 'keyword', 'elif'),
                (tok.Keyword, 'keyword', 'for'),
                (tok.Operand, 'operand', None),
                (tok.Operator, 'unary operator', None),
                (tok.Parenthesis, 'opening parenthesis', '('),
            )
            if isinstance(what, tok.Newline):
                continue
            elif isinstance(what, tok.Keyword) and what.val == 'end':
                return None
            elif isinstance(what, tok.Keyword) and what.val in {'else', 'elif'}:
                self.unget_tokens(1)
                return None
            elif isinstance(what, tok.Keyword) and what.val == 'if':
                #import pudb; pudb.set_trace()
                node = ConditionNode()
                cond = self.read_expression()
                blk = self.read_code_block()
                node.add_child(TrueBranchNode(condition=cond, block=blk))
                while True:
                    maybe_else_or_elif = self.expect(
                        (tok.Keyword, 'keyword', 'else'),
                        (tok.Keyword, 'keyword', 'elif'),
                        required=False
                    )
                    if maybe_else_or_elif is None:
                        break
                    if maybe_else_or_elif[0].val == 'elif':
                        cond = self.read_expression()
                        blk = self.read_code_block()
                        node.add_child(AlternativeBranchNode(condition=cond, block=blk))
                    else:   # else
                        blk = self.read_code_block()
                        node.add_child(FalseBranchNode(block=blk))
                        break
                return node
            elif isinstance(what, tok.Keyword) and what.val == 'for':
                node = ForLoopNode()
                [var] = self.expect((tok.Identifier, 'loop variable name', None))
                self.expect((tok.Keyword, 'keyword', 'in'))
                iter_range = self.read_expression()
                blk = self.read_code_block()
                node.add_child(IdentifierNode(var))
                node.add_child(iter_range)
                node.add_child(blk)
                return node
            elif isinstance(what, tok.Operand) \
                    or isinstance(what, tok.Operator) \
                    or isinstance(what, tok.Parenthesis):
                self.unget_tokens(1)
                return self.read_expression()

    def read_expression(self):
        return self.expression_to_ast(self.read_raw_expression())

    def expand_postfix_unary_operators(self, expr_nodes):
        result_nodes = []
        for node in expr_nodes:
            if isinstance(node, FunctionCallNode):
                if len(result_nodes) == 0:
                    raise MandarinSyntaxError(
                        'Expected a callable object before function call',
                        posinfo=node.posinfo
                    )
                func = result_nodes[-1]
                result_nodes.pop()
                result_nodes.append(AstCallOperatorNode(func=func, args_node=node))
            else:
                if isinstance(node, Node) and not isinstance(node, AstCallOperatorNode):
                    src_children = node.children
                    node.children = self.expand_postfix_unary_operators(src_children)
                result_nodes.append(node)
        return result_nodes

    def expand_prefix_unary_operators(self, expr_nodes):
        result_nodes = []
        for node in reversed(expr_nodes):
            if isinstance(node, OperatorTokenNode):
                op = node.data.val
                possible_operators = {'!', '~', '+', '-'}
                if op not in possible_operators:
                    raise MandarinSyntaxError('Invalid unary operator: "{}"'.format(op), posinfo=node.posinfo)
                if len(result_nodes) == 0:
                    raise MandarinSyntaxError(
                        'Expected operand or expression after a unary operator',
                        posinfo=node.posinfo
                    )
                what = result_nodes[-1]
                result_nodes.pop()
                result_nodes.append(AstGenericUnaryOperatorNode(operator=op, operand=what))
            else:
                if isinstance(node, Node):
                    src_children = node.children
                    node.children = self.expand_prefix_unary_operators(src_children)
                result_nodes.append(node)
        return list(reversed(result_nodes))

    def expand_binary_operators(self, expr_nodes):
        return expr_nodes
    
    def expression_to_ast(self, expr_node):
        # Converts list of nodes to AST
        expr_nodes = expr_node.children
        expr_nodes = self.expand_postfix_unary_operators(expr_nodes)
        expr_nodes = self.expand_prefix_unary_operators(expr_nodes)
        expr_nodes = self.expand_binary_operators(expr_nodes)
        result_node = ExpressionNode()
        for i in expr_nodes:
            result_node.add_child(i, adopt=True)
        return result_node

    def read_raw_expression(self):
        # This functions just reads an expression and return a list of tokens; it doesn't parse
        # the expression
        # TODO: Stub, just reads tokens until a newline
        # TODO: Allow newlines in nested expressions
        node = ExpressionNode()
        token_ls = self.expect(
            # TODO: add arrays and dictionaries
            (tok.Operator, 'unary operator', None),
            (tok.Operand, 'operand', None),
            (tok.Parenthesis, 'opening parenthesis', '('),
            (tok.Newline, 'newline', '\n'),
            required=False
        )
        if token_ls is None:
            return None
        [token] = token_ls
        while True:
            # (1) Check if we should stop reading
            if isinstance(token, tok.Newline):
                break

            # (2) Depending on which token we have read, expect the next one to be of specific type
            if isinstance(token, tok.Operator):
                node.add_child(OperatorTokenNode(token))
                [token] = self.expect(
                    (tok.Operator, 'unary operator', None),
                    (tok.Operand, 'operand', None),
                    (tok.Parenthesis, 'opening parenthesis', '(')
                )
            elif isinstance(token, tok.Operand):
                node.add_child(OperandNode(token))
                token_ls = self.expect(
                    (tok.Operator, 'unary operator', None),
                    (tok.Parenthesis, 'opening parenthesis', '('),
                    (tok.Newline, 'newline', '\n'),
                    required=False
                )
                # An operand can end the expression
                if token_ls is None:
                    break
                else:
                    [token] = token_ls
            elif isinstance(token, tok.Parenthesis) and token.val == '(':
                # An opening parenthesis can mean 2 things: (1) function call or (2) sub-expression
                # Example (1): 7 + foo(23, 2)
                # Example (2): 7 * (3 + 1)
                # In the first case the parenthesis is following an operand,
                # and in the second case it is following an operator OR it is the first token in the
                # expression

                #__import__('pudb').set_trace()

                # TODO
                if len(node.children) == 0 or isinstance(node.children[-1], OperatorTokenNode):
                    # Sub-expression
                    node.add_child(self.read_expression())
                #elif isinstance(node.children[-1].data, tok.Operand):
                else:
                    # Function call
                    node.add_child(self.read_function_call())
                self.expect((tok.Parenthesis, 'closing parenthesis', ')'))

                # Closing parenthesis acts like an operand
                token_ls = self.expect(
                    (tok.Operator, 'unary operator', None),
                    (tok.Parenthesis, 'opening parenthesis', '('),
                    (tok.Newline, 'newline', '\n'),
                    required=False
                )
                # It can end the expression
                if token_ls is None:
                    break
                else:
                    [token] = token_ls
        return node

    def read_function_call(self):
        node = FunctionCallNode(None)
        maybe_paren = self.expect(
            (tok.Parenthesis, 'closing parenthesis', ')'),
            required=False
        )
        if maybe_paren is not None:
            self.unget_tokens(1)
            return node
        while True:
            x = self.read_expression()
            if x is None:
                raise UnexpectedTokenError('Expected expression', self.tokens[self.offset].posinfo)
            node.add_child(x)
            [paren_or_comma] = self.expect(
                (tok.Parenthesis, 'closing parenthesis', ')'),
                (tok.Comma, 'comma', ',')
            )
            if isinstance(paren_or_comma, tok.Parenthesis):
                self.unget_tokens(1)
                return node


    def read_function_definition(self):
        self.expect((tok.Keyword, 'keyword', 'def'))
        has_body = True
        native_kw_ls = self.expect((tok.Keyword, 'keyword', 'native'), required=False)
        if native_kw_ls is not None:
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
                    raise UnexpectedTokenError('Expected a variable name, got comma')
                varname = typename.data
                vartype = PrimitiveTypeNode('var')
                args.append(FunctionParameterNode(vartype, varname))
                continue
            else:
                early_paren_ls = self.expect((tok.Parenthesis, 'closing parenthesis', ')'), required=False)
                if early_paren_ls is not None:
                    # If we met a closing paren right after the type name, then it was the last variable name
                    if not isinstance(typename, PrimitiveTypeNode):
                        raise UnexpectedTokenError('Expected a variable name, got closing parenthesis')
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
        if has_body:
            body = self.read_code_block()
            return FunctionDefinitionNode(func_name, args, body)
        return NativeFunctionDefinitionNode(func_name, args)

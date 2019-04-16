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


import copy

import lark

from . import operators


class BinaryOperatorNode(lark.tree.Tree):
    def __init__(self, lhs, rhs, operator, **kwargs):
        super.__init__(data='binary_operator', children=[lhs, rhs, operator], **kwargs)


class PostParser(object):
    def post_parse(self, pre_ast):
        ast = copy.deepcopy(pre_ast)
        return self.walk(ast)

    def walk(self, ast):
        if isinstance(ast, BinaryOperatorNode):
            raise ValueError('Pre-AST already contains post-parser nodes')
        elif isinstance(ast, lark.lexer.Token):
            # Entirely strip newlines as we don't need them anymore
            if ast.type == 'NL':
                return None
        elif isinstance(ast, lark.tree.Tree):
            if self.is_expression(ast):
                return self.walk_expression(ast.children)
            else:
                ast.children = list(filter(lambda x: x is not None, (self.walk(node) for node in ast.children)))
                return ast
        else:
            raise ValueError('Unknown tree node type: {}'.format(type(ast)))

    def walk_expression(self, children):
        children = [self.walk(node) for node in children]
        rawlhs, rawrhs, op = self.binop_partition(children)
        if rawlhs is None or rawrhs is None or op is None:
            pass
            # Stopped here (TODO)
        lhs = self.walk_expression(rawlhs)
        rhs = self.walk_expression(rawrhs)
        return BinaryOperatorNode(lhs=lhs, rhs=rhs, operator=op)
    
    def binop_partition(self, children):
        operators = [
            (i, node)
            for i, node in enumerate(children)
            if isinstance(node, lark.lexer.Token) and node.type == 'BINOP'
        ]
        if len(operators) == 0:
            return None, None, None
        i, node = min(operators, key = lambda i_node: operators.OPERATORS[i_node[1].value].priority)
        return operators[:i], operators[i+1:], operators[i]

    def is_expression(self, ast):
        return ast.data in {'expression', 'atomic_expression', 'front_atomic_expression'}

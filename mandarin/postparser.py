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

from .operators import OPERATORS


class BinaryOperatorNode(lark.tree.Tree):
    def __init__(self, lhs, rhs, operator, **kwargs):
        super().__init__(data='binary_operator', children=[lhs, rhs, operator], **kwargs)


class PostParser(object):
    def post_parse(self, pre_ast):
        #ast = copy.deepcopy(pre_ast)    # <--- PROBLEM WITH UNSTABLE PARSE TREE PINPOINTED!!!
        #ast = pre_ast
        return pre_ast
        # F*ck the input immutability
        #return self.walk(pre_ast)

    def walk(self, ast):
        if isinstance(ast, BinaryOperatorNode):
            raise ValueError('Pre-AST already contains post-parser nodes')
        elif isinstance(ast, lark.lexer.Token):
            # Entirely strip newlines as we don't need them anymore
            if ast.type == 'NL':
                return None
            else:
                return ast
        elif isinstance(ast, lark.tree.Tree):
            ast.children = [i for i in (self.walk(node) for node in ast.children) if i is not None]
            if self.is_expression(ast):
                expr_node = self.make_expression_tree(ast.children)
                return expr_node
            return ast
        else:
            raise ValueError('Unknown tree node type: {}'.format(type(ast)))

    def make_expression_tree(self, nodes):
        print('make_expression_tree({})'.format(nodes))
        if len(nodes) == 1:
            return nodes[0]
        lhs, rhs, op = self.binop_partition(nodes)
        return [BinaryOperatorNode(lhs=lhs, rhs=rhs, operator=op)]
    
    def binop_partition(self, children):
        operators = [
            node
            for node in children
            if isinstance(node, lark.lexer.Token) and node.type == 'BINOP'
        ]

        enum_operators = list(enumerate(operators))
        if len(enum_operators) == 0:
            return None, None, None
        i, node = min(enum_operators, key = lambda i_node: OPERATORS[i_node[1].value].priority)
        return operators[:i], operators[i+1:], operators[i]

    def is_expression(self, ast):
        return ast.data == 'expression'

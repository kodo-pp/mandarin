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
import pprint

import lark

from .operators import OPERATORS


class BinaryOperatorNode(lark.tree.Tree):
    def __init__(self, lhs, rhs, operator, **kwargs):
        super().__init__(data='binary_operator_node', children=[operator, lhs, rhs], **kwargs)
        self.lhs = lhs
        self.rhs = rhs
        self.op = operator


def make_op(terminals):
    return ''.join([t.value for t in terminals])

def binop(x):
    lhs = x[0]
    rhs = x[-1]
    op = make_op(x[1:-1])
    op_line = x[1].line
    op_column = x[1].column
    node = BinaryOperatorNode(lhs=lhs, rhs=rhs, operator=op)
    node.meta.line = op_line
    node.meta.column = op_column
    return node

class PostParser(lark.visitors.Transformer):
    @staticmethod
    def g__binop_1000(x):
        return binop(x)

    @staticmethod
    def g__binop_500(x):
        return binop(x)

    @staticmethod
    def g__binop_200(x):
        return binop(x)

    @staticmethod
    def g__binop_100(x):
        return binop(x)

    @staticmethod
    def g__binop_30(x):
        return binop(x)

    @staticmethod
    def g__binop_20(x):
        return binop(x)

    @staticmethod
    def g__binop_minus_1000(x):
        return binop(x)

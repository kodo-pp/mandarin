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


import antlr4


class AstNode(object):
    def __init__(self, value):
        self.value = value
        self.children = []

    def __repr__(self):
        if self.value is None:
            return self.__class__.__name__
        else:
            return '{}({})'.format(self.__class__.__name__, repr(self.value))

    def __str__(self):
        return str(self.value)

    def add(self, child):
        self.children.append(child)


class EmptyAstNode(AstNode):
    def __init__(self):
        super().__init__(None)


class RootAstNode(EmptyAstNode):
    pass


class ToplevelStatementAstNode(AstNode):
    pass


class AstGenerator(antlr4.ParseTreeListener):
    def __init__(self):
        self.ast_root = EmptyAstNode()
        self.stack = []

    def get_ast(self):
        return self.ast_root

    def enterCode(self, ctx):
        self.ast_root = RootAstNode()
        self.stack = [self.ast_root]

    def exitCode(self, ctx):
        self.stack = []

    def enterToplevel_statement(self, ctx):
        node = ToplevelStatementAstNode(None)
        self.stack[-1].add(node)
        self.stack.append(node)

    def exitToplevel_statement(self, ctx):
        self.stack.pop()


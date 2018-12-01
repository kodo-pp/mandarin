# -*- coding: utf-8 -*-

import weakref
import src.tokens as tok


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
    

def split_list_by(ls, by, allow_empty=True):
    last_index = 0
    for i, v in enumerate(ls):
        if isinstance(v, by):
            if ls[last_index:i] != [] or allow_empty:
                yield ls[last_index:i]
            last_index = i + 1
    if ls[last_index:] != [] or allow_empty:
        yield ls[last_index:]


def parse_expression(tokens):
    root = TopLevelNode()
    declarations = split_list_by(tokens, tok.Newline, False)
    for i in declarations:
        root.add_child(TopLevelDeclarationNode(i))
    return root

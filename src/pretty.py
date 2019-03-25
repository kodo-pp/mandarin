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


def default_children_getter(node):
    return node.children


class TreePrinter(object):
    def __init__(self, *, children_getter = default_children_getter, value_getter = repr):
        self.children_getter = children_getter
        self.value_getter = value_getter

    def print(self, root, **kwargs):
        for line in self.get_lines(root):
            print(line, **kwargs)

    def get_lines(self, root):
        return (i for i in self._get_lines(root))

    def _get_lines(self, root, nest=[]):
        if len(nest) == 0:
            yield self.value_getter(root)
        else:
            start = self._make_start(nest)
            yield start + self.value_getter(root)
        children = self.children_getter(root)
        for i, child in enumerate(children):
            nest.append(i != len(children) - 1)
            for line in self._get_lines(child, nest):
                yield line
            nest.pop(-1)

    def _make_start(self, nest):
        def mapper(x):
            return '|  ' if x else '   '

        return ''.join(map(mapper, nest[:-1])) + '+- '

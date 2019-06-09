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


class Posinfo(object):
    """ Information about position in a source file """

    __slots__ = ['line', 'column', 'filename']

    def __init__(self, line, column, filename):
        self.line = line
        self.column = column
        self.filename = filename

    def __str__(self):
        return f'{self.filename}, line {self.line}, column {self.column}'


class EofPosinfo(Posinfo):
    __slots__ = ['line', 'column', 'filename']

    def __init__(self, filename):
        super().__init__(None, None, filename)

    def __str__(self):
        return f'{self.filename}, end of file'


def from_lark(filename, node):
    line = node.line
    column = node.column
    return Posinfo(filename=filename, line=line, column=column)


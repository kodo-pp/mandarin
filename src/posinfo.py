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

class Posinfo:
    def __init__(self, line=1, col=1, filename=None):
        self.filename = filename
        self.line = line
        self.col = col

    def colshift(self, n=1):
        self.col += n

    def newline(self, n=1):
        self.col = 1
        self.line += n

    def str(self, s):
        newlines = s.count('\n')
        col_offset = len(s.split('\n')[-1])
        self.col = col_offset + 1
        self.line += newlines

    def fmt(self):
        return '{}: line {}, col {}'.format(
            self.filename if self.filename is not None else '<unknown file>',
            self.line,
            self.col
        )

class EofPosinfo(Posinfo):
    def __init__(self, filename=None):
        super().__init__(line=-1, col=-1, filename=filename)

    def fmt(self):
        return '{}: end of file'.format(self.filename if self.filename is not None else '<unknown file>')

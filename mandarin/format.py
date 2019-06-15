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


#from . import posinfo as pi

import os
import sys
import colorama
import traceback as tb

colorama.init()


class Formatter(object):
    __slots__ = ['data']

    def __init__(self, filename, code):
        self.data = {filename: code}

    def add_file(self, filename, code):
        assert filename not in self.data
        self.data[filename] = code

    @staticmethod
    def is_output_colored(forced=None):
        if forced is None:
            return sys.stderr.isatty()
        return forced

    @staticmethod
    def get_colortab(color=None):
        if Formatter.is_output_colored(color):
            return {
                'warning':      '\x1b[1;35m{}\x1b[0m',
                'error':        '\x1b[1;31m{}\x1b[0m',
                'number':       '\x1b[31m{}\x1b[0m',
                'filename':     '\x1b[1m{}\x1b[0m',
                'desc':         '\x1b[1m{}\x1b[0m',
                'lineno_fmt':   Formatter.lineno_fmt,
                'position_fmt': Formatter.position_fmt,
            }
        else:
            return {
                'warning':      '{}',
                'error':        '{}',
                'number':       '{}',
                'filename':     '{}',
                'desc':         '{}',
                'lineno_fmt':   lambda x: x,
                'position_fmt': lambda x: x,
            }

    @staticmethod
    def lineno_fmt(line):
        def gen():
            yield '\x1b[36m'
            t = line.index(' ')
            p = line.rindex(']')
            yield line[:t+1]
            yield '\x1b[31m'
            yield line[t+1:p]
            yield '\x1b[36m'
            yield line[p:]
            yield '\x1b[0m'
        return ''.join(gen())

    @staticmethod
    def position_fmt(pos):
        def gen():
            yield '\x1b[35m'
            t = pos.index('^')
            yield pos[:t]
            yield '\x1b[1;31m'
            yield pos[t]
            yield '\x1b[0;35m'
            yield pos[t+1:]
            yield '\x1b[0m'
        return ''.join(gen())


    def print_compile_error(self, e, warning=False, color=None):
        color = self.is_output_colored(color)
        tab = self.get_colortab(color)
        if warning:
            prefix = tab['warning'].format('Warning: ')
        else:
            prefix = tab['error'].format('Error: ')
        print(prefix + str(e), file=sys.stderr)

        #if not isinstance(e.posinfo, pi.EofPosinfo):
        if (e.posinfo.filename in self.data) and (e.posinfo.line is not None):
            code = self.data[e.posinfo.filename]
            lines = code.split('\n')
            n = len(lines)
            lineno = e.posinfo.line
            column_no = e.posinfo.column
            line = lines[lineno-1]
            raw_prefix = '[line {:@}] |  '.replace('@', str(len(str(n)))).format(lineno)
            prefix = '    ' + tab['lineno_fmt'](raw_prefix)
            print(prefix + line, file=sys.stderr)
            end = ' (newline)' if column_no > len(line) else ''
            print('    ' + ' ' * len(raw_prefix) + tab['position_fmt'](
                '~' * (column_no - 1) + '^' + '~' * (len(line) - column_no) + end),
                file=sys.stderr,
            )
            print(file=sys.stderr)
    
        if not warning and os.getenv('MANDARIN_VERBOSE_ERRORS', '0') == '1':
            print('Verbose errors enabled, displaying the traceback', file=sys.stderr)
            tb.print_exc()

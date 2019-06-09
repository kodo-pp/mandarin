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

import os
import sys
import traceback as tb

from . import analyzer
from . import generator
from . import grammar
from . import postparser
from . import targets
from .exceptions import UsageError, MandarinError

from lark import Lark


def run_parser(code):
    parser = Lark(
        grammar.GRAMMAR,
        start = 'code',
        parser = 'earley',
        propagate_positions = True,
    )
    ast = parser.parse(code)
    pp = postparser.PostParser()
    ast = pp.transform(ast)
    
    return ast


def print_compile_error(e, code):
    print('Error: ' + str(e))
    lines = code.split('\n')
    n = len(lines)
    lineno = e.posinfo.line
    column_no = e.posinfo.column
    line = lines[lineno-1]
    prefix = '[{}:{:@}] |  '.replace('@', str(len(str(n)))).format(e.posinfo.filename, lineno)
    print(prefix + line)
    print(' ' * len(prefix) + '~' * (column_no - 1) + '^' + '~' * (len(line) - column_no))
    print()

    if os.getenv('MANDARIN_VERBOSE_ERRORS', '0') == '1':
        print('Verbose errors enabled, displaying the traceback')
        tb.print_exc()


def main():
    if len(sys.argv) != 3:
        print('Usage: mandarin <file> <output_file>')
        sys.exit(1)

    try:
        source_filename = sys.argv[1]
        output_filename = sys.argv[2]
        with open(source_filename) as f:
            code = f.read()

        ast = run_parser(code)
        an = analyzer.Analyzer(ast, filename=source_filename)
        decls = list(an.get_function_declarations())
        defs = list(an.get_function_definitions())
        #print('-- FUNCTION DECLARATIONS --')
        #print(decls)
        #print()
        #print('-- FUNCTION DEFINITIONS --')
        #print(defs)

        # STUB
        options = {'is_standalone': True, 'target': 'cxx'}
        try:
            target = targets.select(options['target'])
        except KeyError as e:
            raise UsageError('No such target: {}'.format(options['target'])) from e
        gen = target.GeneratorType(analyzer=an, options=options)
        
        generated_code = gen.generate()
        if output_filename == '-':
            print(generated_code)
        else:
            with open(output_filename, 'w') as f:
                f.write(generated_code)
    except MandarinError as e:
        print_compile_error(e, code=code)
        print('Build failed')
        sys.exit(2)
    except Exception as e:
        print('Internal compiler error: {}: {}'.format(e.__class__.__name__, str(e)), file=sys.stderr)
        tb.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

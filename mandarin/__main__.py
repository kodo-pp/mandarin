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
from argparse import ArgumentParser

from . import analyzer
from . import generator
from . import grammar
from . import postparser
from . import targets
from . import format as fmt
from . import posinfo as pi
from .exceptions import UsageError, MandarinError, MandarinSyntaxError

from lark import Lark
from lark.exceptions import LarkError, UnexpectedToken, UnexpectedCharacters


def parse_args():
    ap = ArgumentParser('mandarin', description='Mandarin compiler')
    ap.add_argument('--output', '-o', help='Name of the output file. - == stdout (default)', default='-')
    ap.add_argument('--standalone', '-s', help='Generate standalone code', action='store_true')

    target_names = [t.name for t in targets.targets]
    ap.add_argument(
        '--target',
        '-t',
        help = 'Target to generate code for (default = cxx)',
        default = 'cxx',
        choices = target_names,
    )

    ap.add_argument('input_filename', help='Name of the source file')

    parsed = ap.parse_args()
    
    options = {
        'output': parsed.output,
        'input': parsed.input_filename,
        'is_standalone': parsed.standalone,
        'target': parsed.target,
    }
    return options


def run_parser(code, filename=None):
    try:
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
    except UnexpectedToken as e:
        raise MandarinSyntaxError(
            message = f'Unexpected token `{repr(e.token)}`',
            posinfo = pi.from_lark(filename=filename, node=e),
        ) from e
    except UnexpectedCharacters as e:
        raise MandarinSyntaxError(
            message = f'Unexpected token',
            posinfo = pi.from_lark(filename=filename, node=e),
        ) from e
    except LarkError as e:
        raise MandarinSyntaxError(
            message = str(e),
            posinfo = pi.EofPosinfo(filename=filename),
        ) from e


def parse_file(filename, code):
    ast = run_parser(code, filename=filename)
    an = analyzer.Analyzer(ast, filename=filename)
    return an


def find_librin():
    # STUB!
    return 'librin.man'


def read_file(filename):
    with open(filename) as f:
        return f.read()


def main():
    try:
        options = parse_args()
        librin_filename = find_librin()

        main_code = read_file(options['input'])
        librin_code = read_file(librin_filename)

        formatter = fmt.Formatter(filename=options['input'], code=main_code)
        formatter.add_file(filename=librin_filename, code=librin_code)

        main_an = parse_file(options['input'], main_code)
        librin_an = parse_file(librin_filename, librin_code)

        try:
            target = targets.select(options['target'])
        except KeyError as e:
            raise UsageError('No such target: {}'.format(options['target'])) from e
        gen = target.GeneratorType(analyzer=main_an, formatter=formatter, options=options)
        gen.import_analyzer(librin_an)
        
        generated_code = gen.generate()
        if options['output'] == '-':
            print(generated_code)
        else:
            with open(options['output'], 'w') as f:
                f.write(generated_code)
    except MandarinError as e:
        formatter.print_compile_error(e)
        print('Build failed', file=sys.stderr)
        sys.exit(2)
    except Exception as e:
        print('Internal compiler error: {}: {}'.format(e.__class__.__name__, str(e)), file=sys.stderr)
        tb.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

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
import re
import src.exceptions as exceptions


class UnknownTokenError(exceptions.MandarinSyntaxError):
    def __init__(self, token):
        text = 'unknown token in expression: ' + repr(token)
        super().__init__(text)
        self.token = token

    def __repr__(self):
        return 'UnknownTokenError: ' + repr(self.token)

    def __str__(self):
        return str(self.text)


class AmbiguousTokenError(exceptions.MandarinSyntaxError):
    def __init__(self, token, matches):
        text = 'ambiguous token in expression: {}. It matches at least these token rules:\n{}'.format(
            repr(token),
            '\n'.join(['\t-> {} (match {})'.format(repr(s), repr(token[:n])) for n, s in matches])
        )
        super().__init__(text)
        self.token = token
        self.matches = matches

    def __repr__(self):
        return 'AmbiguousTokenError: ' + repr(self.token)

    def __str__(self):
        return str(self.text)


class Token:
    def __init__(self, val):
        self.val = val
        self.name = 'Token'

    def __repr__(self):
        return '{}({})'.format(self.name, repr(self.val))


class Operator(Token):
    def __init__(self, val):
        super().__init__(val=val)
        self.name = 'Operator'


class Operand(Token):
    def __init__(self, val):
        super().__init__(val=val)
        self.name = 'Operand'


class Whitespace(Token):
    def __init__(self, val):
        super().__init__(val=val)
        self.name = 'Whitespace'


class SyntaxConstruction(Token):
    def __init__(self, val):
        super().__init__(val=val)
        self.name = 'SyntaxConstruction'


class Newline(SyntaxConstruction):
    def __init__(self, val):
        super().__init__(val=val)
        self.name = 'Newline'


class Literal(Operand):
    def __init__(self, val):
        super().__init__(val=val)
        self.name = 'Literal'


class Integer(Literal):
    def __init__(self, val):
        super().__init__(val=val)
        self.name = 'Integer'


class BoolLiteral(Literal):
    def __init__(self, val):
        super().__init__(val=val)
        self.name = 'BoolLiteral'


class DecimalInteger(Integer):
    def __init__(self, val):
        super().__init__(val=val)
        self.name = 'DecimalInteger'


class HexadecimalInteger(Integer):
    def __init__(self, val):
        super().__init__(val=val)
        self.name = 'HexadecimalInteger'


class OctalInteger(Integer):
    def __init__(self, val):
        super().__init__(val=val)
        self.name = 'OctalInteger'


class BinaryInteger(Integer):
    def __init__(self, val):
        super().__init__(val=val)
        self.name = 'BinaryInteger'


class String(Literal):
    def __init__(self, val):
        super().__init__(val=val)
        self.name = 'String'


class Float(Literal):
    def __init__(self, val):
        super().__init__(val=val)
        self.name = 'Float'


class Identifier(Operand):
    def __init__(self, val):
        super().__init__(val=val)
        self.name = 'Identifier'


class Punctuation(SyntaxConstruction):
    def __init__(self, val):
        super().__init__(val=val)
        self.name = 'Punctuation'


class Parenthesis(Punctuation):
    def __init__(self, val):
        super().__init__(val=val)
        self.name = 'Parenthesis'


class Bracket(Punctuation):
    def __init__(self, val):
        super().__init__(val=val)
        self.name = 'Bracket'


class Brace(Punctuation):
    def __init__(self, val):
        super().__init__(val=val)
        self.name = 'Brace'


class Comma(Punctuation):
    def __init__(self, val):
        super().__init__(val=val)
        self.name = 'Comma'


class Colon(Punctuation):
    def __init__(self, val):
        super().__init__(val=val)
        self.name = 'Colon'


class Keyword(SyntaxConstruction):
    def __init__(self, val):
        super().__init__(val=val)
        self.name = 'Keyword'


class Comment(Token):
    def __init__(self, val):
        super().__init__(val=val)
        self.name = 'Comment'


def is_token_ignored(token, ignlist):
    for T in ignlist:
        if isinstance(token, T):
            return True
    return False


def tokenize(expr, token_rules, ignored_tokens):
    while len(expr) > 0:
        token, expr = read_token(expr, token_rules)
        if not is_token_ignored(token, ignored_tokens):
            yield token


def read_token(expr, token_rules):
    matches = []
    for Type, regex in token_rules.items():
        if type(regex) is str:
            match = re.match(regex, expr)
            if match is None:
                continue
            start, end = match.span()
            length = end - start
            matches.append((length, Type))
        else:
            length = regex(expr)
            if length is None:
                continue
            matches.append((length, Type))

    matches = list(reversed(sorted(matches, key=lambda x: x[0])))
    if len(matches) == 0:
        raise UnknownTokenError(expr)
    max_length = matches[0][0]

    longest_matches = []
    for i in matches:
        if i[0] == max_length:
            longest_matches.append(i)

    if len(longest_matches) >= 2:
        raise AmbiguousTokenError(expr, longest_matches)
    else:
        length, Type = longest_matches[0]
        return Type(expr[:length]), expr[length:]

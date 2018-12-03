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

import string

import src.tokens as tokens
from src.string_matcher import StringMatcher


def is_keyword(s):
    core_kws = {
        'break',
        'class',
        'continue',
        'def',
        'elif',
        'else',
        'end',
        'for',
        'if',
        'in',
        'is',
        'later',
        'pass',
        'super',
        'return',
        'template',
        'type',
        'while'
    }
    return s in core_kws

def is_bool_literal(s):
    return s in {'true', 'false'}


def maybe_identifier_length(s):
    if s is None:
        return None
    if is_keyword(s) or is_bool_literal(s):
        return None
    else:
        return len(s)

def maybe_bool_literal_length(s):
    if s is None:
        return None
    if is_bool_literal(s):
        return len(s)
    else:
        return None

def maybe_keyword_length(s):
    if s is None:
        return None
    if is_keyword(s):
        return len(s)
    else:
        return None


def read_base(expr):
    id_chars = set(string.ascii_letters + string.digits + '_')
    id_firstchars = set(string.ascii_letters + '_')
    if len(expr) == 0 or expr[0] not in id_firstchars:
        return None
    for length in range(len(expr)):
        if expr[length] not in id_chars:
            return expr[:length] if length > 0 else None
    return expr

def read_identifier(expr):
    return maybe_identifier_length(read_base(expr))

def read_bool_literal(expr):
    return maybe_bool_literal_length(read_base(expr))

def read_keyword(expr):
    return maybe_keyword_length(read_base(expr))


def read_string(expr):
    if len(expr) == 0:
        return None
    q = expr[0]
    if q not in {'"', "'"}:
        return None
    i = 1
    while i < len(expr):
        if expr[i] == q:
            return i + 1
        elif expr[i] == '\\':
            i += 2
        else:
            i += 1
    return None


def read_comment(expr):
    if len(expr) == 0:
        return None
    if expr[0] != '#':
        return None
    i = 1
    while i < len(expr) and expr[i] != '\n':
        i += 1
    return i


operator_matcher = StringMatcher(
    '+ - * / % ! && || < <= == != >= > = += -= *= /= %= >> << >>= <<= & | ~ &= |= ^ ^= . .. ...'.split()
)


token_rules = {
    tokens.DecimalInteger:      r'[1-9][0-9]*|0',
    tokens.Float:               r'(([1-9][0-9]*|0)?[.][0-9]+(e[+-]?[0-9]+)?)|(([1-9][0-9]*|0)e[+-]?([0-9]+))',
    tokens.Whitespace:          r'[ \t]',
    tokens.Newline:             r'\r?\n',
    tokens.Identifier:          read_identifier,
    tokens.Operator:            operator_matcher.longest_len,
    tokens.Parenthesis:         r'[()]',
    tokens.Bracket:             r'\[|\]',
    tokens.Brace:               r'[{}]',
    tokens.Comma:               r',',
    tokens.Colon:               r':',
    tokens.Keyword:             read_keyword,
    tokens.String:              read_string,
    tokens.BoolLiteral:         read_bool_literal,
    tokens.Comment:             read_comment,
}


ignored_tokens = [tokens.Whitespace, tokens.Comment]

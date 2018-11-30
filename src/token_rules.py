# -*- coding: utf-8 -*-

import string

import src.tokens as tokens
from src.string_matcher import StringMatcher


def is_keyword(s):
    core_kws = {
        'def',
        'if',
        'end',
        'for',
        'in',
        'while',
        'break',
        'continue',
        'return',
        'class',
        'template',
        'type',
        'elif',
        'else',
    }
    typename_kws = {
        'int',
        'bool',
        'uint',
        'float',
        'string',
        'tuple',
        'array',
        'function',
    }
    kws = core_kws.union(typename_kws)
    return s in kws

def maybe_identifier_length(s):
    if is_keyword(s) or is_bool_literal(s):
        return None
    else:
        return len(s)

def maybe_bool_literal_length(s):
    if is_bool_literal(s):
        return len(s)
    else:
        return None

def is_bool_literal(s):
    return s in {'true', 'false'}

def maybe_keyword_length(s):
    if is_keyword(s):
        return len(s)
    else:
        return None

def read_identifier(expr):
    id_chars = set(string.ascii_letters + string.digits + '_')
    id_firstchars = set(string.ascii_letters + '_')
    if len(expr) == 0 or expr[0] not in id_firstchars:
        return None
    for length in range(len(expr)):
        if expr[length] not in id_chars:
            return maybe_identifier_length(expr[:length]) if length > 0 else None

def read_bool_literal(expr):
    id_chars = set(string.ascii_letters + string.digits + '_')
    id_firstchars = set(string.ascii_letters + '_')
    if len(expr) == 0 or expr[0] not in id_firstchars:
        return None
    for length in range(len(expr)):
        if expr[length] not in id_chars:
            return maybe_bool_literal_length(expr[:length]) if length > 0 else None

def read_keyword(expr):
    id_chars = set(string.ascii_letters + string.digits + '_')
    id_firstchars = set(string.ascii_letters + '_')
    if len(expr) == 0 or expr[0] not in id_firstchars:
        return None
    for length in range(len(expr)):
        if expr[length] not in id_chars:
            return maybe_keyword_length(expr[:length]) if length > 0 else None

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

operator_matcher = StringMatcher(
    '+ - * / % ! && || < <= == != >= > = += -= *= /= %= >> << >>= <<= & | ~ &= |= ^ ^= .. ...'.split()
)


token_rules = {
    tokens.DecimalInteger:      r'[1-9][0-9]*|0',
    tokens.Float:               r'(([1-9][0-9]*|0)?[.][0-9]+(e[+-]?[0-9]+)?)|(([1-9][0-9]*|0)e[+-]?([0-9]+))',
    tokens.Whitespace:          r'[ \t]',
    tokens.Newline:             r'\r?\n',
    tokens.Identifier:          read_identifier,
    tokens.Operator:            operator_matcher.longest_len,
    tokens.Parenthesis:         r'[()]',
    tokens.Comma:               r',',
    tokens.Keyword:             read_keyword,
    tokens.String:              read_string,
    tokens.BoolLiteral:         read_bool_literal,
}


ignored_tokens = [tokens.Whitespace]

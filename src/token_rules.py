# -*- coding: utf-8 -*-

import string

import src.tokens as tokens


def is_keyword(s):
    core_kws = set([
        'def', 'if', 'end', 'for', 'in', 'while', 'break', 'continue', 'return', 'class', 'template', 'type'
    ])
    typename_kws = set([
        'int', 'uint', 'float', 'string', 'tuple', 'array', 'function'
    ])
    kws = core_kws.union(typename_kws)
    return s in kws

def maybe_identifier_length(s):
    if is_keyword(s):
        return None
    else:
        return len(s)

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

def read_keyword(expr):
    id_chars = set(string.ascii_letters + string.digits + '_')
    id_firstchars = set(string.ascii_letters + '_')
    if len(expr) == 0 or expr[0] not in id_firstchars:
        return None
    for length in range(len(expr)):
        if expr[length] not in id_chars:
            return maybe_keyword_length(expr[:length]) if length > 0 else None

token_rules = {
    tokens.DecimalInteger:      r'[1-9][0-9]*|0',
    tokens.Float:               r'(([1-9][0-9]*|0)?[.][0-9]+(e[+-]?[0-9]+)?)|(([1-9][0-9]*|0)e[+-]?([0-9]+))',
    tokens.Whitespace:          r'[ \t]',
    tokens.Newline:             r'\r?\n',
    tokens.Identifier:          read_identifier,
    tokens.Operator:            r'[+*/%-]|\|\||\&\&|\!=|==|\>=|\<=|-\>|\<|\>|\!',
    tokens.Parenthesis:         r'[()]',
    tokens.Comma:               r',',
    tokens.Keyword:             read_keyword,
}


ignored_tokens = [tokens.Whitespace]

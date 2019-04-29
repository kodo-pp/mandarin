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


import re

import lark


Token = lark.lexer.Token
Lexer = lark.lexer.Lexer

class MandarinLexer(Lexer):
    def __init__(self, conf):
        self.terminals = [
            (terminal.name, re.compile(terminal.pattern.to_regexp()), terminal.priority)
            for terminal in conf.tokens
        ]
        self.ignores = set(conf.ignore)

    def lex(self, data):
        offset = 0
        line = 1
        col = 1
        n = len(data)
        while offset < n:
            matches = []
            for name, regex, prio in self.terminals:
                match = regex.match(data, pos=offset)
                if match is None:
                    continue
                matches.append((prio, match.group(0), name))
            if len(matches) == 0:
                raise lark.lexer.UnexpectedCharacters(
                    seq      = data,
                    lex_pos  = offset,
                    line     = line,
                    column   = col,
                    allowed  = None,
                    state    = self.state,
                )
            matches.sort(key = lambda x: (-x[0], -len(x[1])))
            max_match = matches[0]
            max_matches = [x for x in matches if (x[0], len(x[1])) == (max_match[0], len(max_match[1]))]
            if len(max_matches) > 1:
                if self.allow_ambiguous_tokens:
                    used_match = max_match
                else:
                    s = 'Ambiguous characters at line {}, col {}\nMax matches:'.format(line, col)
                    for mm in max_matches:
                        s += '\n    {}'.format(repr(mm))
                    raise lark.lexer.LexError(s)
            else:
                used_match = max_match

            _, used_match_str, used_match_name = used_match
            if used_match_name not in self.ignores:
                yield Token(
                    type_         = used_match_name,
                    value         = used_match_str,
                    pos_in_stream = offset,
                    line          = line,
                    column        = col, 
                )

    allow_ambiguous_tokens = False


class AmbiguousMandarinLexer(MandarinLexer):
    allow_ambiguous_tokens = True

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


class StringMatcher:
    def __init__(self, ls):
        self.ls = ls
    
    def longest(self, s):
        max_length = 0
        max_string = None
        for i in self.ls:
            if len(i) > max_length and s.startswith(i):
                max_length = len(i)
                max_string = i
        return max_string

    def longest_len(self, s):
        longest = self.longest(s)
        return None if longest is None else len(longest)


def list_starts_with(ls, sub):
    if len(ls) < len(sub):
        return False
    for i, j in zip(ls, sub):
        if i != j:
            return False
    return True


class ListMatcher:
    def __init__(self, ls):
        self.ls = ls
    
    def longest(self, s):
        max_length = 0
        max_string = None
        for i in self.ls:
            if len(i) > max_length and list_starts_with(s, i):
                max_length = len(i)
                max_string = i
        return max_string

    def longest_len(self, s):
        longest = self.longest(s)
        return None if longest is None else len(longest)

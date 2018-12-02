# -*- coding: utf-8 -*-


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

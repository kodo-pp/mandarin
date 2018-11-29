# -*- coding: utf-8 -*-
class Factory:
    def __init__(self, type, *args, **kwargs):
        self.type = type
        self.args = args
        self.kwargs = kwargs

    def __call__(self):
        return self.type(*self.args, **self.kwargs)

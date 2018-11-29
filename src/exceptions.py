# -*- coding: utf-8 -*-

class MandarinSyntaxError(RuntimeError):
    def __init__(self, text):
        self.text = text

    def __repr__(self):
        return 'MandarinSyntaxError: ' + repr(self.text)

    def __str__(self):
        return str(self.text)

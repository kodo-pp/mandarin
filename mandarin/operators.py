# This file (operators.py, NOT operators.py.in) is auto-generated.ArithmeticError
# Do not edit it as your changes will be overwritten.
# Edit gen/operators.txt instead

class Operator(object):
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def __getattr__(self, attr):
        return self.kwargs[attr]

OPERATORS = {
'*': Operator(data='*', priority=1000),
'/': Operator(data='/', priority=1000),
'%': Operator(data='%', priority=1000),
'//': Operator(data='//', priority=1000),
'+': Operator(data='+', priority=500),
'-': Operator(data='-', priority=500),
'...': Operator(data='...', priority=200),
'..': Operator(data='..', priority=200),
'==': Operator(data='==', priority=100),
'<=': Operator(data='<=', priority=100),
'>=': Operator(data='>=', priority=100),
'!=': Operator(data='!=', priority=100),
'<': Operator(data='<', priority=100),
'>': Operator(data='>', priority=100),
'&&': Operator(data='&&', priority=30),
'||': Operator(data='||', priority=20),
'++': Operator(data='++', priority=20)
}
# vim: set syntax=python:

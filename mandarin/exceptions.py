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


from .format import Formatter
from .posinfo import Posinfo


class MandarinError(Exception):
    """ Base class for exceptions raised by compiler """

    def __init__(self, message):
        super().__init__(message)

    def __str__(self):
        tab = Formatter.get_colortab()
        return f'{tab["desc"].format(self.description)}:\n    {super().__str__()}'

    description = 'Unknown error'


class UsageError(MandarinError):
    """ Class representing error in command-line usage of `mandarin` tool """
    description = 'Usage error'


class CodeError(MandarinError):
    """ Base class for errors connected with code """

    def __init__(self, message, posinfo):
        super().__init__(message)
        self.posinfo = posinfo

    def __str__(self):
        return f'[at {self.posinfo.format(color=True)}]:\n  {super().__str__()}'

    description = 'Unknown error in code'


class InternalError(CodeError):
    """ Internal error which occured while processing the code """
    
    def __init__(self, posinfo, message):
        msg = f'{message}. This is a bug in compiler, not your program'
        super().__init__(posinfo=posinfo, message=msg)


class MandarinSyntaxError(CodeError):
    """ Represents syntax error in a source file """
    description = 'Syntax error'


class SemanticalError(CodeError):
    """ Class representing semantical (type mismatch, duplicate declaration,
    etc. error in code.
    """
    description = 'Unknown semantical error'


class TypeMismatchError(SemanticalError):
    description = 'Type mismatch'


class DuplicateVariableDeclaration(SemanticalError):
    def __init__(self, posinfo, name):
        msg = f'Variable `{name}` is already declared'
        super().__init__(posinfo=posinfo, message=msg)
        self.name = name

    description = 'Duplicate variable declaration'


class FunctionArgumentsCountError(SemanticalError):
    def __init__(self, posinfo, count, expected, function, args):
        msg = f'Function takes exactly {expected} argument(s) but {count} was(were) provided'
        super().__init__(posinfo=posinfo, message=msg)
        self.function = function
        self.args = args

    description = 'Invalid number of arguments'


class UndeclaredVariable(SemanticalError):
    def __init__(self, posinfo, name):
        msg = f'Variable `{name}` is not declared'
        super().__init__(posinfo=posinfo, message=msg)
        self.name = name

    description = 'Undeclared variable'


class InvalidDefaultConstructorUsed(SemanticalError):
    def __init__(self, posinfo, varname, typename):
        msg = f'Default constructor for variable `{varname}` of type `{typename}` is not defined'
        super().__init__(posinfo=posinfo, message=msg)
        self.varname = varname
        self.typename = typename

    description = 'Inexistent default constructor used'


class IntegerOutOfBounds(SemanticalError):
    def __init__(self, posinfo, value):
        msg = f'Integer {value} is either too large or too small for the native integer type'
        super().__init__(posinfo=posinfo, message=msg)
        self.value = value
    
    description = 'Literal value out of bounds'


class InvalidImplicitDeclaration(SemanticalError):
    def __init__(self, posinfo):
        msg = f'Implicit declaration of a non-local variable via assignment is not allowed'
        super().__init__(posinfo=posinfo, message=msg)

    description = 'Invalid variable declaration'


class ImportNameConflictError(SemanticalError):
    def __init__(self, posinfo, name):
        msg = f'Imported name `{name}` conflicts with already present one'
        super().__init__(posinfo=posinfo, message=msg)

    description = 'Import name conflict'


def warn(w, formatter):
    # STUB!
    formatter.print_compile_error(w, warning=True)

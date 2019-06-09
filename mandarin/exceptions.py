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


from .posinfo import Posinfo


class MandarinError(Exception):
    """ Base class for exceptions raised by compiler """

    def __init__(self, message):
        super().__init__(message)

    def __str__(self):
        return f'{self.description}: {super().__str__()}'

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
        return f'[at {str(self.posinfo)}]: {super().__str__()}'

    description = 'Unknown error in code'


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
    def __init__(self, name, posinfo):
        msg = f'Variable `{name}` is already declared'
        super().__init__(posinfo=posinfo, message=msg)
        self.name = name

    description = 'Duplicate variable declaration'

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

import abc
from typing import List

from . import analyzer as an
from . import exceptions as exc
from . import targets


class Generator(object):
    def __init__(self, analyzer, options):
        self.analyzer = analyzer
        self.class_defs     = list(self.analyzer.get_class_definitions())
        self.function_decls = list(self.analyzer.get_function_declarations())
        self.function_defs  = list(self.analyzer.get_function_definitions())
        self.options = options

    def generate(self):
        buf = []

        class_defs     = self.class_defs
        function_decls = self.function_decls
        function_defs  = self.function_defs

        buf += self.generate_prologue()
        buf += self.generate_visual_separator()

        buf += self.generate_class_declarations   (class_defs, function_decls, function_defs)
        buf += self.generate_visual_separator()

        buf += self.generate_function_declarations(class_defs, function_decls, function_defs)
        buf += self.generate_visual_separator()

        buf += self.generate_class_definitions    (class_defs, function_decls, function_defs)
        buf += self.generate_visual_separator()

        buf += self.generate_function_definitions (class_defs, function_decls, function_defs)
        buf += self.generate_visual_separator()

        buf += self.generate_epilogue()
        return ''.join(buf)

    def generate_visual_separator(self) -> List[str]:
        return []

    @abc.abstractmethod
    def generate_prologue(self) -> List[str]:
        return []

    @abc.abstractmethod
    def generate_epilogue(self) -> List[str]:
        return []
    
    @abc.abstractmethod
    def generate_class_declarations(
        self,
        class_defs:     List[an.ClassDefinition],
        function_decls: List[an.FunctionDeclaration],
        function_defs:  List[an.FunctionDefiniton],
    ) -> List[str]:
        return []
    
    @abc.abstractmethod
    def generate_function_declarations(
        self,
        class_defs:     List[an.ClassDefinition],
        function_decls: List[an.FunctionDeclaration],
        function_defs:  List[an.FunctionDefiniton],
    ) -> List[str]:
        return []
    
    @abc.abstractmethod
    def generate_class_definitions(
        self,
        class_defs:     List[an.ClassDefinition],
        function_decls: List[an.FunctionDeclaration],
        function_defs:  List[an.FunctionDefiniton],
    ) -> List[str]:
        return []
    
    @abc.abstractmethod
    def generate_function_definitions(
        self,
        class_defs:     List[an.ClassDefinition],
        function_decls: List[an.FunctionDeclaration],
        function_defs:  List[an.FunctionDefiniton],
    ) -> List[str]:
        return []


class Indenter(object):
    def __init__(self, indent_string):
        self.indent_string = indent_string

    def get_indentation(self):
        return self.indent_string

    def indent(self, buf):
        code = ''.join(buf)
        lines = code.split('\n')
        indented_lines = [(self.get_indentation() if len(line) > 0 else '') + line for line in lines]
        return '\n'.join(indented_lines)


class Context(object):
    class VariableAlreadyExists(Exception):
        def __init__(self, name):
            self.name = name

        def __str__(self):
            return f'Variable `{self.name}` already exists'

    class Frame(object):
        __slots__ = ['variables']

        def __init__(self):
            self.variables = {}

        def maybe_add_variable(self, name, var):
            if self.has_variable(name):
                return False
            self.variables[name] = var
            return True

        def has_variable(self, name):
            return self.maybe_get_variable(name) is not None

        def add_variable(self, name, var):
            if not self.maybe_add_variable(name, var):
                raise Context.VariableAlreadyExists(name)

        def maybe_get_variable(self, name):
            return self.variables.get(name, None)

        def get_variable(self, name):
            maybe_var = self.maybe_get_variable(name)
            if maybe_var is None:
                raise KeyError(name)
            return maybe_var


    class PushHolder(object):
        __slots__ = ['parent']

        def __init__(self, parent):
            self.parent = parent

        def __enter__(self):
            self.parent.raw_push()
        
        def __exit__(self, *args):
            self.parent.raw_pop()


    class StackEmptyError(Exception):
        def __init__(self):
            super().__init__()

        def __str__(self):
            return '`Context` object: stack is empty but a frame was requested'


    __slots__ = ['function', 'stack']

    def __init__(self):
        self.function = None
        self.stack = []

    def maybe_add_variable(self, name, var):
        if len(self.stack) == 0:
            raise Context.StackEmptyError()
        return self.stack[-1].maybe_add_variable(name, var)

    def add_variable(self, name, var):
        if not self.maybe_add_variable(name, var):
            raise Context.VariableAlreadyExists(name)

    def maybe_get_variable(self, name):
        for frame in reversed(self.stack):
            maybe_var = frame.maybe_get_variable(name)
            if maybe_var is not None:
                return maybe_var
        return None

    def get_variable(self, name):
        maybe_var = self.maybe_get_variable(name)
        if maybe_var is None:
            raise KeyError(name)
        return maybe_var

    def has_variable(self, name):
        return self.maybe_get_variable(name) is not None

    def raw_push(self):
        self.stack.append(Context.Frame())

    def raw_pop(self):
        self.stack.pop()

    def push(self):
        return self.PushHolder(parent=self)


class CxxGenerator(Generator):
    __slots__ = ['indenter', 'context']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.indenter = Indenter(' ' * 4)
        self.context = Context()

    def generate_visual_separator(self):
        return ['\n']

    def generate_prologue(self):
        return [
            '/* This file was auto-generated by Mandarin compiler */\n',
            '#include <csetjmp>\n',
            '#include <cstddef>\n',
            '#include <cstdint>\n',
            '#include <memory>\n',
            'namespace mandarin {namespace user {\n',
        ]

    def generate_epilogue(self):
        common_epilogue = [
            '}} /* namespace mandarin::user */\n',
        ]
        standalone_epilogue = [
            'int main(int argc, char** argv) {\n',
            '    mandarin::support::preinit();\n',
            '    mandarin::support::store_args(argc, argv);\n',
            '    auto scoped_init = mandarin::support::init();\n',
            '    mandarin::user::mndr_main();\n',
            '    return 0;\n',
            '}\n',
        ] if self.options['is_standalone'] else []
        return common_epilogue + standalone_epilogue

    def generate_class_definitions(self, class_defs, function_decls, function_defs):
        buf = []
        for cd in class_defs:
            buf += self.generate_class_definition(cd)
        return buf

    def generate_class_definition(self, cd):
        name = cd.name
        outer_buf = []
        outer_buf.append('class mndr_{} : public mandarin::support::Shared {{\n'.format(name))
        outer_buf.append('public:\n')
        buf = []
        for md in cd.method_decls:
            buf += self.generate_method_declaration(md, cd)
        for member in cd.members:
            typename = self.canonicalize_type(member.type);
            buf.append(f'    {typename} mndr_{member.name.split(".")[-1]};\n')
        outer_buf += buf
        outer_buf.append('};\n')
        return outer_buf

    def generate_method_declaration(self, md, cd):
        method_name = md.name
        has_typename, canonical_method_name = self.canonicalize_method_name(method_name, cd)
        buf = []
        if has_typename:
            return_type = md.return_type
            canonical_return_type = self.canonicalize_type(return_type)
            buf.append(f'    virtual {canonical_return_type} mndr_{canonical_method_name}(')
        else:
            buf.append(f'    virtual void mndr_{canonical_method_name}(')
        buf += self.generate_function_arguments(md)
        buf.append(');\n');
        return buf

    def canonicalize_method_name(self, method_name, cd):
        raw_name = method_name.split('.')[-1]
        if raw_name == 'new':
            return False, 'new'
        elif raw_name == 'del':
            return False, 'del'
        else:
            return True, raw_name

    def canonicalize_type(self, typename):
        if typename.name == 'var':
            return 'mandarin::support::SharedDynamicObject'
        else:
            return 'mandarin::user::mndr_' + typename.name

    def generate_function_arguments(self, fd):
        argument_strings = [
            f'{self.canonicalize_type(arg.type)} mndr_{arg.name}'
            for arg in fd.arguments
        ]
        return [', '.join(argument_strings)]

    def generate_function_declarations(self, class_defs, function_decls, function_defs):
        buf = []
        for fd in function_decls:
            if '.' in fd.name:
                continue
            buf += self.generate_function_declaration(fd)
        return buf

    def generate_function_declaration(self, fd):
        function_name = fd.name
        buf = []
        return_type = fd.return_type
        canonical_return_type = self.canonicalize_type(return_type)
        buf.append(f'{canonical_return_type} mndr_{function_name}(')
        buf += self.generate_function_arguments(fd)
        buf.append(');\n');
        return buf

    def generate_class_declarations(self, class_defs, function_decls, function_defs):
        return [f'class mndr_{cd.name};\n' for cd in class_defs]

    def generate_function_definitions(self, class_defs, function_decls, function_defs):
        return sum(
            [self.generate_function_definition(fd,) for fd in function_defs],
            [],
        )

    def generate_function_definition(self, fd):
        function_name = fd.decl.name
        buf = []
        return_type = fd.decl.return_type
        canonical_return_type = self.canonicalize_type(return_type)
        buf.append(f'{canonical_return_type} mndr_{function_name}(')
        buf += self.generate_function_arguments(fd.decl)
        buf.append(') {\n');
        buf += self.generate_code_block(fd.body)
        buf.append('}\n');
        return buf

    def generate_code_block(self, block):
        with self.context.push():
            buf = []
            for statement in block:
                buf += self.generate_code_statement(statement)
            return self.indenter.indent(buf)

    def generate_code_statement(self, stmt):
        methods = [
            (an.Expression,             lambda e: self.generate_expression(e) + [';\n']),
            (an.VariableAssignment,     self.generate_variable_assignment),
            (an.VariableDeclaration,    self.generate_variable_declaration),
        ]

        for Type, method in methods:
            if isinstance(stmt, Type):
                return method(stmt)
        #raise exc.InternalError(posinfo=stmt.posinfo, message=f'Unknown statement class: {Type.__name__}')
        return [f'/* Unimplemented (stub) statement type "{type(stmt)}" */\n']

    def generate_expression(self, expr):
        methods = [
            (an.BinaryOperatorExpression,   self.generate_binop_expression),
            (an.FunctionCallExpression,     self.generate_function_call_expression),
            (an.IdentifierExpression,       self.generate_identifier_expression),
            (an.LiteralExpression,          self.generate_literal_expression),
            (an.PropertyExpression,         self.generate_property_expression),
            (an.UnaryOperatorExpression,    self.generate_unop_expression),
        ]
        for Type, method in methods:
            if isinstance(expr, Type):
                return method(expr)
        raise exc.InternalError(posinfo=expr.posinfo, message=f'Unknown expression class: {Type.__name__}')

    def generate_binop_expression(self, expr):
        return ['/* Expression (stub) [binary operator] */']

    def generate_function_call_expression(self, expr):
        return ['/* Expression (stub) [function call] */']

    def generate_identifier_expression(self, expr):
        return ['/* Expression (stub) [identifier] */']

    def generate_literal_expression(self, expr):
        return ['/* Expression (stub) [literal] */']

    def generate_property_expression(self, expr):
        return ['/* Expression (stub) [property] */']

    def generate_unop_expression(self, expr):
        emulated, canon = self.canonicalize_unary_operator(expr.op)
        if emulated:
            return [f'mandarin::support::unop_{canon}({expr.arg})']
        return [f'{canon}({"".join(self.generate_expression(expr.arg))})']

    def canonicalize_unary_operator(self, op):
        if op in ['+', '-', '!', '~']:
            return False, op
        assert False, f'Encountered unknown unary operator `op`'

    def generate_variable_assignment(self, stmt):
        maybe_var = self.context.maybe_get_variable(stmt.name)
        if maybe_var is None:
            # Combined assignment + declaration with implicit type inference
            # (like `x = 5` with no `x` declared earlier)
            # No assignment operator but `=` is permitted
            if stmt.operator != '=':
                # All other operators make it assignment-only statement, not a combined decl+assign one
                raise exc.UndeclaredVariable(posinfo=stmt.posinfo, name=stmt.name)
            typename = self.canonicalize_type(stmt.expr.get_type())
            self.context.add_variable(
                name = stmt.name,
                var = an.VariableDeclaration(
                    posinfo = stmt.posinfo,
                    name = stmt.name,
                    type = typename,
                    init_value = stmt.expr,
                ),
            )
            return [f'{typename} mndr_{stmt.name} = {"".join(self.generate_expression(stmt.expr))};\n']
        # XXX: STUB!
        if stmt.operator != '=':
            raise NotImplementedError('Assignment operators other than `=` are not yet implemented')
        return [f'mndr_{stmt.name} = {"".join(self.generate_expression(stmt.expr))};\n']

    def generate_variable_declaration(self, decl):
        name = decl.name
        typename = self.canonicalize_type(decl.type)
        try:
            self.context.add_variable(name=decl.name, var=decl)
        except Context.VariableAlreadyExists as e:
            raise exc.DuplicateVariableDeclaration(posinfo=decl.posinfo, name=name) from e
        if decl.init_value is None:
            if not self.is_default_constructible(decl.type):
                raise exc.InvalidDefaultConstructorUsed(
                    posinfo = decl.posinfo,
                    varname = name,
                    typename = decl.type,
                )
            return [f'{typename} mndr_{name};\n']
        return [f'{typename} mndr_{name} = {"".join(self.generate_expression(decl.init_value))};\n']

    def is_default_constructible(self, typename):
        # XXX: STUB!
        return True


targets.targets.append(targets.Target(
    name            = 'cxx',
    GeneratorType   = CxxGenerator,
    description     = 'Built-in C++ target',
))

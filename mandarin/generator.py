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
import copy
from typing import List, Optional, Set, Tuple

from . import analyzer as an
from . import exceptions as exc
from . import targets


from typeguard import typechecked


class Generator(object):
    @typechecked
    def __init__(self, analyzer: an.Analyzer, options: dict, formatter):
        self.class_defs     = list(analyzer.get_class_definitions())
        self.function_decls = list(analyzer.get_function_declarations())
        self.function_defs  = list(analyzer.get_function_definitions())
        self.options = options
        self.names: Set[str] = set()
        self.context = Context()
        self.formatter = formatter
        for i in self.class_defs:
            self.add_name(i.name)
        for i in self.function_decls:
            self.add_name(i.name)

        for i in self.class_defs:
            var = an.VariableDeclaration(posinfo=i.posinfo, name=i.name, type=an.Typename('@Type'))
            self.context.add_variable(i.name, var)
        for i in self.function_decls:
            var = an.VariableDeclaration(posinfo=i.posinfo, name=i.name, type=an.Typename('@Function'))
            self.context.add_variable(i.name, var)

    @typechecked
    def import_analyzer(self, analyzer: an.Analyzer, scope: Optional[str] = None, posinfo: Optional[str] = None):
        class_defs     = list(analyzer.get_class_definitions())
        function_decls = list(analyzer.get_function_declarations())
        function_defs  = list(analyzer.get_function_definitions()) 

        if scope is None:
            for i in class_defs:
                self.add_name(i.name)
            for i in function_decls:
                self.add_name(i.name)
        else:
            self.add_name(scope)

        class_defs     = self.scopify(scope, class_defs)
        function_decls = self.scopify(scope, function_decls)
        function_defs  = self.scopify(scope, function_defs)

        self.class_defs     += class_defs
        self.function_decls += function_decls
        self.function_defs  += function_defs

        for i in class_defs:
            var = an.VariableDeclaration(posinfo=i.posinfo, name=i.name, type=an.Typename('@Type'))
            self.context.add_variable(i.name, var)
        for i in function_decls:
            var = an.VariableDeclaration(posinfo=i.posinfo, name=i.name, type=an.Typename('@Function'))
            self.context.add_variable(i.name, var)

    @staticmethod
    @typechecked
    def scopify(scope: Optional[str], objects: list) -> list:
        if scope is None:
            return objects
        def gen():
            for i in objects:
                x = copy.copy(i)
                x.name = '{}.{}'.format(scope, i.name)
                yield x
        return list(gen())

    @typechecked
    def add_name(self, name: str, posinfo=None):
        if self.is_special_identifier(name):
            raise exc.SpecialIdentifierDeclared(posinfo=posinfo, name=name)
        if name in self.names:
            raise exc.ImportNameConflictError(posinfo=posinfo, name=name)

    @typechecked
    def is_special_identifier(self, name: str) -> bool:
        return name in ['self', 'true', 'false', 'none', 'var']

    @typechecked
    def generate(self) -> str:
        buf: List[str] = []

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

    @typechecked
    def generate_visual_separator(self) -> List[str]:
        return []

    @typechecked
    @abc.abstractmethod
    def generate_prologue(self) -> List[str]:
        return []

    @typechecked
    @abc.abstractmethod
    def generate_epilogue(self) -> List[str]:
        return []
    
    @typechecked
    @abc.abstractmethod
    def generate_class_declarations(
        self,
        class_defs:     List[an.ClassDefinition],
        function_decls: List[an.FunctionDeclaration],
        function_defs:  List[an.FunctionDefiniton],
    ) -> List[str]:
        return []
    
    @typechecked
    @abc.abstractmethod
    def generate_function_declarations(
        self,
        class_defs:     List[an.ClassDefinition],
        function_decls: List[an.FunctionDeclaration],
        function_defs:  List[an.FunctionDefiniton],
    ) -> List[str]:
        return []
    
    @typechecked
    @abc.abstractmethod
    def generate_class_definitions(
        self,
        class_defs:     List[an.ClassDefinition],
        function_decls: List[an.FunctionDeclaration],
        function_defs:  List[an.FunctionDefiniton],
    ) -> List[str]:
        return []
    
    @typechecked
    @abc.abstractmethod
    def generate_function_definitions(
        self,
        class_defs:     List[an.ClassDefinition],
        function_decls: List[an.FunctionDeclaration],
        function_defs:  List[an.FunctionDefiniton],
    ) -> List[str]:
        return []


class Indenter(object):
    @typechecked
    def __init__(self, indent_string: str):
        self.indent_string = indent_string

    @typechecked
    def get_indentation(self) -> str:
        return self.indent_string

    @typechecked
    def indent(self, buf: List[str]) -> List[str]:
        code = ''.join(buf)
        lines = code.split('\n')
        indented_lines = [(self.get_indentation() if len(line) > 0 else '') + line + '\n' for line in lines]
        if indented_lines:
            indented_lines[-1] = indented_lines[-1][:-1]    # remove last newline
        #return '\n'.join(indented_lines)
        return indented_lines


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

        @typechecked
        def maybe_add_variable(self, name: str, var: an.VariableDeclaration) -> bool:
            if self.has_variable(name):
                return False
            self.variables[name] = var
            return True

        @typechecked
        def has_variable(self, name: str) -> bool:
            return self.maybe_get_variable(name) is not None

        @typechecked
        def add_variable(self, name: str, var: an.VariableDeclaration):
            if not self.maybe_add_variable(name, var):
                raise Context.VariableAlreadyExists(name)

        @typechecked
        def maybe_get_variable(self, name: str) -> Optional[an.VariableDeclaration]:
            return self.variables.get(name, None)

        @typechecked
        def get_variable(self, name: str) -> an.VariableDeclaration:
            maybe_var = self.maybe_get_variable(name)
            if maybe_var is None:
                raise KeyError(name)
            return maybe_var


    class PushHolder(object):
        __slots__ = ['on_enter', 'on_exit']

        def __init__(self, on_enter, on_exit):
            self.on_enter = on_enter
            self.on_exit = on_exit

        def __enter__(self):
            self.on_enter()
        
        def __exit__(self, *args):
            self.on_exit()


    class StackEmptyError(Exception):
        def __init__(self):
            super().__init__()

        def __str__(self):
            return '`Context` object: stack is empty but a frame was requested'


    class NestedClassError(Exception):
        def __init__(self):
            super().__init__(self)

        def __str__(self):
            return '`Context` object: nested class was entered, which is not supported'


    class NoClassError(Exception):
        def __init__(self):
            super().__init__(self)

        def __str__(self):
            return '`Context` object: class exited when there was no class'


    __slots__ = ['function', 'stack', '_in_class']

    def __init__(self):
        self.function = None
        self.stack = [Context.Frame()]
        self._in_class = False
    
    def is_in_class(self):
        return self._in_class
    
    def _enter_class(self):
        if self._in_class:
            raise Context.NestedClassError()
        self._in_class = True

    def _exit_class(self):
        if not self._in_class:
            raise Context.NoClassError()
        self._in_class = False

    @typechecked
    def maybe_add_variable(self, name: str, var: an.VariableDeclaration) -> bool:
        if len(self.stack) == 0:
            raise Context.StackEmptyError()
        return self.stack[-1].maybe_add_variable(name, var)

    @typechecked
    def add_variable(self, name: str, var: an.VariableDeclaration):
        if not self.maybe_add_variable(name, var):
            raise Context.VariableAlreadyExists(name)

    @typechecked
    def maybe_get_variable(self, name: str) -> Optional[an.VariableDeclaration]:
        for frame in reversed(self.stack):
            maybe_var = frame.maybe_get_variable(name)
            if maybe_var is not None:
                return maybe_var
        return None

    @typechecked
    def get_variable(self, name: str) -> an.VariableDeclaration:
        maybe_var = self.maybe_get_variable(name)
        if maybe_var is None:
            raise KeyError(name)
        return maybe_var

    @typechecked
    def has_variable(self, name: str) -> bool:
        return self.maybe_get_variable(name) is not None

    def _raw_push(self):
        self.stack.append(Context.Frame())

    def _raw_pop(self):
        self.stack.pop()

    def push(self):
        return Context.PushHolder(on_enter=self._raw_push, on_exit=self._raw_pop)

    def push_class(self):
        return Context.PushHolder(on_enter=self._enter_class, on_exit=self._exit_class)


class CxxGenerator(Generator):
    @typechecked
    def __init__(self, *args, bits: int = 64, **kwargs):
        super().__init__(*args, **kwargs)
        self.bits = bits
        self.indenter = Indenter(' ' * 4)

    @typechecked
    def generate_visual_separator(self) -> List[str]:
        return ['\n']

    @typechecked
    def generate_prologue(self) -> List[str]:
        return [
            '/* This file was auto-generated by Mandarin compiler */\n',
            '#include <csetjmp>\n',
            '#include <cstddef>\n',
            '#include <cstdint>\n',
            '#include <memory>\n',
            '#include <mandarin.hpp>\n',
            'namespace mandarin {namespace user {\n',
        ]

    @typechecked
    def generate_epilogue(self) -> List[str]:
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

    @typechecked
    def generate_class_definitions(self, class_defs, function_decls, function_defs) -> List[str]:
        buf: List[str] = []
        for cd in class_defs:
            buf += self.generate_class_definition(cd)
        return buf

    @typechecked
    def generate_class_definition(self, cd: an.ClassDefinition) -> List[str]:
        if cd.is_native:
            return []
        name = cd.name
        with self.context.push_class():
            outer_buf = []
            outer_buf.append('class mndr_{} : public mandarin::support::Object {{\n'.format(name))
            outer_buf.append('public:\n')
            buf: List[str] = []
            for md in cd.method_decls:
                buf += self.generate_method_declaration(md, cd)
            for member in cd.members:
                typename = self.canonicalize_type(member.type, member.posinfo);
                buf.append(f'    {typename} mndr_{member.name.split(".")[-1]};\n')
            outer_buf += buf
            outer_buf.append('};\n')
            return outer_buf

    @typechecked
    def generate_method_declaration(self, md: an.FunctionDeclaration, cd: an.ClassDefinition) -> List[str]:
        method_name = md.name
        has_typename, canonical_method_name = self.canonicalize_method_name(method_name, cd)
        buf = []
        if has_typename:
            return_type = md.return_type
            canonical_return_type = self.canonicalize_type(return_type, md.posinfo)
            buf.append(f'    virtual {canonical_return_type} mndr_{canonical_method_name}(')
        else:
            buf.append(f'    virtual void mndr_{canonical_method_name}(')
        buf += self.generate_function_arguments(md)
        buf.append(');\n');
        return buf

    @typechecked
    def canonicalize_method_name(self, method_name: str, cd: an.ClassDefinition) -> Tuple[bool, str]:
        # Returns (has_typename, canonical_name)
        raw_name = method_name.split('.')[-1]
        if raw_name == 'new':
            return False, 'new'
        elif raw_name == 'del':
            return False, 'del'
        else:
            return True, raw_name

    @typechecked
    def canonicalize_type(self, typename: an.Typename, posinfo) -> str:
        if typename.name == 'var':
            return 'std::shared_ptr<mandarin::support::Object>'
        else:
            if not self.context.has_variable(typename.name):
                # STUB!
                raise exc.UndeclaredVariable(posinfo=posinfo, name=typename.name)
            return f'mandarin::shared_ptr<mandarin::user::mndr_{typename.name}>'

    @typechecked
    def generate_function_arguments(self, fd: an.FunctionDeclaration) -> List[str]:
        argument_strings = [
            f'{self.canonicalize_type(arg.type, arg.posinfo)} mndr_{arg.name}'
            for arg in fd.arguments
        ]
        return [', '.join(argument_strings)]

    @typechecked
    def generate_function_declarations(self, class_defs, function_decls, function_defs) -> List[str]:
        buf: List[str] = []
        for fd in function_decls:
            if '.' in fd.name:
                continue
            buf += self.generate_function_declaration(fd)
        return buf

    @typechecked
    def generate_function_declaration(self, fd: an.FunctionDeclaration) -> List[str]:
        function_name = fd.name
        buf = []
        return_type = fd.return_type
        canonical_return_type = self.canonicalize_type(return_type, fd.posinfo)
        buf.append(f'{canonical_return_type} mndr_{function_name}(')
        buf += self.generate_function_arguments(fd)
        buf.append(');\n');
        return buf

    @typechecked
    def generate_class_declarations(self, class_defs, function_decls, function_defs) -> List[str]:
        return [f'class mndr_{cd.name};\n' for cd in class_defs if not cd.is_native]

    @typechecked
    def generate_function_definitions(self, class_defs, function_decls, function_defs) -> List[str]:
        return sum(
            [self.generate_function_definition(fd) for fd in function_defs],
            [],
        )

    @typechecked
    def generate_function_definition(self, fd: an.FunctionDefiniton) -> List[str]:
        function_name = fd.decl.name.replace('.', '::')
        if '::' in function_name:
            ctx = self.context.push_class()
        else:
            noop = lambda: None
            ctx = Context.PushHolder(noop, noop)
        with ctx:
            buf = []
            return_type = fd.decl.return_type
            canonical_return_type = self.canonicalize_type(return_type, fd.posinfo)
            buf.append(f'{canonical_return_type} mndr_{function_name}(')
            buf += self.generate_function_arguments(fd.decl)
            with self.context.push():
                for arg in fd.decl.arguments:
                    decl = an.VariableDeclaration(
                        posinfo = arg.posinfo,
                        type = arg.type,
                        name = arg.name,
                    )
                    self.context.add_variable(arg.name, decl)
                buf.append(') {\n');
                buf += self.generate_code_block(fd.body)
                buf.append('}\n');
                return buf

    @typechecked
    def generate_code_block(self, block: List[an.Node]) -> List[str]:
        with self.context.push():
            buf: List[str] = []
            for statement in block:
                buf += self.generate_code_statement(statement)
            return self.indenter.indent(buf)

    @typechecked
    def generate_code_statement(self, stmt: an.Node) -> List[str]:
        methods = [
            (an.Expression,             lambda e: self.generate_expression(e) + [';\n']),
            (an.VariableAssignment,     self.generate_variable_assignment),
            (an.VariableDeclaration,    self.generate_variable_declaration),
            (an.IfStatement,            self.generate_if_statement),
            (an.ForLoop,                self.generate_for_loop),
            (an.WhileLoop,              self.generate_while_loop),
            (an.FunctionReturn,         self.generate_function_return),
        ]

        for Type, method in methods:
            if isinstance(stmt, Type):
                return method(stmt)
        raise exc.InternalError(posinfo=stmt.posinfo, message=f'Unknown statement class: {type(stmt).__name__}')
    
    @typechecked
    def generate_if_statement(self, stmt: an.IfStatement) -> List[str]:
        buf = ['if (mandarin::support::native_bool(']
        buf += self.generate_expression(stmt.condition)
        buf += [')) {\n']
        buf += self.generate_code_block(stmt.true_branch)
        buf += ['}']
        for cond, body in stmt.alternatives:
            buf += [' else if (mandarin::support::native_bool(']
            buf += self.generate_expression(cond)
            buf += [')) {\n']
            buf += self.generate_code_block(body)
            buf += ['}']
        if stmt.false_branch is not None:
            buf += [' else {']
            buf += self.generate_code_block(stmt.false_branch)
        buf += ['\n']
        return buf
    
    @typechecked
    def generate_for_loop(self, stmt: an.ForLoop) -> List[str]:
        buf = [f'for (auto mndriter_{stmt.variable} = (']
        buf += self.generate_expression(stmt.expression)
        buf += [')->mndr___iterator__(); ']
        buf += [f'!mandarin::support::native_bool(mndriter_{stmt.variable}->mndr___is_iteration_finished__()); ']
        buf += [f'mndriter_{stmt.variable}->mndr___inplace_next__()) {{\n']
        buf += self.indenter.indent([
            f'auto& mndr_{stmt.variable} = mndriter_{stmt.variable}->mndr___element__();\n'
        ])
        with self.context.push():
            vd = an.VariableDeclaration(
                posinfo = stmt.posinfo,
                name = stmt.variable,
                type = self.deduce_iter_element_type(stmt.expression.get_type(), lvalue=True),
            )
            self.context.add_variable(name = stmt.variable, var = vd)
            buf += self.generate_code_block(stmt.body)
        buf += '}\n'
        return buf

    @typechecked
    def deduce_iter_element_type(self, iterable_type: an.Typename, lvalue=False):
        # Stub!
        return an.Typename('var', lvalue=lvalue)
    
    @typechecked
    def generate_while_loop(self, stmt: an.WhileLoop) -> List[str]:
        buf = ['while (mandarin::support::native_bool(']
        buf += self.generate_expression(stmt.condition)
        buf += [')) {\n']
        buf += self.generate_code_block(stmt.body)
        buf += ['}\n']
        return buf
    
    @typechecked
    def generate_function_return(self, stmt: an.FunctionReturn) -> List[str]:
        return ['return '] + self.generate_expression(stmt.expr) + [';\n']

    @typechecked
    def generate_expression(self, expr: an.Expression) -> List[str]:
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

    @typechecked
    def generate_binop_expression(self, expr: an.BinaryOperatorExpression) -> List[str]:
        canon = self.canonicalize_binary_operator(expr.op)
        return (
            ['(']
            + self.generate_expression(expr.lhs)
            + [f')->{canon}(']
            + self.generate_expression(expr.rhs)
            + [')']
        )

    @typechecked
    def generate_function_call_expression(self, expr: an.FunctionCallExpression) -> List[str]:
        return [
            'mandarin::support::function_call({}{})'.format(
                ''.join(self.generate_expression(expr.func)),
                ''.join([
                    ', ' + ''.join(self.generate_expression(arg)) for arg in expr.args
                ]),
            )
        ]

    @typechecked
    def generate_identifier_expression(self, expr: an.IdentifierExpression) -> List[str]:
        if expr.name == 'self':
            if not self.context.is_in_class():
                raise exc.SelfUsedOutsideClass(posinfo=expr.posinfo)
            return ['this']
        elif expr.name in ['true', 'false', 'none']:
            return [f'mandarin::support::value_of_{expr.name}']
        elif expr.name == 'var':
            raise exc.VarUsedAsIdentifier(posinfo=expr.posinfo)

        assert not self.is_special_identifier(expr.name)
        if not self.context.has_variable(expr.name):
            raise exc.UndeclaredVariable(posinfo=expr.posinfo, name=expr.name)
        return [f'mndr_{expr.name}']

    @typechecked
    def generate_literal_expression(self, expr: an.LiteralExpression) -> List[str]:
        if isinstance(expr, an.StringExpression):
            return [
                'mandarin::support::construct<mandarin::user::mndr_Str>({})'.format(
                    self.escape_string(expr.value, expr.posinfo)
                )
            ]
        elif isinstance(expr, an.IntegerExpression):
            return [
                'mandarin::support::construct<mandarin::user::mndr_Int>({}L)'.format(
                    self.check_integer(expr.value, expr.posinfo)
                )
            ]
        else:
            raise exc.InternalError(posinfo=expr.posinfo, message=f'Unknown literal class: {type(expr).__name__}')

    @typechecked
    def escape_string(self, s: str, posinfo) -> str:
        encoded = s.encode('utf-8')
        def generate():
            yield '"'
            for b in encoded:
                if b < 32 or b >= 127:
                    # Non-printable or non-ascii
                    yield ('" "\\x{}" "').format(hex(b)[2:].zfill(2))
                else:
                    # Printable ascii
                    yield chr(b)
            yield '"'
        return ''.join(generate())

    @typechecked
    def check_integer(self, x: int, posinfo) -> int:
        values_count = 1 << self.bits
        max_value = values_count // 2 - 1
        min_value = -values_count // 2
        if x < min_value or x > max_value:
            exc.warn(exc.IntegerOutOfBounds(posinfo=posinfo, value=x), self.formatter)
        return x

    @typechecked
    def generate_property_expression(self, expr: an.PropertyExpression) -> List[str]:
        # TODO: optimize
        # No need to escape `prop`
        return ['('] + self.generate_expression(expr.obj) + [f')->_mndr_get("{expr.prop}")']

    @typechecked
    def generate_unop_expression(self, expr: an.UnaryOperatorExpression) -> List[str]:
        method = self.canonicalize_unary_operator(expr.op)
        return [f'({"".join(self.generate_expression(expr.arg))})->{method}()']

    @typechecked
    def canonicalize_unary_operator(self, op: str) -> str:
        return {
            '+': '_mndr_unary_plus',
            '-': '_mndr_unary_minus',
            '!': '_mndr_unary_negate',
            '~': '_mndr_unary_compl',
        }[op]

    @typechecked
    def canonicalize_binary_operator(self, op: str) -> str:
        return {
            '*':    '_mndr_binary_multiply',
            '/':    '_mndr_binary_divide',
            '%':    '_mndr_binary_modulo',
            '//':   '_mndr_binary_int_divide',
            '+':    '_mndr_binary_plus',
            '-':    '_mndr_binary_minus',
            '...':  '_mndr_binary_incrange',
            '..':   '_mndr_binary_range',
            '==':   '_mndr_binary_equals',
            '<=':   '_mndr_binary_less_equals',
            '>=':   '_mndr_binary_greater_equals',
            '!=':   '_mndr_binary_not_equals',
            '<':    '_mndr_binary_less',
            '>':    '_mndr_binary_greater',
            '&&':   '_mndr_binary_logical_and',
            '||':   '_mndr_binary_logical_or',
            '++':   '_mndr_binary_logical_xor',
        }[op]

    @typechecked
    def canonicalize_assignment_operator(self, op: str) -> str:
        return {
            '+=':   '_mndr_assign_plus',
            '-=':   '_mndr_assign_minus',
            '*=':   '_mndr_assign_multiply',
            '/=':   '_mndr_assign_divide',
            '//=':  '_mndr_assign_int_divide',
            '%=':   '_mndr_assign_modulo',
        }[op]

    @typechecked
    def generate_variable_assignment(self, stmt: an.VariableAssignment) -> List[str]:
        # Sorry about it, but in fact it isn't a variable assignment
        # it is just an assignment to a Lvalue expression.
        # However, assignment to a variable is a special case because it might
        # be an assignment combined with an implicit declaration
        # Somebody, please just delete this repo!
        lhs = stmt.lhs
        if not lhs.get_type().lvalue:
            raise exc.AssignmentToRvalue(posinfo=stmt.posinfo)
        if isinstance(lhs, an.IdentifierExpression):
            # lhs is variable
            name = lhs.name
            maybe_var = self.context.maybe_get_variable(name)
            if maybe_var is None:
                # Combined assignment + declaration with implicit type inference
                # (like `x = 5` with no `x` declared earlier)
                # No assignment operator but `=` is permitted
                if self.is_special_identifier(name):
                    raise exc.SpecialIdentifierDeclared(posinfo=stmt.posinfo, name=name)
                if stmt.operator != '=':
                    # All other operators make it assignment-only statement, not a combined decl+assign one
                    raise exc.UndeclaredVariable(posinfo=stmt.posinfo, name=stmt.name)
                typename = stmt.expr.get_type()
                typename_c = self.canonicalize_type(typename, stmt.expr.posinfo)
                self.context.add_variable(
                    name = name,
                    var = an.VariableDeclaration(
                        posinfo = stmt.posinfo,
                        name = name,
                        type = typename,
                        init_value = stmt.expr,
                    ),
                )
                return [
                    '{} {} = mandarin::support::cast_to<{}>({});\n'.format(
                        typename_c,
                        ''.join(self.generate_expression(lhs)),
                        typename_c,
                        ''.join(self.generate_expression(stmt.expr)),
                    )
                ]

        # XXX: STUB!
        if stmt.operator != '=':
            return [
                '({})->{}(mandarin::support::cast_to<{}>({}));\n'.format(
                    ''.join(self.generate_expression(lhs)),
                    self.canonicalize_assignment_operator(stmt.operator),
                    self.canonicalize_type(lhs.get_type(), lhs.posinfo),
                    ''.join(self.generate_expression(stmt.expr)),
                )
            ]
        return [
            '{} = mandarin::support::cast_to<{}>({});\n'.format(
                ''.join(self.generate_expression(lhs)),
                self.canonicalize_type(lhs.get_type(), lhs.posinfo),
                ''.join(self.generate_expression(stmt.expr)),
            )
        ]

    @typechecked
    def generate_variable_declaration(self, decl: an.VariableDeclaration) -> List[str]:
        name = decl.name
        if self.is_special_identifier(name):
            raise exc.SpecialIdentifierDeclared(posinfo=decl.posinfo, name=name)
        typename = self.canonicalize_type(decl.type, decl.posinfo)
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

    @typechecked
    def is_default_constructible(self, typename: an.Typename) -> bool:
        # XXX: STUB!
        return True


targets.targets.append(targets.Target(
    name            = 'cxx',
    GeneratorType   = CxxGenerator,
    description     = 'Built-in C++ target',
))

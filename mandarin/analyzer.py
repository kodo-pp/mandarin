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

from typing import Any, List, Union, Generator, Optional, Tuple

from . import exceptions as exc
from . import posinfo as pi

import lark


from typeguard import typechecked


class Node(object):
    @typechecked
    def __init__(self, posinfo: pi.Posinfo):
        self.posinfo = posinfo


class Typename(object):
    @typechecked
    def __init__(self, name: str, lvalue: bool = False):
        self.name = name
        self.lvalue = lvalue

    def __str__(self):
        return '{}{}'.format('Lvalue ' if self.lvalue else '', self.name)

    def __repr__(self):
        return 'Typename({}{})'.format('Lvalue ' if self.lvalue else '', self.name)


class Expression(Node):
    def __str__(self):
        return repr(self)

    def __repr__(self):
        return 'Expr ???'

    def get_type(self):
        raise NotImplementedError()


class FunctionArgument(Node):
    @typechecked
    def __init__(self, posinfo: pi.Posinfo, name: str, type: Typename):
        super().__init__(posinfo)
        self.name = name
        self.type = type

    def __repr__(self):
        return 'FunctionArgument(name: {}, type: {})'.format(self.name, self.type)


class FunctionDeclaration(Node):
    @typechecked
    def __init__(self, posinfo: pi.Posinfo, name: str, return_type: Typename, arguments: List[FunctionArgument]):
        super().__init__(posinfo)
        self.name = name
        self.return_type = return_type
        self.arguments = arguments

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return 'FunctionDeclaration(name: {}, returns: {}, arguments: {})'.format(
            repr(self.name),
            repr(self.return_type),
            repr(self.arguments),
        )
        

class VariableDeclaration(Node):
    @typechecked
    def __init__(self, posinfo: pi.Posinfo, type: Typename, name: str, init_value: Optional[Expression] = None):
        super().__init__(posinfo)
        self.type = type
        self.name = name
        self.init_value = init_value

    def __str__(self):
        return repr(self)
    
    def __repr__(self):
        return 'VarDeclaration(var: {}, type: {}{})'.format(
            self.name,
            repr(self.type),
            ', init: {}'.format(repr(self.init_value)) if self.init_value is not None else '',
        )


class FunctionDefiniton(Node):
    @typechecked
    def __init__(self, posinfo: pi.Posinfo, decl: FunctionDeclaration, body: List[Node]):
        super().__init__(posinfo)
        self.decl = decl
        self.body = body

    def __str__(self):
        return repr(self)
    
    def __repr__(self):
        return 'FunctionDefiniton(decl: {}, body: {})'.format(repr(self.decl), repr(self.body))


class StubExpression(Expression):
    @typechecked
    def __init__(self, posinfo: pi.Posinfo, node: Union[lark.tree.Tree, lark.lexer.Token]):
        super().__init__(posinfo)
        self.node = node

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return 'Expr <{}> stub: {}'.format(self.get_type(), self.node)

    def get_type(self):
        return Typename('var')


class IdentifierExpression(Expression):
    @typechecked
    def __init__(self, posinfo: pi.Posinfo, name: str, typename: Typename):
        super().__init__(posinfo)
        self.name = name
        self.typename = typename

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return 'Expr <{}> id: {}'.format(self.get_type(), self.name)

    def get_type(self):
        return self.typename


# TODO: move these to Analyzer
@typechecked
def deduce_type_binop(op: str, left: Typename, right: Typename) -> Typename:
    # STUB!
    return Typename('var')


@typechecked
def deduce_type_unop(op: str, argt: Typename) -> Typename:
    # STUB!
    return Typename('var')


@typechecked
def deduce_call_type(func: Expression, args: List[Expression]) -> Typename:
    # STUB!
    callable_type = func.get_type()
    if callable_type.name == 'var':
        return Typename('var')

    #if len(args) != len(func.arguments):
    #    raise exc.FunctionArgumentsCountError(
    #        posinfo = func.posinfo,
    #        count = len(args),
    #        expected = len(func.arguments),
    #        function = func,
    #        arguments = args,
    #    )
    return Typename('var')


@typechecked
def deduce_type_property(objt: Typename, prop: str) -> Typename:
    # STUB!
    is_lvalue = objt.lvalue
    return Typename('var', lvalue=is_lvalue)


class BinaryOperatorExpression(Expression):
    @typechecked
    def __init__(self, posinfo: pi.Posinfo, op: str, lhs: Expression, rhs: Expression):
        super().__init__(posinfo)
        self.op = op
        self.lhs = lhs
        self.rhs = rhs

    def __repr__(self):
        return 'Expr <{}> operator2 {} ({}, {})'.format(
            self.get_type(),
            self.op,
            repr(self.lhs),
            repr(self.rhs),
        )

    @typechecked
    def get_type(self) -> Typename:
        # TODO: move to constructor, return already computed value
        lt = self.lhs.get_type()
        rt = self.lhs.get_type()
        return deduce_type_binop(op=self.op, left=lt, right=lt)


class UnaryOperatorExpression(Expression):
    @typechecked
    def __init__(self, posinfo: pi.Posinfo, op: str, arg: Expression):
        super().__init__(posinfo)
        self.op = op
        self.arg = arg

    def __repr__(self):
        return 'Expr <{}> operator1 {} ({})'.format(
            self.get_type(),
            self.op,
            repr(self.arg),
        )

    @typechecked
    def get_type(self) -> Typename:
        # TODO: move to constructor, return already computed value
        argt = self.arg.get_type()
        return deduce_type_unop(op=self.op, argt=argt)


class PropertyExpression(Expression):
    @typechecked
    def __init__(self, posinfo: pi.Posinfo, obj: Expression, prop: str):
        super().__init__(posinfo)
        self.obj = obj
        self.prop = prop

    def __repr__(self):
        return 'Expr <{}> prop ({}) -> {}'.format(
            self.get_type(),
            repr(self.obj),
            repr(self.prop),
        )

    @typechecked
    def get_type(self) -> Typename:
        # TODO: move to constructor, return already computed value
        objt = self.obj.get_type()
        return deduce_type_property(objt=objt, prop=self.prop)


class FunctionCallExpression(Expression):
    @typechecked
    def __init__(self, posinfo: pi.Posinfo, func: Expression, args: List[Expression]):
        super().__init__(posinfo)
        self.func = func
        self.args = args

    def __repr__(self):
        return 'Expr <{}> call: {}({})'.format(
            self.get_type(),
            repr(self.func),
            ', '.join(map(repr, self.args)),
        )

    @typechecked
    def get_type(self) -> Typename:
        # TODO: move to constructor, return already computed value
        return deduce_call_type(func=self.func, args=self.args)


class LiteralExpression(Expression):
    @typechecked
    def __init__(self, posinfo: pi.Posinfo, value: Any):
        super().__init__(posinfo)
        self.value = value

    def __repr__(self):
        return 'Expr <{}> {}: {}'.format(
            self.get_type(),
            self.name,
            repr(self.value),
        )

    @typechecked
    def get_type(self) -> Typename:
        return self.typename

    typename = Typename('var')
    name = 'literal'


class StringExpression(LiteralExpression):
    typename = Typename('Str')
    name = 'str'


class IntegerExpression(LiteralExpression):
    typename = Typename('Int')
    name = 'int'


class VariableAssignment(Node):
    @typechecked
    def __init__(self, posinfo: pi.Posinfo, lhs: Expression, operator: str, expr: Expression):
        super().__init__(posinfo)
        self.lhs = lhs
        self.operator = operator
        self.expr = expr

    def __str__(self):
        return repr(self)
    
    def __repr__(self):
        return 'VarAssignment(lhs: {}, op: {}, expr: {})'.format(
            repr(self.lhs),
            repr(self.operator),
            repr(self.expr),
        )


class WhileLoop(Node):
    @typechecked
    def __init__(self, posinfo: pi.Posinfo, condition: Expression, body: List[Node]):
        super().__init__(posinfo)
        self.condition = condition
        self.body = body

    def __str__(self):
        return repr(self)
    
    def __repr__(self):
        return 'WhileLoop(cond: {}, body: {})'.format(
            repr(self.condition),
            repr(self.body),
        )


class ForLoop(Node):
    @typechecked
    def __init__(self, posinfo: pi.Posinfo, variable: str, expression: Expression, body: List[Node]):
        super().__init__(posinfo)
        self.variable = variable
        self.expression = expression
        self.body = body

    def __str__(self):
        return repr(self)
    
    def __repr__(self):
        return 'ForLoop(var: {}, expr: {}, body: {})'.format(
            repr(self.variable),
            repr(self.expression),
            repr(self.body),
        )


class IfStatement(Node):
    @typechecked
    def __init__(
        self,
        posinfo: pi.Posinfo,
        condition: Expression,
        true_branch: List[Node],
        false_branch: Optional[List[Node]],
        alternatives: List[Tuple[Expression, List[Node]]],
    ):
        super().__init__(posinfo)
        self.condition = condition
        self.true_branch = true_branch
        self.false_branch = false_branch
        self.alternatives = alternatives

    def __str__(self):
        return repr(self)
    
    def __repr__(self):
        alternatives = ', '.join(['elif {}: {}'.format(c, b) for c, b in self.alternatives])
        return 'IfStatement(if {}: {}, {}{})'.format(
            repr(self.condition),
            repr(self.true_branch),
            alternatives,
            '' if self.false_branch is None else ', else: {}'.format(repr(self.false_branch)),
        )


class FunctionReturn(Node):
    @typechecked
    def __init__(self, posinfo: pi.Posinfo, expr: Expression):
        super().__init__(posinfo)
        self.expr = expr

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return 'FunctionReturn({})'.format(self.expr)


class ClassDefinition(Node):
    @typechecked
    def __init__(
        self,
        posinfo: pi.Posinfo,
        is_native: bool,
        name: str,
        members: List[VariableDeclaration],
        method_decls: List[FunctionDeclaration],
        method_defs: List[FunctionDefiniton],
    ):
        super().__init__(posinfo)
        self.name = name
        self.members = members
        self.method_decls = method_decls
        self.method_defs = method_defs
        self.is_native = is_native
    
    def __str__(self):
        return repr(self)

    def __repr__(self):
        return 'Class{}(name: {}, members: {}, methods: (decls: {}, defs: {}))'.format(
            ' native' if self.is_native else '',
            self.name,
            [repr(x) for x in self.members],
            [repr(x) for x in self.method_decls],
            [repr(x) for x in self.method_defs],
        )


class Analyzer(object):
    @typechecked
    def __init__(self, ast: lark.tree.Tree, filename: Optional[str] = None):
        self.ast = ast
        self.filename = filename

    @typechecked
    def get_function_declarations(self) -> Generator[FunctionDeclaration, None, None]:
        for node in self.ast.children:
            if isinstance(node, lark.tree.Tree) \
                    and node.data in ['native_function_declaration', 'function_definition']:
                yield self.parse_function_declaration(node)
        for i in self.get_class_definitions():
            for mdecl in i.method_decls:
                yield mdecl

    @typechecked
    def get_function_definitions(self) -> Generator[FunctionDefiniton, None, None]:
        for node in self.ast.children:
            if isinstance(node, lark.tree.Tree) and node.data == 'function_definition':
                yield self.parse_function_definition(node)
        for i in self.get_class_definitions():
            for mdef in i.method_defs:
                yield mdef

    @typechecked
    def get_class_definitions(self) -> Generator[ClassDefinition, None, None]:
        for node in self.ast.children:
            if isinstance(node, lark.tree.Tree) and node.data == 'class_definition':
                yield self.parse_class_definition(node)

    @typechecked
    def parse_class_definition(self, node: lark.tree.Tree) -> ClassDefinition:
        # class_definition: (0) KW_CLASS (1?) KW_NATIVE? (-2) IDENTIFIER _NL (-1) class_block_end
        # class_block_end: class_statement* KW_END
        assert isinstance(node, lark.tree.Tree)
        assert node.data == 'class_definition'
        assert len(node.children) in [3, 4]

        is_native = (len(node.children) == 4)
    
        class_name = node.children[-2].value
        block = node.children[-1]
        assert isinstance(block, lark.tree.Tree)
        assert block.data.startswith('class_block')
        assert len(block.children) >= 1

        members = []
        mdecls = []
        mdefs = []
        for stmt_node in block.children[:-1]:
            stmt = self.parse_class_statement(stmt_node, prefix=f'{class_name}.')
            if isinstance(stmt, FunctionDeclaration):
                mdecls.append(stmt)
            elif isinstance(stmt, FunctionDefiniton):
                mdefs.append(stmt)
                mdecls.append(stmt.decl)
            elif isinstance(stmt, VariableDeclaration):
                members.append(stmt)
            else:
                assert False, f'Unknown class statement type: {type(stmt)}'

        return ClassDefinition(
            posinfo = pi.from_lark(filename=self.filename, node=node),
            is_native = is_native,
            name = class_name,
            members = members,
            method_decls = mdecls,
            method_defs = mdefs,
        )

    @typechecked
    def parse_class_statement(self, node: lark.tree.Tree, prefix: str) -> Union[
        FunctionDeclaration, FunctionDefiniton, VariableDeclaration
    ]:
        assert isinstance(node, lark.tree.Tree)
        assert node.data in {'function_definition', 'native_function_declaration', 'var_declaration'}
        if node.data == 'native_function_declaration':
            return self.parse_function_declaration(node, prefix=prefix)
        elif node.data == 'function_definition':
            return self.parse_function_definition(node, prefix=prefix)
        else:
            # node.data == 'var_declaration'
            return self.parse_var_declaration(node, prefix=prefix)

    @typechecked
    def parse_function_definition(self, node: lark.tree.Tree, *, prefix: str = '') -> FunctionDefiniton:
        # function_definition: (0) KW_DEF (1) IDENTIFIER "(" (2) typed_arglist ")" (x) _NL (3) code_block_end
        # typed_arglist: (typed_arg ("," typed_arg)* ","?)?
        # typed_arg: typename? IDENTIFIER
        # code_block_end: code_statement* KW_END
        assert isinstance(node, lark.tree.Tree)
        assert len(node.children) == 4

        name = node.children[1].value
        arglist = node.children[2]
        arguments = list(self.parse_typed_arglist(arglist))
        code = node.children[3]
        body = self.parse_code_block(code)
        return_type = Typename('var') # STUB

        posinfo = pi.from_lark(filename=self.filename, node=node)
        decl = FunctionDeclaration(
            posinfo = posinfo,
            name = prefix+name,
            return_type = return_type,
            arguments = arguments,
        )
        return FunctionDefiniton(posinfo=posinfo, decl=decl, body=body)
    
    @typechecked
    def parse_code_block(self, cb_node: lark.tree.Tree) -> List[Node]:
        # code_block_<***>: code_statement* KW_<***>
        # <***> in [end, else, elif]
        assert isinstance(cb_node, lark.tree.Tree)
        assert cb_node.data in ['code_block_end', 'code_block_elif', 'code_block_else']
        assert len(cb_node.children) >= 1
        end_keyword = cb_node.children[-1]
        assert isinstance(end_keyword, lark.lexer.Token)
        assert end_keyword.type == {
            'code_block_end': 'KW_END',
            'code_block_elif': 'KW_ELIF',
            'code_block_else': 'KW_ELSE',
        }[cb_node.data]

        statements = cb_node.children[:-1]
        return [self.parse_code_statement(st) for st in statements]

    @typechecked
    def parse_code_statement(self, statement: lark.tree.Tree) -> Node:
        # ?code_statement: (expression
        #     | var_declaration
        #     | var_assignment
        #     | if_statement
        #     | for_statement
        #     | while_statement) _NL
        assert isinstance(statement, lark.tree.Tree)
        if statement.data == 'var_declaration':
            return self.parse_var_declaration(statement)
        elif statement.data == 'var_assignment':
            return self.parse_var_assignment(statement)
        elif statement.data == 'if_statement':
            return self.parse_if_statement(statement)
        elif statement.data == 'for_statement':
            return self.parse_for_statement(statement)
        elif statement.data == 'while_statement':
            return self.parse_while_statement(statement)
        elif statement.data == 'expression':
            return self.parse_expression(statement)
        elif statement.data == 'return_statement':
            return self.parse_return(statement)
        else:
            raise exc.InternalError('Unknown code statement: {}'.format(statement.data))
            
    @typechecked
    def parse_return(self, statement: lark.tree.Tree) -> FunctionReturn:
        # return_statement: KW_RETURN expression
        assert isinstance(statement, lark.tree.Tree)
        assert len(statement.children) == 2

        return FunctionReturn(
            posinfo = pi.from_lark(filename=self.filename, node=statement),
            expr = self.parse_expression(statement.children[1]),
        )

    @typechecked
    def parse_var_declaration(self, node: lark.tree.Tree, *, prefix: str = '') -> VariableDeclaration:
        # var_declaration: typename IDENTIFIER (strict_assignment_op expression)?
        assert isinstance(node, lark.tree.Tree)
        type = self.parse_typename(node.children[0])
        name = node.children[1].value
        value = None
        if len(node.children) > 2:
            assert len(node.children) == 4
            value = self.parse_expression(node.children[3])
        return VariableDeclaration(
            posinfo = pi.from_lark(filename=self.filename, node=node),
            type = type,
            name = prefix + name,
            init_value = value,
        )

    @typechecked
    def parse_var_assignment(self, node: lark.tree.Tree) -> VariableAssignment:
        # var_assignment: front_atomic_expression assignment_op expression
        assert isinstance(node, lark.tree.Tree)
        assert len(node.children) == 3
        lhs = self.parse_expression(node.children[0])
        operator = self.parse_operator(node.children[1])
        expr = self.parse_expression(node.children[2])
        if not lhs.get_type().lvalue:
            line = node.children[1].line
            column = node.children[1].column
            posinfo = pi.Posinfo(filename=self.filename, line=line, column=column)
            raise exc.TypeMismatchError('At variable assignment: left-hand side is not a lvalue', posinfo)
        return VariableAssignment(
            posinfo = pi.from_lark(filename=self.filename, node=node),
            lhs = lhs,
            operator = operator,
            expr = expr,
        )

    @typechecked
    def parse_operator(self, node: lark.tree.Tree) -> str:
        assert isinstance(node, lark.tree.Tree)
        assert all([isinstance(x, lark.lexer.Token) for x in node.children]) or len(node.children) == 1
        if len(node.children) == 1 and isinstance(node.children[0], lark.tree.Tree):
            return self.parse_operator(node.children[0])
        return ''.join([x.value for x in node.children])

    @typechecked
    def parse_if_statement(self, node: lark.tree.Tree) -> IfStatement:
        # if_statement: KW_IF expression _NL (code_block_elif expression _NL)* ...
        # ... (code_block_else _NL)? code_block_end
        assert isinstance(node, lark.tree.Tree)
        main_condition = self.parse_expression(node.children[1])
        true_branch = self.parse_code_block(node.children[2])
        alternatives = []       # (condition, body) tuples
        false_branch = None

        nodes = node.children
        i = 3
        while i < len(nodes) and nodes[i-1].data == 'code_block_elif':
        #while i < len(nodes):
            assert i + 1 < len(nodes)
            cond = self.parse_expression(nodes[i])
            body = self.parse_code_block(nodes[i+1])
            alternatives.append((cond, body))
            #if nodes[i+1].data == 'code_block_else':
            #    break
            i += 2
        if i < len(nodes):
            #if nodes[i-1].data == 'code_block_else':
            assert nodes[i-1].data == 'code_block_else'
            false_branch = self.parse_code_block(nodes[i])
            #assert i + 3 == len(nodes)
        
        return IfStatement(
            posinfo = pi.from_lark(filename=self.filename, node=node),
            condition = main_condition,
            true_branch = true_branch,
            false_branch = false_branch,
            alternatives = alternatives,
        )

    @typechecked
    def parse_for_statement(self, node: lark.tree.Tree) -> ForLoop:
        # for_statement: KW_FOR IDENTIFIER KW_IN expression _NL code_block_end
        assert isinstance(node, lark.tree.Tree)
        assert len(node.children) == 5
        var = node.children[1].value
        expr = node.children[3]
        cb = node.children[4]
        return ForLoop(
            posinfo = pi.from_lark(filename=self.filename, node=node),
            variable = var,
            expression = self.parse_expression(expr),
            body = self.parse_code_block(cb),
        )
            
    @typechecked
    def parse_while_statement(self, node: lark.tree.Tree) -> WhileLoop:
        # while_statement: KW_WHILE expression _NL code_block_end
        assert isinstance(node, lark.tree.Tree)
        assert len(node.children) == 3
        expr = node.children[1]
        cb = node.children[2]
        return WhileLoop(
            posinfo = pi.from_lark(filename=self.filename, node=node),
            condition = self.parse_expression(expr),
            body = self.parse_code_block(cb),
        )
            
    @typechecked
    def parse_expression(self, node: lark.tree.Tree) -> Expression:
        assert isinstance(node, lark.tree.Tree)
        if node.data == 'expression' or node.data == 'expression_nl':
            assert len(node.children) == 1
            return self.parse_expression(node.children[0])
        if node.data.endswith('atomic_expression'):
            return self.parse_atomic_expression(node)
        assert node.data == 'binary_operator_node'
        op = node.op
        lhs = self.parse_expression(node.lhs)
        rhs = self.parse_expression(node.rhs)
        return BinaryOperatorExpression(
            posinfo = pi.from_lark(filename=self.filename, node=node),
            op = op,
            lhs = lhs,
            rhs = rhs,
        )

    @typechecked
    def parse_atomic_expression(self, node: lark.tree.Tree) -> Expression:
        # FIXME: loops on old_tests/parser/006-unary-operators.man
        assert isinstance(node, lark.tree.Tree)
        assert node.data == 'front_atomic_expression'
        atom = self.parse_pure_atomic_expression(node.children[-1])
        for unop in node.children[::-1][1:]:
            atom = UnaryOperatorExpression(
                posinfo = pi.from_lark(filename=self.filename, node=unop),
                op = self.parse_operator(unop),
                arg = atom,
            )
        return atom

    @typechecked
    def parse_pure_atomic_expression(self, node: lark.tree.Tree) -> Expression:
        # ?atomic_expression: [1] literal | [2] symbol | [3] "(" expression ")" | [4] function_call | [5] property
        assert isinstance(node, lark.tree.Tree)
        if node.data == 'literal':
            # [1]
            return self.parse_literal(node)
        elif node.data == 'symbol':
            # [2]
            return self.get_variable(node.children[0])
        elif node.data.startswith('expression'):
            # [3]
            return self.parse_expression(node)
        elif node.data == 'function_call':
            # [4]
            return self.parse_function_call(node)
        else:
            assert node.data == 'property'
            return self.parse_property(node)

    @typechecked
    def parse_property(self, node: lark.tree.Tree) -> PropertyExpression:
        assert isinstance(node, lark.tree.Tree)
        assert len(node.children) == 3
        obj = self.parse_pure_atomic_expression(node.children[0])
        prop = node.children[2].value
        return PropertyExpression(
            posinfo = pi.from_lark(filename=self.filename, node=node),
            obj = obj,
            prop = prop,
        )

    @typechecked
    def parse_literal(self, node: lark.tree.Tree) -> LiteralExpression:
        # literal: NUMBER | STRING_SINGLE | STRING_DOUBLE
        assert isinstance(node, lark.tree.Tree)
        assert len(node.children) == 1
        assert isinstance(node.children[0], lark.lexer.Token)
        lit = node.children[0]
        if lit.type == 'NUMBER':
            # TODO: floats
            return IntegerExpression(
                posinfo = pi.from_lark(filename=self.filename, node=node),
                value = int(lit.value),
            )
        elif lit.type in ['STRING_SINGLE', 'STRING_DOUBLE']:
            return StringExpression(
                posinfo = pi.from_lark(filename=self.filename, node=node),
                value = self.unescape_string(lit.value),
            )
        else:
            assert False, 'Unknown literal type: {}'.format(lit.type)

    @typechecked
    def unescape_string(self, string: str) -> str:
        # STUB!
        def gen():
            s = string[1:-1]
            for i in range(len(s)):
                if s[i] == '\\':
                    if i + 1 >= len(s):
                        yield s[i]
                        continue
                    c = s[i+1]
                    if c in 'ntrv0\\':
                        yield {'n':'\n', 'r':'\r', 't':'\t', 'v':'\v', '0':'\0', '\\':'\\'}[c]
                else:
                    yield s[i]
        return ''.join(gen())

    @typechecked
    def parse_function_call(self, node: lark.tree.Tree) -> FunctionCallExpression:
        # function_call: atomic_expression call_operator
        assert isinstance(node, lark.tree.Tree)
        assert node.data == 'function_call'
        assert len(node.children) == 2
        functor = self.parse_pure_atomic_expression(node.children[0])
        args = self.parse_call_operator(node.children[1])
        return FunctionCallExpression(
            posinfo = pi.from_lark(filename=self.filename, node=node),
            func = functor,
            args = args,
        )

    @typechecked
    def parse_call_operator(self, node: lark.tree.Tree) -> List[Expression]:
        # call_operator: "(" (expression ("," expression)*)? ")"
        assert isinstance(node, lark.tree.Tree)
        assert node.data == 'call_operator'
        return [self.parse_expression(x) for x in node.children]

    @typechecked
    def get_variable(self, var_token: lark.lexer.Token) -> IdentifierExpression:
        assert isinstance(var_token, lark.lexer.Token)
        assert var_token.type == 'IDENTIFIER'
        return IdentifierExpression(
            posinfo = pi.from_lark(filename=self.filename, node=var_token),
            name = var_token.value,
            typename = Typename('var', lvalue=True),
        )

    @typechecked
    def parse_function_declaration(self, node: lark.tree.Tree, *, prefix: str = '') -> FunctionDeclaration:
        # native_function_declaration: (0) KW_DEF (1) KW_NATIVE (2) IDENTIFIER "(" (3) typed_arglist ")"
        # typed_arglist: (typed_arg ("," typed_arg)* ","?)?
        # typed_arg: typename? IDENTIFIER
        assert isinstance(node, lark.tree.Tree)
        assert len(node.children) == 4
        is_native = self.is_native(node)

        id_node = node.children[2 if is_native else 1]
        assert isinstance(id_node, lark.lexer.Token)
        assert id_node.type == 'IDENTIFIER'
        name = id_node.value
        arglist = node.children[3 if is_native else 2]
        arguments = list(self.parse_typed_arglist(arglist))
        return_type = Typename('var') # STUB
        return FunctionDeclaration(
            posinfo = pi.from_lark(filename=self.filename, node=node),
            name = prefix + name,
            return_type = return_type,
            arguments = arguments,
        )

    @typechecked
    def is_native(self, node: lark.tree.Tree) -> bool:
        return isinstance(node.children[1], lark.lexer.Token) and node.children[1].type == 'KW_NATIVE'

    @typechecked
    def parse_typed_arglist(self, arglist: lark.tree.Tree) -> Generator[FunctionArgument, None, None]:
        assert isinstance(arglist, lark.tree.Tree)
        for argnode in arglist.children:
            if isinstance(argnode, lark.tree.Tree) and argnode.data.startswith('typed_arg'):
                if len(argnode.children) == 1:
                    # no typename
                    name, type = argnode.children[-1].value, Typename('var')
                else:
                    # with typename
                    name, type = argnode.children[-1].value, self.parse_typename(argnode.children[0])
                yield FunctionArgument(
                    posinfo = pi.from_lark(filename=self.filename, node=argnode),
                    name = name,
                    type = type,
                )
    
    @typechecked
    def parse_typename(self, node: lark.tree.Tree) -> Typename:
        assert isinstance(node, lark.tree.Tree)
        assert node.data == 'typename'
        assert len(node.children) == 1
        id_node = node.children[0]
        assert isinstance(id_node, lark.lexer.Token)
        assert id_node.type == 'IDENTIFIER'
        return Typename(id_node.value)

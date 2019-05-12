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


import lark


class Typename(object):
    def __init__(self, name, lvalue=False):
        self.name = name
        self.lvalue = lvalue

    def __str__(self):
        return self.name

    def __repr__(self):
        return 'Typename({}{})'.format('Lvalue ' if self.lvalue else '', self.name)


class FunctionArgument(object):
    def __init__(self, name, type):
        self.name = name
        self.type = type

    def __repr__(self):
        return 'FunctionArgument(name: {}, type: {})'.format(self.name, self.type)


class FunctionDeclaration(object):
    def __init__(self, name, return_type, arguments):
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


class FunctionDefiniton(object):
    def __init__(self, decl, body):
        self.decl = decl
        self.body = body

    def __str__(self):
        return repr(self)
    
    def __repr__(self):
        return 'FunctionDefiniton(decl: {}, body: {})'.format(repr(self.decl), repr(self.body))


class Expression(object):
    def __str__(self):
        return repr(self)

    def __repr__(self):
        return 'Expr ???'

    def get_type(self):
        raise NotImplementedError()


class StubExpression(Expression):
    def __init__(self, node):
        self.node = node

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return 'Expr <{}> stub: {}'.format(self.get_type(), self.node)

    def get_type(self):
        return Typename('var')


# TODO: move these to Analyzer
def deduce_type_binop(op, left, right):
    # STUB!
    return Typename('var')


def deduce_type_unop(op, argt):
    # STUB!
    return Typename('var')


def deduce_call_type(func, args):
    # STUB!
    return Typename('var')


class BinaryOperatorExpression(Expression):
    def __init__(self, op, lhs, rhs):
        self.op = op
        self.lhs = lhs
        self.rhs = rhs

    def __repr__(self):
        return 'Expr <{}> operator2 {} ({}, {})'.format(
            self.get_type().name,
            self.op,
            repr(self.lhs),
            repr(self.rhs),
        )

    def get_type(self):
        # TODO: move to constructor, return already computed value
        lt = self.lhs.get_type()
        rt = self.lhs.get_type()
        return deduce_type_binop(op=self.op, left=lt, right=lt)


class UnaryOperatorExpression(Expression):
    def __init__(self, op, arg):
        self.op = op
        self.arg = arg

    def __repr__(self):
        return 'Expr <{}> operator1 {} ({})'.format(
            self.get_type().name,
            self.op,
            repr(self.arg),
        )

    def get_type(self):
        # TODO: move to constructor, return already computed value
        argt = self.arg.get_type()
        return deduce_type_unop(op=self.op, argt=argt)


class FunctionCallExpression(Expression):
    def __init__(self, func, args):
        self.func = func
        self.args = args

    def __repr__(self):
        return 'Expr <{}> call: {}({})'.format(
            self.get_type().name,
            repr(self.func),
            ', '.join(map(repr, self.args)),
        )

    def get_type(self):
        # TODO: move to constructor, return already computed value
        return deduce_call_type(func=self.func, args=self.args)


class LiteralExpression(Expression):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return 'Expr <{}> {}: {}'.format(
            self.get_type().name,
            self.name,
            repr(self.value),
        )

    def get_type(self):
        return self.typename

    typename = Typename('var')
    name = 'literal'


class StringExpression(LiteralExpression):
    typename = Typename('Str')
    name = 'str'


class IntegerExpression(LiteralExpression):
    typename = Typename('Int')
    name = 'int'


class VariableAssignment(object):
    def __init__(self, varspec, operator, expr):
        self.varspec = varspec
        self.operator = operator
        self.expr = expr

    def __str__(self):
        return repr(self)
    
    def __repr__(self):
        return 'VarAssignment(var: {}, op: {}, expr: {})'.format(
            repr(self.varspec),
            repr(self.operator),
            repr(self.expr),
        )
        

class VariableDeclaration(object):
    def __init__(self, type, name, init_value=None):
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


class WhileLoop(object):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

    def __str__(self):
        return repr(self)
    
    def __repr__(self):
        return 'WhileLoop(cond: {}, body: {})'.format(
            repr(self.condition),
            repr(self.body),
        )


class ForLoop(object):
    def __init__(self, variable, expression, body):
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


class IfStatement(object):
    def __init__(self, condition, true_branch, false_branch, alternatives):
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


class Analyzer(object):
    def __init__(self, ast):
        self.ast = ast

    def get_function_declarations(self):
        for node in self.ast.children:
            if isinstance(node, lark.tree.Tree) \
                    and node.data in ['native_function_declaration', 'function_definition']:
                yield self.parse_function_declaration(node)

    def get_function_definitions(self):
        for node in self.ast.children:
            if isinstance(node, lark.tree.Tree) and node.data == 'function_definition':
                yield self.parse_function_definition(node)

    def parse_function_definition(self, node):
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
        decl = FunctionDeclaration(name=name, return_type=return_type, arguments=arguments)
        return FunctionDefiniton(decl=decl, body=body)
    
    def parse_code_block(self, cb_node):
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

    def parse_code_statement(self, statement):
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
        else:
            assert False, 'Unknown code statement: {}'.format(statement.data)
            
    def parse_var_declaration(self, node):
        # var_declaration: typename IDENTIFIER (strict_assignment_op expression)?
        assert isinstance(node, lark.tree.Tree)
        type = self.parse_typename(node.children[0])
        name = node.children[1].value
        value = None
        if len(node.children) > 2:
            assert len(node.children) == 4
            value = self.parse_expression(node.children[3])
        return VariableDeclaration(type=type, name=name, init_value=value)
            
    def parse_var_assignment(self, node):
        # var_assignment: front_atomic_expression assignment_op expression
        assert isinstance(node, lark.tree.Tree)
        assert len(node.children) == 3
        varspec = self.parse_expression(node.children[0])
        operator = self.parse_operator(node.children[1])
        expr = self.parse_expression(node.children[2])
        return VariableAssignment(varspec=varspec, operator=operator, expr=expr)

    def parse_operator(self, node):
        assert isinstance(node, lark.tree.Tree)
        assert all([isinstance(x, lark.lexer.Token) for x in node.children]) or len(node.children) == 1
        if len(node.children) == 1 and isinstance(node.children[0], lark.tree.Tree):
            return self.parse_operator(node.children[0])
        return ''.join([x.value for x in node.children])

    def parse_if_statement(self, node):
        # if_statement: KW_IF expression _NL (code_block_elif expression _NL)* ...
        # ... (code_block_else _NL)? code_block_end
        assert isinstance(node, lark.tree.Tree)
        main_condition = self.parse_expression(node.children[1])
        true_branch = self.parse_code_block(node.children[2])
        alternatives = []       # (condition, body) tuples
        false_branch = None

        nodes = node.children
        i = 3
        while i < len(nodes):
            assert i + 1 < len(nodes)
            cond = self.parse_expression(nodes[i])
            body = self.parse_code_block(nodes[i+1])
            alternatives.append((cond, body))
            if nodes[i+1].data == 'code_block_else':
                break
            i += 2
        if i < len(nodes):
            if nodes[i+1].data == 'code_block_else':
                false_branch = self.parse_code_block(nodes[i+2])
            assert i + 3 == len(nodes)
        
        return IfStatement(
            condition=main_condition,
            true_branch=true_branch,
            false_branch=false_branch,
            alternatives=alternatives,
        )

    def parse_for_statement(self, node):
        # for_statement: KW_FOR IDENTIFIER KW_IN expression _NL code_block_end
        assert isinstance(node, lark.tree.Tree)
        assert len(node.children) == 5
        var = node.children[1].value
        expr = self.parse_expression(node.children[3])
        cb = self.parse_code_block(node.children[4])
        return ForLoop(variable=var, expression=expr, body=cb)
            
    def parse_while_statement(self, node):
        # while_statement: KW_WHILE expression _NL code_block_end
        assert isinstance(node, lark.tree.Tree)
        assert len(node.children) == 3
        expr = node.children[1]
        cb = node.children[2]
        return WhileLoop(condition=expr, body=cb)
            
    def parse_expression(self, node):
        assert isinstance(node, lark.tree.Tree)
        if node.data == 'expression':
            assert len(node.children) == 1
            return self.parse_expression(node.children[0])
        if node.data.endswith('atomic_expression'):
            return self.parse_atomic_expression(node)
        assert node.data == 'binary_operator_node'
        op = node.op
        lhs = self.parse_expression(node.lhs)
        rhs = self.parse_expression(node.rhs)
        return BinaryOperatorExpression(op=op, lhs=lhs, rhs=rhs)

    def parse_atomic_expression(self, node):
        # FIXME: loops on old_tests/parser/006-unary-operators.man
        assert isinstance(node, lark.tree.Tree)
        assert node.data == 'front_atomic_expression'
        atom = self.parse_pure_atomic_expression(node.children[-1])
        for unop in node.children[::-1][1:]:
            atom = UnaryOperatorExpression(op=self.parse_operator(unop), arg=atom)
        return atom

    def parse_pure_atomic_expression(self, node):
        # ?atomic_expression: [1] literal | [2] IDENTIFIER | [3] "(" expression ")" | [4] function_call
        if isinstance(node, lark.lexer.Token):
            # [2]
            assert node.type == 'IDENTIFIER'
            return self.get_variable(node.value)
        else:
            # [1,3,4]
            if node.data == 'literal':
                # [1]
                return self.parse_literal(node)
            elif node.data == 'expression':
                # [3]
                return self.parse_expression(node)
            else:
                # [4]
                assert node.data == 'function_call'
                return self.parse_function_call(node)

    def parse_literal(self, node):
        # literal: NUMBER | STRING_SINGLE | STRING_DOUBLE
        assert isinstance(node, lark.tree.Tree)
        assert len(node.children) == 1
        assert isinstance(node.children[0], lark.lexer.Token)
        lit = node.children[0]
        if lit.type == 'NUMBER':
            # TODO: floats
            return IntegerExpression(int(lit.value))
        elif lit.type in ['STRING_SINGLE', 'STRING_DOUBLE']:
            return StringExpression(self.unescape_string(lit.value))
        else:
            assert False, 'Unknown literal type: {}'.format(lit.type)

    def unescape_string(self, string):
        # STUB!
        return string

    def parse_function_call(self, node):
        # function_call: atomic_expression call_operator
        assert isinstance(node, lark.tree.Tree)
        assert node.data == 'function_call'
        assert len(node.children) == 2
        functor = self.parse_pure_atomic_expression(node.children[0])
        args = self.parse_call_operator(node.children[1])
        return FunctionCallExpression(func=functor, args=args)

    def parse_call_operator(self, node):
        # call_operator: "(" (expression ("," expression)*)? ")"
        assert isinstance(node, lark.tree.Tree)
        assert node.data == 'call_operator'
        return [self.parse_expression(x) for x in node.children]

    def get_variable(self, varname):
        # STUB!
        return StubExpression(varname)

    def parse_function_declaration(self, node):
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
        return FunctionDeclaration(name=name, return_type=return_type, arguments=arguments)

    def is_native(self, node):
        return isinstance(node.children[1], lark.lexer.Token) and node.children[1].type == 'KW_NATIVE'

    def parse_typed_arglist(self, arglist):
        assert isinstance(arglist, lark.tree.Tree)
        for argnode in arglist.children:
            if isinstance(argnode, lark.tree.Tree) and argnode.data == 'typed_arg':
                if len(argnode.children) == 1:
                    # no typename
                    name, type = argnode.children[-1].value, Typename('var')
                else:
                    # with typename
                    name, type = argnode.children[-1].value, self.parse_typename(argnode.children[0])
                yield FunctionArgument(name=name, type=type)
    
    def parse_typename(self, node):
        assert isinstance(node, lark.tree.Tree)
        assert node.data == 'typename'
        assert len(node.children) == 1
        id_node = node.children[0]
        assert isinstance(id_node, lark.lexer.Token)
        assert id_node.type == 'IDENTIFIER'
        return Typename(id_node.value)

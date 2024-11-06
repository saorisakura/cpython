#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 词法分析器
# CFG: Context-Free Grammar构建基础
from abc import ABC, abstractmethod
from typing import Union
from VM.scope import Scope
from VM.symbol_t import FunctionSymbol, VariableSymbol
from VM.type import Type
from typing import Any


class AST(ABC):
    @abstractmethod
    def accept(self, visitor, additional=None):
        pass

    @abstractmethod
    def dump(self, indent=0):
        pass


class Declaration(AST):
    def __init__(self, name):
        self.name = name

    def accept(self, visitor, additional=None):
        return visitor.visit_declaration(self)

    def dump(self, indent=0):
        print('  ' * indent + 'Declaration: ' + self.name)


class Statement(AST):
    def accept(self, visitor, additional=None):
        pass

    def dump(self, indent=0):
        pass


class BlockStatement(Statement):
    def __init__(self, statements: list, scope: Scope=None):
        self.statements = statements
        self.scope = scope

    def accept(self, visitor, additional=None):
        return visitor.visit_block_statement(self)

    def dump(self, indent=0):
        print('  ' * indent + 'BlockStatement')
        for statement in self.statements:
            statement.dump(indent + 1)


class ArrayStatement(Statement):
    def __init__(self, statements: list):
        self.statements = statements

    def accept(self, visitor, additional=None):
        return visitor.visit_array_statement(self)

    def dump(self, indent=0):
        print('  ' * indent + 'ArrayStatement')
        for statement in self.statements:
            statement.dump(indent + 1)


class Expression(AST):
    def __init__(self, the_type: Type, is_left: bool, is_constant: bool, is_temp: bool, inferred_type: Type=None):
        super().__init__()
        self.the_type = the_type
        self.is_left = is_left
        self.is_constant = is_constant
        self.is_temp = is_temp
        self.inferred_type = inferred_type

    def accept(self, visitor, additional=None):
        pass

    def dump(self, indent=0):
        pass


class ExpressionStatement(Statement):
    def __init__(self, expression: Expression):
        self.expression = expression

    def accept(self, visitor, additional=None):
        return visitor.visit_expression_statement(self)

    def dump(self, indent=0):
        print('  ' * indent + 'ExpressionStatement')
        if isinstance(self.expression, list):
            for expression in self.expression:
                expression.dump(indent + 1)
        else:
            self.expression.dump(indent + 1)


class FunctionDeclaration(Declaration):
    def __init__(self, name: str, parameters: list, body: BlockStatement, scope: Scope, symbol: FunctionSymbol, return_type: Type=None):
        self.name = name
        self.parameters = parameters
        self.body = body
        self.scope = scope
        self.symbol = symbol
        self.return_type = return_type

    def accept(self, visitor, additional=None):
        return visitor.visit_function_declaration(self)

    def dump(self, indent=0):
        print('  ' * indent + 'FunctionDeclaration: ' + self.name)
        print('  ' * (indent + 1) + 'ReturnType: ' + str(self.return_type))
        print('  ' * (indent + 1) + 'Symbol: ' + str(self.symbol))
        s = self.scope
        while s:
            print('  ' * (indent + 1) + 'Scope: ' + str(s))
            s = s.parent
        for parameter in self.parameters:
            parameter.dump(indent + 1)
        self.body.dump(indent + 1)


class Variable(Expression):
    def __init__(self, name: str, declaration: Declaration = None, symbol: VariableSymbol = None, is_left: bool = None):
        self.name = name
        self.declaration = declaration
        self.symbol = symbol
        self.is_left = is_left

    def accept(self, visitor, additional=None):
        return visitor.visit_variable(self, additional)

    def dump(self, indent=0):
        print('  ' * indent + 'Variable: ' + self.name)
        print('  ' * (indent + 1) + 'Symbol: ' + str(self.symbol))
        self.declaration.dump(indent + 1) if self.declaration else print('  ' * (indent + 1) + 'Declaration: None')


class VariableDeclaration(Declaration):
    def __init__(self, name: str, initializer: Variable=None, symbol: VariableSymbol=None, inferredType: Type=None):
        self.name = name
        self.initializer = initializer
        self.symbol = symbol
        self.inferredType = inferredType

    def accept(self, visitor, additional=None):
        return visitor.visit_variable_declaration(self, additional)

    def dump(self, indent=0):
        print('  ' * indent + 'VariableDeclaration: ' + self.name)
        self.initializer.dump(indent + 1) if self.initializer else print('  ' * (indent + 1) + 'Initializer: None')
        print('  ' * (indent + 1) + 'InferredType: ' + str(self.inferredType))
        print('  ' * (indent + 1) + 'Symbol: ' + str(self.symbol))


class Program(BlockStatement):
    def __init__(self, statements, scope: Scope, symbol: FunctionSymbol = None):
        super().__init__(statements, scope)
        self.symbol = symbol

    def accept(self, visitor, additional=None):
        return visitor.visit_program(self, additional)

    def dump(self, indent=0):
        print('  ' * indent + 'Program')
        print('  ' * (indent + 1) + 'Symbol: ' + str(self.symbol))
        for statement in self.statements:
            if isinstance(statement, list):
                for s in statement:
                    s.dump(indent + 1)
            else:
                statement.dump(indent + 1)


class IfStatement(Statement):
    def __init__(self, test: Expression, consequent: BlockStatement, alternate: BlockStatement):
        self.test = test
        self.consequent = consequent
        self.alternate = alternate

    def accept(self, visitor, additional=None):
        return visitor.visit_if_statement(self)

    def dump(self, indent=0):
        print('  ' * indent + 'IfStatement')
        self.test.dump(indent + 1)
        if self.consequent:
            self.consequent.dump(indent + 1)
        if self.alternate:
            self.alternate.dump(indent + 1)


class WhileStatement(Statement):
    def __init__(self, test: Expression, body: BlockStatement):
        self.test = test
        self.body = body

    def accept(self, visitor, additional=None):
        return visitor.visit_while_statement(self)

    def dump(self, indent=0):
        print('  ' * indent + 'WhileStatement')
        self.test.dump(indent + 1)
        self.body.dump(indent + 1)


class ForStatement(Statement):
    def __init__(self, init: AST, test: Expression, update: Expression, body: BlockStatement, scope: Scope):
        self.init = init
        self.test = test
        self.update = update
        self.body = body
        self.scope = scope

    def accept(self, visitor, additional=None):
        return visitor.visit_for_statement(self)

    def dump(self, indent=0):
        print('  ' * indent + 'ForStatement')
        self.init.dump(indent + 1)
        self.test.dump(indent + 1)
        self.update.dump(indent + 1)
        self.body.dump(indent + 1)


class BreakStatement(Statement):
    def accept(self, visitor, additional=None):
        return visitor.visit_break_statement(self)

    def dump(self, indent=0):
        print('  ' * indent + 'BreakStatement')


class ContinueStatement(Statement):

    def accept(self, visitor, additional=None):
        return visitor.visit_continue_statement(self)

    def dump(self, indent=0):
        print('  ' * indent + 'ContinueStatement')


class ReturnStatement(Statement):
    def __init__(self, argument: Expression):
        self.argument = argument

    def accept(self, visitor, additional=None):
        return visitor.visit_return_statement(self)

    def dump(self, indent=0):
        print('  ' * indent + 'ReturnStatement')
        self.argument.dump(indent + 1)


class BinaryExpression(Expression):
    def __init__(self, left: Expression, operator: str, right: Expression):
        self.left = left
        self.operator = operator
        self.right = right

    def accept(self, visitor, additional=None):
        return visitor.visit_binary_expression(self)

    def dump(self, indent=0):
        print('  ' * indent + 'BinaryExpression: ' + self.operator)
        self.left.dump(indent + 1)
        self.right.dump(indent + 1)


class CallExpression(Expression):
    def __init__(self, name: str, callee: FunctionDeclaration, arguments: list):
        self.name = name
        self.callee = callee
        self.arguments = arguments

    def accept(self, visitor, additional=None):
        return visitor.visit_call_expression(self)

    def dump(self, indent=0):
        print('  ' * indent + 'CallExpression: ' + self.name)
        if isinstance(self.callee, FunctionSymbol):
            print('  ' * (indent + 1) + 'Callee Symbol: ' + self.callee.name)
        else:
            print('  ' * (indent + 1) + 'Callee: ' + self.callee.name) if self.callee else print('  ' * (indent + 1) + 'Callee: None')
        for argument in self.arguments:
            argument.dump(indent + 1)


class String(Expression):
    def __init__(self, value: str):
        self.value = value

    def accept(self, visitor, additional=None):
        return visitor.visit_string_literal(self)

    def dump(self, indent=0):
        print('  ' * indent + 'StringLiteral: ' + self.value)


class Integer(Expression):
    def __init__(self, value: int):
        self.value = value

    def accept(self, visitor, additional=None):
        return visitor.visit_integer_literal(self)

    def dump(self, indent=0):
        print('  ' * indent + 'IntegerLiteral: ' + str(self.value))


class Decimal(Expression):
    def __init__(self, value: float):
        self.value = value

    def accept(self, visitor, additional=None):
        return visitor.visit_decimal_literal(self)

    def dump(self, indent=0):
        print('  ' * indent + 'DecimalLiteral: ' + str(self.value))


class Boolean(Expression):
    def __init__(self, value: bool):
        self.value = value

    def accept(self, visitor, additional=None):
        return visitor.visit_boolean_literal(self)

    def dump(self, indent=0):
        print('  ' * indent + 'BooleanLiteral: ' + str(self.value))


class Null(Expression):
    def accept(self, visitor, additional=None):
        return visitor.visit_null_literal(self)

    def dump(self, indent=0):
        print('  ' * indent + 'NullLiteral')


class Assignment(Expression):
    def __init__(self, left: Variable, right: Expression):
        self.left = left
        self.right = right

    def accept(self, visitor, additional=None):
        return visitor.visit_assignment_expression(self)

    def dump(self, indent=0):
        print('  ' * indent + 'AssignmentExpression')
        self.left.dump(indent + 1)
        self.right.dump(indent + 1)


class LogicalOr(BinaryExpression):
    def accept(self, visitor, additional=None):
        return visitor.visit_logical_or_expression(self)

    def dump(self, indent=0):
        print('  ' * indent + 'LogicalOrExpression')
        self.left.dump(indent + 1)
        self.right.dump(indent + 1)


class LogicalAnd(BinaryExpression):
    def accept(self, visitor, additional=None):
        return visitor.visit_logical_and_expression(self)

    def dump(self, indent=0):
        print('  ' * indent + 'LogicalAndExpression')
        self.left.dump(indent + 1)
        self.right.dump(indent + 1)


class BitwiseOr(BinaryExpression):
    def accept(self, visitor, additional=None):
        return visitor.visit_bitwise_or_expression(self)

    def dump(self, indent=0):
        print('  ' * indent + 'BitwiseOrExpression')
        self.left.dump(indent + 1)
        self.right.dump(indent + 1)


class BitwiseAnd(BinaryExpression):
    def accept(self, visitor, additional=None):
        return visitor.visit_bitwise_and_expression(self)

    def dump(self, indent=0):
        print('  ' * indent + 'BitwiseAndExpression')
        self.left.dump(indent + 1)
        self.right.dump(indent + 1)


class BitwiseXor(BinaryExpression):
    def accept(self, visitor, additional=None):
        return visitor.visit_bitwise_xor_expression(self)

    def dump(self, indent=0):
        print('  ' * indent + 'BitwiseXorExpression')
        self.left.dump(indent + 1)
        self.right.dump(indent + 1)


class BitwiseNot(Expression):
    def __init__(self, expression: Expression):
        self.expression = expression

    def accept(self, visitor, additional=None):
        return visitor.visit_bitwise_not_expression(self)

    def dump(self, indent=0):
        print('  ' * indent + 'BitwiseNotExpression')
        self.expression.dump(indent + 1)


class Equal(BinaryExpression):
    def accept(self, visitor, additional=None):
        return visitor.visit_equality_expression(self)

    def dump(self, indent=0):
        print('  ' * indent + 'EqualityExpression')
        self.left.dump(indent + 1)
        self.right.dump(indent + 1)


class NotEqual(BinaryExpression):
    def accept(self, visitor, additional=None):
        return visitor.visit_equality_expression(self)

    def dump(self, indent=0):
        print('  ' * indent + 'NotEqualExpression')
        self.left.dump(indent + 1)
        self.right.dump(indent + 1)


class Less(BinaryExpression):
    def accept(self, visitor, additional=None):
        return visitor.visit_relational_expression(self)

    def dump(self, indent=0):
        print('  ' * indent + 'LessExpression')
        self.left.dump(indent + 1)
        self.right.dump(indent + 1)


class Greater(BinaryExpression):
    def accept(self, visitor, additional=None):
        return visitor.visit_relational_expression(self)

    def dump(self, indent=0):
        print('  ' * indent + 'GreaterExpression')
        self.left.dump(indent + 1)
        self.right.dump(indent + 1)


class LessEqual(BinaryExpression):
    def accept(self, visitor, additional=None):
        return visitor.visit_relational_expression(self)

    def dump(self, indent=0):
        print('  ' * indent + 'LessEqualExpression')
        self.left.dump(indent + 1)
        self.right.dump(indent + 1)


class GreaterEqual(BinaryExpression):
    def accept(self, visitor, additional=None):
        return visitor.visit_relational_expression(self)

    def dump(self, indent=0):
        print('  ' * indent + 'GreaterEqualExpression')
        self.left.dump(indent + 1)
        self.right.dump(indent + 1)


class Add(BinaryExpression):
    def accept(self, visitor, additional=None):
        return visitor.visit_additive_expression(self)

    def dump(self, indent=0):
        print('  ' * indent + 'AdditiveExpression')
        self.left.dump(indent + 1)
        self.right.dump(indent + 1)


class Subtract(BinaryExpression):
    def accept(self, visitor, additional=None):
        return visitor.visit_additive_expression(self)

    def dump(self, indent=0):
        print('  ' * indent + 'SubtractExpression')
        self.left.dump(indent + 1)
        self.right.dump(indent + 1)


class Multiply(BinaryExpression):
    def accept(self, visitor, additional=None):
        return visitor.visit_multiplicative_expression(self)

    def dump(self, indent=0):
        print('  ' * indent + 'MultiplicativeExpression')
        self.left.dump(indent + 1)
        self.right.dump(indent + 1)


class Divide(BinaryExpression):
    def accept(self, visitor, additional=None):
        return visitor.visit_multiplicative_expression(self)

    def dump(self, indent=0):
        print('  ' * indent + 'DivideExpression')
        self.left.dump(indent + 1)
        self.right.dump(indent + 1)


class Modulo(BinaryExpression):
    def accept(self, visitor, additional=None):
        return visitor.visit_multiplicative_expression(self)

    def dump(self, indent=0):
        print('  ' * indent + 'ModuloExpression')
        self.left.dump(indent + 1)
        self.right.dump(indent + 1)


class Positive(Expression):
    def __init__(self, expression: Expression):
        self.expression = expression

    def accept(self, visitor, additional=None):
        return visitor.visit_unary_expression(self)

    def dump(self, indent=0):
        print('  ' * indent + 'PositiveExpression')
        self.expression.dump(indent + 1)


class Negative(Expression):
    def __init__(self, expression: Expression):
        self.expression = expression

    def accept(self, visitor, additional=None):
        return visitor.visit_unary_expression(self)

    def dump(self, indent=0):
        print('  ' * indent + 'NegativeExpression')
        self.expression.dump(indent + 1)


class Not(Expression):

    def __init__(self, expression: Expression):
        self.expression = expression

    def accept(self, visitor, additional=None):
        return visitor.visit_unary_expression(self)

    def dump(self, indent=0):
        print('  ' * indent + 'NotExpression')
        self.expression.dump(indent + 1)


# 对AST做遍历的Vistor
# 这是一个基类，定义了缺省的遍历方式。子类可以覆盖某些方法，修改遍历方式。
class AstVisitor:
    def visit(self, node: AST, additional=None) -> Any:
        return node.accept(self, additional) if node and isinstance(node, AST) else None

    def visit_program(self, node: Program, additional=None) -> Any:
        # Program是BlockStatement的子类，所以直接调用BlockStatement的visit方法
        return self.visit_block_statement(node, additional)

    def visit_block_statement(self, node: BlockStatement, additional=None) -> Any:
        ret = None
        for statement in node.statements:
            ret = self.visit(statement, additional)
        return ret

    def visit_variable_declaration(self, node: VariableDeclaration, additional=None) -> Any:
        return self.visit(node.initializer, additional)

    def visit_function_declaration(self, node: FunctionDeclaration, additional=None) -> Any:
        for parameter in node.parameters:
            self.visit(parameter, additional)
        return self.visit(node.body, additional)

    def visit_expression_statement(self, node: ExpressionStatement, additional=None) -> Any:
        return self.visit(node.expression, additional)

    def visit_return_statement(self, node: ReturnStatement, additional=None) -> Any:
        return self.visit(node.argument, additional)

    def visit_if_statement(self, node: IfStatement, additional=None) -> Any:
        self.visit(node.test, additional)
        self.visit(node.consequent, additional)
        self.visit(node.alternate, additional) if node.alternate else None
        return None

    def visit_while_statement(self, node: WhileStatement, additional=None) -> Any:
        self.visit(node.test, additional)
        return self.visit(node.body, additional)

    def visit_for_statement(self, node: ForStatement, additional=None) -> Any:
        self.visit(node.init, additional) if node.init else None
        self.visit(node.test, additional) if node.test else None
        self.visit(node.update, additional) if node.update else None
        return self.visit(node.body, additional)

    def visit_break_statement(self, node: BreakStatement, additional=None) -> Any:
        return None

    def visit_continue_statement(self, node: ContinueStatement, additional=None) -> Any:
        return None

    def visit_binary_expression(self, node: BinaryExpression, additional=None) -> Any:
        self.visit(node.left, additional)
        return self.visit(node.right, additional)

    def visit_integer_literal(self, node: Integer, additional=None) -> Any:
        return node.value

    def visit_decimal_literal(self, node: Decimal, additional=None) -> Any:
        return node.value

    def visit_string_literal(self, node: String, additional=None) -> Any:
        return node.value

    def visit_boolean_literal(self, node: Boolean, additional=None) -> Any:
        return node.value

    def visit_null_literal(self, node: Null, additional=None) -> Any:
        return None

    def visit_variable(self, node: Variable, additional=None) -> Any:
        print("variable name -> ", node.name)
        print("variable declaration -> ", node.declaration)
        print("variable symbol -> ", node.symbol)
        print("variable is_left -> ", node.is_left)
        return None

    def visit_logical_or_expression(self, node: LogicalOr, additional=None) -> Any:
        self.visit(node.left, additional)
        return self.visit(node.right, additional)

    def visit_logical_and_expression(self, node: LogicalAnd, additional=None) -> Any:
        self.visit(node.left, additional)
        return self.visit(node.right, additional)

    def visit_bitwise_or_expression(self, node: BitwiseOr, additional=None) -> Any:
        self.visit(node.left, additional)
        return self.visit(node.right, additional)

    def visit_bitwise_and_expression(self, node: BitwiseAnd, additional=None) -> Any:
        self.visit(node.left, additional)
        return self.visit(node.right, additional)

    def visit_bitwise_xor_expression(self, node: BitwiseXor, additional=None) -> Any:
        self.visit(node.left, additional)
        return self.visit(node.right, additional)

    def visit_bitwise_not_expression(self, node: BitwiseNot, additional=None) -> Any:
        return self.visit(node.expression, additional)

    def visit_equality_expression(self, node: Union[Equal, NotEqual], additional=None) -> Any:
        self.visit(node.left, additional)
        return self.visit(node.right, additional)

    def visit_relational_expression(self, node: Union[Less, Greater, LessEqual, GreaterEqual], additional=None) -> Any:
        self.visit(node.left, additional)
        return self.visit(node.right, additional)

    def visit_additive_expression(self, node: Union[Add, Subtract], additional=None) -> Any:
        self.visit(node.left, additional)
        return self.visit(node.right, additional)

    def visit_multiplicative_expression(self, node: Union[Multiply, Divide, Modulo], additional=None) -> Any:
        self.visit(node.left, additional)
        return self.visit(node.right, additional)

    def visit_unary_expression(self, node: Union[Positive, Negative, Not], additional=None) -> Any:
        return self.visit(node.expression, additional)

    def visit_assignment_expression(self, node: Assignment, additional=None) -> Any:
        self.visit(node.left, additional)
        return self.visit(node.right, additional)

    def visit_call_expression(self, node: CallExpression, additional=None) -> Any:
        for argument in node.arguments:
            self.visit(argument, additional)
        return self.visit(node.callee, additional)

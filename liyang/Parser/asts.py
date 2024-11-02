#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 词法分析器
# CFG: Context-Free Grammar构建基础
from abc import ABC, abstractmethod
from typing import Union

class AST(ABC):
    @abstractmethod
    def accept(self, visitor):
        pass

    @abstractmethod
    def dump(self, indent=0):
        pass


class Declaration(AST):
    def __init__(self, name):
        self.name = name

    def accept(self, visitor):
        return visitor.visit_declaration(self)

    def dump(self, indent=0):
        print('  ' * indent + 'Declaration: ' + self.name)


class Statement(AST):
    def accept(self, visitor):
        pass

    def dump(self, indent=0):
        pass


class BlockStatement(Statement):
    def __init__(self, statements):
        self.statements = statements

    def accept(self, visitor):
        return visitor.visit_block_statement(self)

    def dump(self, indent=0):
        for statement in self.statements:
            statement.dump(indent + 1)


class Expression(AST):
    def accept(self, visitor):
        pass

    def dump(self, indent=0):
        pass


class ExpressionStatement(Statement):
    def __init__(self, expression: Expression):
        self.expression = expression

    def accept(self, visitor):
        return visitor.visit_expression_statement(self)

    def dump(self, indent=0):
        print('  ' * indent + 'ExpressionStatement')
        self.expression.dump(indent + 1)


class FunctionDeclaration(Declaration):
    def __init__(self, name: str, parameters: list, body: list):
        self.name = name
        self.parameters = parameters
        self.body = body

    def accept(self, visitor):
        return visitor.visit_function_declaration(self)

    def dump(self, indent=0):
        print('  ' * indent + 'FunctionDeclaration: ' + self.name)
        for parameter in self.parameters:
            print('  ' * (indent + 1) + 'Parameter: ' + parameter)
        for statement in self.body:
            statement.dump(indent + 1)


class VariableDeclaration(Declaration):
    def __init__(self, name: str, initializer: AST):
        self.name = name
        self.initializer = initializer

    def accept(self, visitor):
        return visitor.visit_variable_declaration(self)

    def dump(self, indent=0):
        print('  ' * indent + 'VariableDeclaration: ' + self.name)
        self.initializer.dump(indent + 1)


class Program(BlockStatement):
    def __init__(self, statements):
        self.statements = statements

    def accept(self, visitor):
        return visitor.visit_program(self)

    def dump(self, indent=0):
        print('  ' * indent + 'Program')
        for statement in self.statements:
            statement.dump(indent + 1)


class IfStatement(Statement):
    def __init__(self, test: Expression, consequent: BlockStatement, alternate: BlockStatement):
        self.test = test
        self.consequent = consequent
        self.alternate = alternate

    def accept(self, visitor):
        return visitor.visit_if_statement(self)

    def dump(self, indent=0):
        print('  ' * indent + 'IfStatement')
        self.test.dump(indent + 1)
        self.consequent.dump(indent + 1)
        self.alternate.dump(indent + 1)


class WhileStatement(Statement):
    def __init__(self, test: Expression, body: BlockStatement):
        self.test = test
        self.body = body

    def accept(self, visitor):
        return visitor.visit_while_statement(self)

    def dump(self, indent=0):
        print('  ' * indent + 'WhileStatement')
        self.test.dump(indent + 1)
        self.body.dump(indent + 1)


class ForStatement(Statement):
    def __init__(self, init: AST, test: Expression, update: AST, body: BlockStatement):
        self.init = init
        self.test = test
        self.update = update
        self.body = body

    def accept(self, visitor):
        return visitor.visit_for_statement(self)

    def dump(self, indent=0):
        print('  ' * indent + 'ForStatement')
        self.init.dump(indent + 1)
        self.test.dump(indent + 1)
        self.update.dump(indent + 1)
        self.body.dump(indent + 1)


class BreakStatement(Statement):
    def accept(self, visitor):
        return visitor.visit_break_statement(self)

    def dump(self, indent=0):
        print('  ' * indent + 'BreakStatement')


class ContinueStatement(Statement):

    def accept(self, visitor):
        return visitor.visit_continue_statement(self)

    def dump(self, indent=0):
        print('  ' * indent + 'ContinueStatement')


class ReturnStatement(Statement):
    def __init__(self, argument: Expression):
        self.argument = argument

    def accept(self, visitor):
        return visitor.visit_return_statement(self)

    def dump(self, indent=0):
        print('  ' * indent + 'ReturnStatement')
        self.argument.dump(indent + 1)


class BinaryExpression(Expression):
    def __init__(self, left: Expression, operator: str, right: Expression):
        self.left = left
        self.operator = operator
        self.right = right

    def accept(self, visitor):
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

    def accept(self, visitor):
        return visitor.visit_call_expression(self)

    def dump(self, indent=0):
        print('  ' * indent + 'CallExpression: ' + self.name)
        for argument in self.arguments:
            argument.dump(indent + 1)


class Variable(Expression):
    def __init__(self, name: str, declaration: Declaration):
        self.name = name
        self.declaration = declaration

    def accept(self, visitor):
        return visitor.visit_variable(self)

    def dump(self, indent=0):
        print('  ' * indent + 'Variable: ' + self.name)


class String(Expression):
    def __init__(self, value: str):
        self.value = value

    def accept(self, visitor):
        return visitor.visit_string_literal(self)

    def dump(self, indent=0):
        print('  ' * indent + 'StringLiteral: ' + self.value)


class Integer(Expression):
    def __init__(self, value: int):
        self.value = value

    def accept(self, visitor):
        return visitor.visit_integer_literal(self)

    def dump(self, indent=0):
        print('  ' * indent + 'IntegerLiteral: ' + str(self.value))


class Decimal(Expression):
    def __init__(self, value: float):
        self.value = value

    def accept(self, visitor):
        return visitor.visit_decimal_literal(self)

    def dump(self, indent=0):
        print('  ' * indent + 'DecimalLiteral: ' + str(self.value))


class Boolean(Expression):
    def __init__(self, value: bool):
        self.value = value

    def accept(self, visitor):
        return visitor.visit_boolean_literal(self)

    def dump(self, indent=0):
        print('  ' * indent + 'BooleanLiteral: ' + str(self.value))


class Null(Expression):
    def accept(self, visitor):
        return visitor.visit_null_literal(self)

    def dump(self, indent=0):
        print('  ' * indent + 'NullLiteral')


class Assignment(Expression):
    def __init__(self, left: Variable, right: Expression):
        self.left = left
        self.right = right

    def accept(self, visitor):
        return visitor.visit_assignment_expression(self)

    def dump(self, indent=0):
        print('  ' * indent + 'AssignmentExpression')
        self.left.dump(indent + 1)
        self.right.dump(indent + 1)


class LogicalOr(BinaryExpression):
    def accept(self, visitor):
        return visitor.visit_logical_or_expression(self)

    def dump(self, indent=0):
        print('  ' * indent + 'LogicalOrExpression')
        self.left.dump(indent + 1)
        self.right.dump(indent + 1)


class LogicalAnd(BinaryExpression):
    def accept(self, visitor):
        return visitor.visit_logical_and_expression(self)

    def dump(self, indent=0):
        print('  ' * indent + 'LogicalAndExpression')
        self.left.dump(indent + 1)
        self.right.dump(indent + 1)


class BitwiseOr(BinaryExpression):
    def accept(self, visitor):
        return visitor.visit_bitwise_or_expression(self)

    def dump(self, indent=0):
        print('  ' * indent + 'BitwiseOrExpression')
        self.left.dump(indent + 1)
        self.right.dump(indent + 1)


class BitwiseAnd(BinaryExpression):
    def accept(self, visitor):
        return visitor.visit_bitwise_and_expression(self)

    def dump(self, indent=0):
        print('  ' * indent + 'BitwiseAndExpression')
        self.left.dump(indent + 1)
        self.right.dump(indent + 1)


class BitwiseXor(BinaryExpression):
    def accept(self, visitor):
        return visitor.visit_bitwise_xor_expression(self)

    def dump(self, indent=0):
        print('  ' * indent + 'BitwiseXorExpression')
        self.left.dump(indent + 1)
        self.right.dump(indent + 1)


class BitwiseNot(Expression):
    def __init__(self, expression: Expression):
        self.expression = expression

    def accept(self, visitor):
        return visitor.visit_bitwise_not_expression(self)

    def dump(self, indent=0):
        print('  ' * indent + 'BitwiseNotExpression')
        self.expression.dump(indent + 1)


class Equal(BinaryExpression):
    def accept(self, visitor):
        return visitor.visit_equality_expression(self)

    def dump(self, indent=0):
        print('  ' * indent + 'EqualityExpression')
        self.left.dump(indent + 1)
        self.right.dump(indent + 1)


class NotEqual(BinaryExpression):
    def accept(self, visitor):
        return visitor.visit_equality_expression(self)

    def dump(self, indent=0):
        print('  ' * indent + 'NotEqualExpression')
        self.left.dump(indent + 1)
        self.right.dump(indent + 1)


class Less(BinaryExpression):
    def accept(self, visitor):
        return visitor.visit_relational_expression(self)

    def dump(self, indent=0):
        print('  ' * indent + 'LessExpression')
        self.left.dump(indent + 1)
        self.right.dump(indent + 1)


class Greater(BinaryExpression):
    def accept(self, visitor):
        return visitor.visit_relational_expression(self)

    def dump(self, indent=0):
        print('  ' * indent + 'GreaterExpression')
        self.left.dump(indent + 1)
        self.right.dump(indent + 1)


class LessEqual(BinaryExpression):
    def accept(self, visitor):
        return visitor.visit_relational_expression(self)

    def dump(self, indent=0):
        print('  ' * indent + 'LessEqualExpression')
        self.left.dump(indent + 1)
        self.right.dump(indent + 1)


class GreaterEqual(BinaryExpression):
    def accept(self, visitor):
        return visitor.visit_relational_expression(self)

    def dump(self, indent=0):
        print('  ' * indent + 'GreaterEqualExpression')
        self.left.dump(indent + 1)
        self.right.dump(indent + 1)


class Add(BinaryExpression):
    def accept(self, visitor):
        return visitor.visit_additive_expression(self)

    def dump(self, indent=0):
        print('  ' * indent + 'AdditiveExpression')
        self.left.dump(indent + 1)
        self.right.dump(indent + 1)


class Subtract(BinaryExpression):
    def accept(self, visitor):
        return visitor.visit_additive_expression(self)

    def dump(self, indent=0):
        print('  ' * indent + 'SubtractExpression')
        self.left.dump(indent + 1)
        self.right.dump(indent + 1)


class Multiply(BinaryExpression):
    def accept(self, visitor):
        return visitor.visit_multiplicative_expression(self)

    def dump(self, indent=0):
        print('  ' * indent + 'MultiplicativeExpression')
        self.left.dump(indent + 1)
        self.right.dump(indent + 1)


class Divide(BinaryExpression):
    def accept(self, visitor):
        return visitor.visit_multiplicative_expression(self)

    def dump(self, indent=0):
        print('  ' * indent + 'DivideExpression')
        self.left.dump(indent + 1)
        self.right.dump(indent + 1)


class Modulo(BinaryExpression):
    def accept(self, visitor):
        return visitor.visit_multiplicative_expression(self)

    def dump(self, indent=0):
        print('  ' * indent + 'ModuloExpression')
        self.left.dump(indent + 1)
        self.right.dump(indent + 1)


class Positive(Expression):
    def __init__(self, expression: Expression):
        self.expression = expression

    def accept(self, visitor):
        return visitor.visit_unary_expression(self)

    def dump(self, indent=0):
        print('  ' * indent + 'PositiveExpression')
        self.expression.dump(indent + 1)


class Negative(Expression):
    def __init__(self, expression: Expression):
        self.expression = expression

    def accept(self, visitor):
        return visitor.visit_unary_expression(self)

    def dump(self, indent=0):
        print('  ' * indent + 'NegativeExpression')
        self.expression.dump(indent + 1)


class Not(Expression):

    def __init__(self, expression: Expression):
        self.expression = expression

    def accept(self, visitor):
        return visitor.visit_unary_expression(self)

    def dump(self, indent=0):
        print('  ' * indent + 'NotExpression')
        self.expression.dump(indent + 1)


# 对AST做遍历的Vistor
# 这是一个基类，定义了缺省的遍历方式。子类可以覆盖某些方法，修改遍历方式。
class AstVisitor:
    def visit(self, node: AST):
        return node.accept(self)

    def visit_declaration(self, node: Declaration):
        pass

    def visit_statement(self, node: Statement):
        pass

    def visit_expression(self, node: Expression):
        pass

    def visit_block_statement(self, node: BlockStatement):
        for statement in node.statements:
            self.visit(statement)

    def visit_expression_statement(self, node: ExpressionStatement):
        self.visit(node.expression)

    def visit_function_declaration(self, node: FunctionDeclaration):
        self.visit(node.body)

    def visit_variable_declaration(self, node: VariableDeclaration):
        self.visit(node.initializer)

    def visit_program(self, node: Program):
        self.visit(node.statements)

    def visit_binary_expression(self, node: BinaryExpression):
        self.visit(node.left)
        self.visit(node.right)

    def visit_call_expression(self, node: CallExpression):
        for argument in node.arguments:
            self.visit(argument)

    def visit_variable(self, node: Variable):
        pass

    def visit_string_literal(self, node: String):
        pass

    def visit_integer_literal(self, node: Integer):
        pass

    def visit_decimal_literal(self, node: Decimal):
        pass

    def visit_boolean_literal(self, node: Boolean):
        pass

    def visit_null_literal(self, node: Null):
        pass

    def visit_if_statement(self, node: IfStatement):
        self.visit(node.test)
        self.visit(node.consequent)
        self.visit(node.alternate)

    def visit_while_statement(self, node: WhileStatement):
        self.visit(node.test)
        self.visit(node.body)

    def visit_for_statement(self, node: ForStatement):
        self.visit(node.init)
        self.visit(node.test)
        self.visit(node.update)
        self.visit(node.body)

    def visit_break_statement(self, node: BreakStatement):
        pass

    def visit_continue_statement(self, node: ContinueStatement):
        pass

    def visit_return_statement(self, node: ReturnStatement):
        self.visit(node.argument)

    def visit_assignment_expression(self, node: Assignment):
        self.visit(node.left)
        self.visit(node.right)

    def visit_logical_or_expression(self, node: LogicalOr):
        self.visit(node.left)
        self.visit(node.right)

    def visit_logical_and_expression(self, node: LogicalAnd):
        self.visit(node.left)
        self.visit(node.right)

    def visit_equality_expression(self, node: Equal):
        self.visit(node.left)
        self.visit(node.right)

    def visit_relational_expression(self, node: Less):
        self.visit(node.left)
        self.visit(node.right)

    def visit_additive_expression(self, node: Add):

        self.visit(node.left)
        self.visit(node.right)

    def visit_multiplicative_expression(self, node: Multiply):
        self.visit(node.left)
        self.visit(node.right)

    def visit_unary_expression(self, node: Union[Positive, Negative, Not]):
        self.visit(node.expression)

    def visit_positive_expression(self, node: Positive):
        self.visit(node.expression)

    def visit_negative_expression(self, node: Negative):

        self.visit(node.expression)

    def visit_not_expression(self, node: Not):
        self.visit(node.expression)


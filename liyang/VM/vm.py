#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import List, Tuple, Mapping, Union
from VM.asts import AstVisitor, AST, BlockStatement, CallExpression, ForStatement, FunctionDeclaration, Program, Variable, VariableDeclaration, ReturnStatement, IfStatement
from VM.scope import Scope
from VM.symbol_t import FunctionSymbol, VariableSymbol, Symbol
from VM.asts import *

class Frame:
    def __init__(self, scope: Scope = None):
        self.scope = scope or Scope()
        self.values: Mapping[Symbol, any] = {}
        self.return_value = None


class ReturnValue:
    def __init__(self, value: any):
        self.value = value

    def __str__(self):
        return f"ReturnValue({self.value})"

class Interpretor(AstVisitor):
    def __init__(self):
        self.current_frame = Frame()
        self.stacks: List[Frame] = [self.current_frame]

    def push_frame(self, frame: Frame):
        self.stacks.append(frame)
        self.current_frame = frame

    def pop_frame(self):
        self.stacks.pop()
        if len(self.stacks) > 0:
            self.current_frame = self.stacks[-1]
        else:
            self.current_frame = None

    def visit_function_declaration(self, node, additional=None):
        return None

    def visit_block_statement(self, node: BlockStatement, additional=None):
        ret = None
        for statement in node.statements:
            ret = self.visit(statement)
            # 如果是return语句，直接返回
            if isinstance(ret, ReturnValue):
                return ret
        return ret

    def set_return_value(self, value):
        # 设置调用者的返回值
        frame = self.stacks[-2]
        frame.return_value = value

    def visit_return_statement(self, node: ReturnStatement, additional=None):
        value = None
        if node.argument:
            value = self.visit(node.argument)
            self.set_return_value(value)
        return ReturnValue(value)

    def visit_if_statement(self, node: IfStatement, additional=None):
        if self.visit(node.test):
            return self.visit(node.consequent)
        elif node.alternate:
            return self.visit(node.alternate)
        return None

    def visit_for_statement(self, node: ForStatement, additional=None):
        if node.init:
            self.visit(node.init)

        not_break = True if node.test is None else self.visit(node.test)
        while not_break:
            ret = self.visit(node.body)
            if isinstance(ret, ReturnValue):
                return ret

            if node.update:
                self.visit(node.update)
            not_break = True if node.test is None else self.visit(node.test)

    def visit_call_expression(self, node: CallExpression, additional=None):
        # 内置函数
        # TODO: callee没有resolve
        if node.callee.name == "print":
            for arg in node.arguments:
                ret = self.visit(arg)
                if isinstance(ret, ReturnValue):
                    ret = ret.value
                print(ret, end="")
            return None
        elif node.callee.name == "input":
            return input()
        elif node.callee.name == "int":
            return int(self.visit(node.arguments[0]))
        elif node.callee.name == "float":
            return float(self.visit(node.arguments[0]))
        elif node.callee.name == "str":
            return str(self.visit(node.arguments[0]))
        elif node.callee.name == "bool":
            return bool(self.visit(node.arguments[0]))
        elif node.callee.name == "void":
            return None
        elif node.callee.name == "len":
            return len(self.visit(node.arguments[0]))
        else:
            # 用户自定义函数
            self.push_frame(Frame(self.current_frame.scope))
            for param, arg in zip(node.callee.parameters, node.arguments):
                self.current_frame.values[param.name] = self.visit(arg)
            ret = self.visit(node.callee.body)
            self.pop_frame()
            return ret

    def visit_variable_declaration(self, node: VariableDeclaration, additional=None):
        if node.initializer:
            val = self.visit(node.initializer)
            self.current_frame.values[node.symbol.name] = val
            return val
        return None

    def visit_variable(self, node: Variable, additional=None):
        if node.is_left:
            return node.symbol
        else:
            return self.lookup_variable(node.symbol.name)

    def lookup_variable(self, name: str):
        for frame in reversed(self.stacks):
            if name in frame.values:
                return frame.values[name]
        return None

    def visit_assignment_expression(self, node: Assignment, additional=None):
        val = self.visit(node.right)
        self.current_frame.values[node.left.symbol.name] = val
        return val

    def visit_additive_expression(self, node: Union[Add, Subtract], additional=None):
        left = self.visit(node.left)
        right = self.visit(node.right)
        if isinstance(left, ReturnValue):
            left = left.value
        if isinstance(right, ReturnValue):
            right = right.value

        if isinstance(node, Add):
            return left + right
        else:
            return left - right

    def visit_multiplicative_expression(self, node: Union[Multiply, Divide, Modulo], additional=None):
        left = self.visit(node.left)
        right = self.visit(node.right)
        if isinstance(left, ReturnValue):
            left = left.value
        if isinstance(right, ReturnValue):
            right = right.value

        if isinstance(node, Multiply):
            return left * right
        elif isinstance(node, Divide):
            return left / right
        else:
            return left % right

    def visit_relational_expression(self, node: Union[Less, LessEqual, Greater, GreaterEqual], additional=None):
        left = self.visit(node.left)
        right = self.visit(node.right)
        if isinstance(left, ReturnValue):
            left = left.value
        if isinstance(right, ReturnValue):
            right = right.value

        if isinstance(node, Less):
            return left < right
        elif isinstance(node, LessEqual):
            return left <= right
        elif isinstance(node, Greater):
            return left > right
        else:
            return left >= right

    def visit_equality_expression(self, node: Union[Equal, NotEqual], additional=None):
        left = self.visit(node.left)
        right = self.visit(node.right)
        if isinstance(left, ReturnValue):
            left = left.value
        if isinstance(right, ReturnValue):
            right = right.value

        if isinstance(node, Equal):
            return left == right
        else:
            return left != right

    def visit_logical_and_expression(self, node: LogicalAnd, additional=None):
        left = self.visit(node.left)
        right = self.visit(node.right)
        if isinstance(left, ReturnValue):
            left = left.value
        if isinstance(right, ReturnValue):
            right = right.value

        return left and right

    def visit_logical_or_expression(self, node: LogicalOr, additional=None):
        left = self.visit(node.left)
        right = self.visit(node.right)
        if isinstance(left, ReturnValue):
            left = left.value
        if isinstance(right, ReturnValue):
            right = right.value

        return left or right

    def visit_logical_not_expression(self, node: Not, additional=None):
        return not self.visit(node.argument)

    def visit_integer_literal(self, node: Integer, additional=None):
        return int(node.value)

    def visit_decimal_literal(self, node: Decimal, additional=None):
        return float(node.value)

    def visit_string_literal(self, node: String, additional=None):
        return node.value

    def visit_boolean_literal(self, node: Boolean, additional=None):
        return bool(node.value)

    def visit_bitwise_and_expression(self, node: BitwiseAnd, additional=None):
        left = self.visit(node.left)
        right = self.visit(node.right)
        if isinstance(left, ReturnValue):
            left = left.value
        if isinstance(right, ReturnValue):
            right = right.value

        return left & right

    def visit_bitwise_or_expression(self, node: BitwiseOr, additional=None):
        left = self.visit(node.left)
        right = self.visit(node.right)
        if isinstance(left, ReturnValue):
            left = left.value
        if isinstance(right, ReturnValue):
            right = right.value

        return left | right

    def visit_bitwise_xor_expression(self, node: BitwiseXor, additional=None):
        left = self.visit(node.left)
        right = self.visit(node.right)
        if isinstance(left, ReturnValue):
            left = left.value
        if isinstance(right, ReturnValue):
            right = right.value

        return left ^ right

    def visit_bitwise_not_expression(self, node: BitwiseNot, additional=None):
        return ~self.visit(node.argument)

    def visit_unary_expression(self, node: Union[Positive, Negative], additional=None):
        if isinstance(node, Positive):
            return self.visit(node.argument)
        else:
            return -self.visit(node.argument)



class OpCode:
    def __init__(self, op: str, arg: any = None):
        self.op = op
        self.arg = arg

    def __str__(self):
        return f"{self.op} {self.arg}" if self.arg else self.op

    def __repr__(self):
        return self.__str__()


class ByteCodeGenerator(AstVisitor):
    def __init__(self):
        self.current_frame = Frame()
        self.stacks: List[Frame] = [self.current_frame]
        self.code: List[OpCode] = []

    def dump(self):
        for op in self.code:
            print(op)

    def push_frame(self, frame: Frame):
        self.stacks.append(frame)
        self.current_frame = frame

    def pop_frame(self):
        self.stacks.pop()
        if len(self.stacks) > 0:
            self.current_frame = self.stacks[-1]
        else:
            self.current_frame = None

    def visit_program(self, node: Program, additional=None):
        for statement in node.statements:
            self.visit(statement)

    def visit_function_declaration(self, node: FunctionDeclaration, additional=None):
        self.push_frame(Frame(self.current_frame.scope))
        for param in node.parameters:
            self.current_frame.scope.put(param.name, param.symbol)
        self.visit(node.body)
        self.pop_frame()

    def visit_block_statement(self, node: BlockStatement, additional=None):
        for statement in node.statements:
            self.visit(statement)

    def visit_return_statement(self, node: ReturnStatement, additional=None):
        if node.argument:
            self.code.append(OpCode("PUSH", self.visit(node.argument)))
        self.code.append(OpCode("RET"))

    def visit_if_statement(self, node: IfStatement, additional=None):
        self.code.append(OpCode("PUSH", self.visit(node.test)))
        self.code.append(OpCode("JMPF", len(self.code) + 2))
        self.visit(node.consequent)
        if node.alternate:
            self.code.append(OpCode("JMP", len(self.code) + 2))
            self.visit(node.alternate)

    def visit_for_statement(self, node: ForStatement, additional=None):
        if node.init:
            self.visit(node.init)
        self.code.append(OpCode("PUSH", self.visit(node.test)))
        self.code.append(OpCode("JMPF", len(self.code) + 2))
        self.visit(node.body)
        if node.update:
            self.visit(node.update)
        self.code.append(OpCode("JMP", len(self.code) - 3))

    def visit_call_expression(self, node: CallExpression, additional=None):
        for arg in node.arguments:
            self.code.append(OpCode("PUSH", self.visit(arg)))
        self.code.append(OpCode("CALL", node.callee.name))

    def visit_variable_declaration(self, node: VariableDeclaration, additional=None):
        if node.initializer:
            self.code.append(OpCode("PUSH", self.visit(node.initializer)))
            self.code.append(OpCode("STORE", node.symbol.name))

    def visit_variable(self, node: Variable, additional=None):
        return node.symbol.name

    def visit_assignment_expression(self, node: Assignment, additional=None):
        self.code.append(OpCode("PUSH", self.visit(node.right)))
        self.code.append(OpCode("STORE", node.left.symbol.name))

    def visit_additive_expression(self, node: Union[Add, Subtract], additional=None):
        self.code.append(OpCode("PUSH", self.visit(node.left)))
        self.code.append(OpCode("PUSH", self.visit(node.right)))
        if isinstance(node, Add):
            self.code.append(OpCode("ADD"))
        else:
            self.code.append(OpCode("SUB"))

    def visit_multiplicative_expression(self, node: Union[Multiply, Divide, Modulo], additional=None):
        self.code.append(OpCode("PUSH", self.visit(node.left)))
        self.code.append(OpCode("PUSH", self.visit(node.right)))
        if isinstance(node, Multiply):
            self.code.append(OpCode("MUL"))
        elif isinstance(node, Divide):
            self.code.append(OpCode("DIV"))
        else:
            self.code.append(OpCode("MOD"))

    def visit_relational_expression(self, node: Union[Less, LessEqual, Greater, GreaterEqual], additional=None):
        self.code.append(OpCode("PUSH", self.visit(node.left)))
        self.code.append(OpCode("PUSH", self.visit(node.right)))
        if isinstance(node, Less):
            self.code.append(OpCode("LT"))
        elif isinstance(node, LessEqual):
            self.code.append(OpCode("LE"))
        elif isinstance(node, Greater):
            self.code.append(OpCode("GT"))
        else:
            self.code.append(OpCode("GE"))

    def visit_equality_expression(self, node: Union[Equal, NotEqual], additional=None):
        self.code.append(OpCode("PUSH", self.visit(node.left)))
        self.code.append(OpCode("PUSH", self.visit(node.right)))
        if isinstance(node, Equal):
            self.code.append(OpCode("EQ"))
        else:
            self.code.append(OpCode("NE"))

    def visit_logical_and_expression(self, node: LogicalAnd, additional=None):
        self.code.append(OpCode("PUSH", self.visit(node.left)))
        self.code.append(OpCode("PUSH", self.visit(node.right)))
        self.code.append(OpCode("AND"))

    def visit_logical_or_expression(self, node: LogicalOr, additional=None):
        self.code.append(OpCode("PUSH", self.visit(node.left)))
        self.code.append(OpCode("PUSH", self.visit(node.right)))
        self.code.append(OpCode("OR"))

    def visit_logical_not_expression(self, node: Not, additional=None):
        self.code.append(OpCode("PUSH", self.visit(node.argument)))
        self.code.append(OpCode("NOT"))

    def visit_integer_literal(self, node: Integer, additional=None):
        return node.value

    def visit_decimal_literal(self, node: Decimal, additional=None):
        return node.value

    def visit_string_literal(self, node: String, additional=None):
        return node.value

    def visit_boolean_literal(self, node: Boolean, additional=None):
        return node.value

    def visit_bitwise_and_expression(self, node: BitwiseAnd, additional=None):
        self.code.append(OpCode("PUSH", self.visit(node.left)))
        self.code.append(OpCode("PUSH", self.visit(node.right)))
        self.code.append(OpCode("BAND"))

    def visit_bitwise_or_expression(self, node: BitwiseOr, additional=None):
        self.code.append(OpCode("PUSH", self.visit(node.left)))
        self.code.append(OpCode("PUSH", self.visit(node.right)))
        self.code.append(OpCode("BOR"))

    def visit_bitwise_xor_expression(self, node: BitwiseXor, additional=None):
        self.code.append(OpCode("PUSH", self.visit(node.left)))
        self.code.append(OpCode("PUSH", self.visit(node.right)))
        self.code.append(OpCode("BXOR"))

    def visit_bitwise_not_expression(self, node: BitwiseNot, additional=None):
        self.code.append(OpCode("PUSH", self.visit(node.argument)))
        self.code.append(OpCode("BNOT"))

    def visit_unary_expression(self, node: Union[Positive, Negative], additional=None):
        self.code.append(OpCode("PUSH", self.visit(node.argument)))
        if isinstance(node, Positive):
            self.code.append(OpCode("POS"))
        else:
            self.code.append(OpCode("NEG"))

    def generate(self, node: AST):
        self.visit(node)
        return self.code

    def __str__(self):
        return "\n".join([str(op) for op in self.code])

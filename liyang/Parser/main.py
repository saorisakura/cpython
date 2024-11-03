#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 词法分析器
# 词法分析器的作用是将源代码转换为单词流，即Token序列
from Parser.scanner import *
from Parser.asts import *


# 语法分析为LL算法，因此需要知道如何使用First和Follow集合
# 语法分析器的作用是将Token序列转换为抽象语法树
class Parser:
    def __init__(self, lexer: Lexer):
        self.lexer = lexer

    def parse(self):
        return Program(self.parse_statements())

    def parse_statements(self):
        statements = []
        token = self.lexer.peek()
        while token.kind != EOF:
            statements.append(self.parse_statement())
            token = self.lexer.peek()
        return statements

    def parse_statement(self) -> Statement:
        token = self.lexer.peek()
        if token.kind == KeyWord and token.value == 'var':
            return self.parse_var_decl()
        elif token.kind == KeyWord and token.value == 'let':
            return self.parse_let_decl()
        elif token.kind == KeyWord and token.value == 'function':
            return self.parse_func_decl()
        elif token.kind == KeyWord and token.value == 'if':
            return self.parse_if()
        elif token.kind == KeyWord and token.value == 'while':
            return self.parse_while()
        elif token.kind == KeyWord and token.value == 'for':
            return self.parse_for()
        elif token.kind == KeyWord and token.value == 'break':
            return self.parse_break()
        elif token.kind == KeyWord and token.value == 'continue':
            return self.parse_continue()
        elif token.kind == KeyWord and token.value == 'return':
            return self.parse_return()
        elif token.kind == Separator and token.value == '{':
            return self.parse_block()
        else:
            return self.parse_expr_stmt()

    def parse_var_decl(self):
        self.lexer.next()
        name = self.lexer.next().value
        token = self.lexer.next()
        if token.kind == Operator and token.value == '=':
            expr = self.parse_expr()
            self.lexer.next()
            return VariableDeclaration(name, expr)
        return VariableDeclaration(name, None)

    def parse_let_decl(self):
        self.lexer.next()
        name = self.lexer.next().value
        token = self.lexer.next()
        if token.kind == Operator and token.value == '=':
            expr = self.parse_expr()
            self.lexer.next()
            return VariableDeclaration(name, expr)
        return VariableDeclaration(name, None)

    def parse_func_decl(self):
        self.lexer.next()
        name = self.lexer.next().value
        self.lexer.next()
        params = []
        token = self.lexer.peek()
        while token.kind != Separator or token.value != ')':
            if token.kind == Separator and token.value == ',':
                self.lexer.next()
                token = self.lexer.peek()
            params.append(self.lexer.next().value)
            token = self.lexer.peek()
        # skip ')'
        if self.lexer.peek().value == ')':
            self.lexer.next()
        else:
            raise Exception('Expect )')
        token = self.lexer.peek()
        if token.kind != Separator or token.value != '{':
            raise Exception('Expect {')
        body = self.parse_block()
        return FunctionDeclaration(name, params, body)

    def parse_if(self):
        # skip 'if'
        self.lexer.next()
        # skip '('
        self.lexer.next()
        condition = self.parse_expr()
        self.lexer.next()
        then_block = self.parse_block()
        else_block = None
        token = self.lexer.peek()
        if token.kind == KeyWord and token.value == 'else':
            self.lexer.next()
            else_block = self.parse_block()
        return IfStatement(condition, then_block, else_block)

    def parse_while(self):
        self.lexer.next()
        self.lexer.next()
        condition = self.parse_expr()
        self.lexer.next()
        body = self.parse_block()
        return WhileStatement(condition, body)

    def parse_for(self):
        self.lexer.next()
        self.lexer.next()
        init = self.parse_expr_stmt()
        condition = self.parse_expr()
        self.lexer.next()
        update = self.parse_expr()
        self.lexer.next()
        body = self.parse_block()
        return ForStatement(init, condition, update, body)

    def parse_break(self):
        self.lexer.next()
        self.lexer.next()
        return BreakStatement()

    def parse_continue(self):
        self.lexer.next()
        self.lexer.next()
        return ContinueStatement()

    def parse_return(self):
        self.lexer.next()
        expr = self.parse_expr()
        self.lexer.next()
        return ReturnStatement(expr)

    def parse_expr_stmt(self):
        expr = self.parse_expr()
        self.lexer.next()
        return ExpressionStatement(expr)

    def parse_block(self):
        if self.lexer.peek().value == '{':
            self.lexer.next()
        else:
            raise Exception('Expect {')
        stmt = []
        token = self.lexer.peek()
        while token.kind != Separator or token.value != '}':
            stmt.append(self.parse_statement())
            token = self.lexer.peek()
        if self.lexer.peek().value == '}':
            self.lexer.next()
        else:
            raise Exception('Expect }')
        return stmt

    def parse_expr(self):
        # 递归下降解析表达式
        # 优先级从高到低
        # 当前是一种实现方式，还有一种实现方式是使用表来记录优先级，然后for循环处理
        # 当前这种方式是从低优先级开始处理，然后递归调用更高优先级的表达式，适合大多数语言尤其是表达能力欠佳的语言如C、C++
        # 但是对于表达能力强的语言如Haskell、Go，还是使用表来记录优先级更合适（清晰）
        return self.parse_assignment_expr()

    def parse_assignment_expr(self):
        # 递归下降解析赋值表达式，先下降到最高优先级的表达式，然后递归调用更低优先级的表达式
        expr = self.parse_logical_or_expr()
        token = self.lexer.peek()
        if token.kind == Operator and token.value == '=':
            self.lexer.next()
            right = self.parse_assignment_expr()
            return Assignment(expr, right)
        return expr

    def parse_logical_or_expr(self):
        expr = self.parse_logical_and_expr()
        token = self.lexer.peek()
        while token.kind == Operator and token.value == '||':
            self.lexer.next()
            right = self.parse_logical_and_expr()
            expr = LogicalOr(expr, token.value, right)
            token = self.lexer.peek()
        return expr

    def parse_logical_and_expr(self):
        expr = self.parse_bitwise_or_expr()
        token = self.lexer.peek()
        while token.kind == Operator and token.value == '&&':
            self.lexer.next()
            right = self.parse_equality_expr()
            expr = LogicalAnd(expr, token.value, right)
            token = self.lexer.peek()
        return expr

    def parse_bitwise_or_expr(self):
        expr = self.parse_bitwise_xor_expr()
        token = self.lexer.peek()
        while token.kind == Operator and token.value == '|':
            self.lexer.next()
            right = self.parse_bitwise_xor_expr()
            expr = BitwiseOr(expr, token.value, right)
            token = self.lexer.peek()
        return expr

    def parse_bitwise_xor_expr(self):
        expr = self.parse_bitwise_and_expr()
        token = self.lexer.peek()
        while token.kind == Operator and token.value == '^':
            self.lexer.next()
            right = self.parse_bitwise_and_expr()
            expr = BitwiseXor(expr, token.value, right)
            token = self.lexer.peek()
        return expr

    def parse_bitwise_and_expr(self):
        expr = self.parse_equality_expr()
        token = self.lexer.peek()
        while token.kind == Operator and token.value == '&':
            self.lexer.next()
            right = self.parse_equality_expr()
            expr = BitwiseAnd(expr, token.value, right)
            token = self.lexer.peek()
        return expr

    def parse_equality_expr(self):
        expr = self.parse_relational_expr()
        token = self.lexer.peek()
        while token.kind == Operator and (token.value == '==' or token.value == '!='):
            self.lexer.next()
            right = self.parse_relational_expr()
            if token.value == '==':
                expr = Equal(expr, token.value, right)
            else:
                expr = NotEqual(expr, token.value, right)
            token = self.lexer.peek()
        return expr

    def parse_relational_expr(self):
        expr = self.parse_additive_expr()
        token = self.lexer.peek()
        while token.kind == Operator and (token.value == '<' or token.value == '>' or token.value == '<=' or token.value == '>='):
            self.lexer.next()
            right = self.parse_additive_expr()
            if token.value == '<':
                expr = Less(expr, token.value, right)
            elif token.value == '>':
                expr = Greater(expr, token.value, right)
            elif token.value == '<=':
                expr = LessEqual(expr, token.value, right)
            else:
                expr = GreaterEqual(expr, token.value, right)
            token = self.lexer.peek()
        return expr

    def parse_additive_expr(self):
        expr = self.parse_multiplicative_expr()
        token = self.lexer.peek()
        while token.kind == Operator and (token.value == '+' or token.value == '-'):
            self.lexer.next()
            right = self.parse_multiplicative_expr()
            if token.value == '+':
                expr = Add(expr, token.value, right)
            else:
                expr = Subtract(expr, token.value, right)
            token = self.lexer.peek()
        return expr

    def parse_multiplicative_expr(self):
        expr = self.parse_unary_expr()
        token = self.lexer.peek()
        while token.kind == Operator and (token.value == '*' or token.value == '/' or token.value == '%'):
            self.lexer.next()
            right = self.parse_unary_expr()
            if token.value == '*':
                expr = Multiply(expr, token.value, right)
            elif token.value == '/':
                expr = Divide(expr, token.value, right)
            else:
                expr = Modulo(expr, token.value, right)
            token = self.lexer.peek()
        return expr

    def parse_unary_expr(self):
        token = self.lexer.peek()
        if token.kind == Operator and (token.value == '+' or token.value == '-' or token.value == '!' or token.value == '~'):
            self.lexer.next()
            expr = self.parse_unary_expr()
            if token.value == '+':
                return Positive(expr)
            elif token.value == '-':
                return Negative(expr)
            elif token.value == '!':
                return Not(expr)
            elif token.value == '~':
                return BitwiseNot(expr)
            else:
                raise Exception('Not implemented')
        return self.parse_primary_expr()

    def parse_primary_expr(self):
        token = self.lexer.peek()
        if token.kind == Identifier:
            self.lexer.next()
            # function call
            if self.lexer.peek().value == '(':
                function_name = token.value
                self.lexer.next()
                args = []
                token = self.lexer.peek()
                while token.kind != Separator or token.value != ')':
                    if token.kind == Separator and token.value == ',':
                        self.lexer.next()
                        token = self.lexer.peek()
                    args.append(self.parse_expr())
                    token = self.lexer.peek()
                # skip ')'
                self.lexer.next()
                return CallExpression(function_name, None, args)
            return Variable(token.value, None)
        elif token.kind == IntegerLiteral:
            self.lexer.next()
            return Integer(token.value)
        elif token.kind == StringLiteral:
            self.lexer.next()
            return String(token.value)
        elif token.kind == DecimalLiteral:
            self.lexer.next()
            return Decimal(token.value)
        elif token.kind == BooleanLiteral:
            self.lexer.next()
            return Boolean(token.value)
        elif token.kind == Separator and token.value == '(':
            self.lexer.next()
            expr = self.parse_expr()
            self.lexer.next()
            return expr
        elif token.kind == Separator and token.value == '{':
            expr = self.parse_block()
            return expr
        elif token.kind == Separator and token.value == '[':
            self.lexer.next()
            expr = self.parse_array()
            self.lexer.next()
            return expr
        elif token.kind == Operator and token.value == '~':
            self.lexer.next()
            expr = self.parse_expr()
            return expr
        else:
            raise Exception('Unexpected token: ' + token.value)


class AstPrinter(AstVisitor):
    pass


def main():
    source = '''
{
    let a = 1;
    print(a);
}
print('hello, world');
let ret = add(1, 2);
print(ret);
if (ret == 3) {
    print('add ok');
} else {
    print('add failed');
}
let ret1 = sub(1, 2);
while (ret1 > 0) {
    print(ret1);
    ret1 = sub(ret1, 1);
}
let ret2 = mul(2, 3);
let i;
for (i = 0; i < ret2; i = add(i, 1)) {
    print(i);
}
function add(a, b) {
    return a + b;
}
function sub(a, b) {
    return a - b;
}
function mul(a, b) {
    return a * b;
}
function div(a, b) {
    return a / b;
}
function mod(a, b) {
    return a % b;
}
function eq(a, b) {
    return a == b;
}
function ne(a, b) {
    return a != b;
}
function lt(a, b) {
    return a < b;
}
function gt(a, b) {
    return a > b;
}
function le(a, b) {
    return a <= b;
}
function ge(a, b) {
    return a >= b;
}
function and(a, b) {
    return a && b;
}
function or(a, b) {
    return a || b;
}
function band(a, b) {
    return a & b;
}
function bor(a, b) {
    return a | b;
}
function bxor(a, b) {
    return a ^ b;
}
function bnot(a) {
    return ~a;
}
'''
# TODO: 三元操作符识别
# function cond(a, b, c) {
    # return a ? b : c;
# }

    lexer = Lexer(CharStream(source))
    parser = Parser(lexer)
    program = parser.parse()
    program.dump()
    # printer = AstPrinter()
    # program.accept(printer)


if __name__ == '__main__':
    main()

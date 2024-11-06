#!/usr/bin/env python
# -*- coding: utf-8 -*-
from VM.scanner import CharStream, Lexer
from VM.parser import Parser
from VM.semantics import Entry, RefResolver
from VM.vm import Interpretor


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


def main1():
    source1 = '''
let a: int = 1;
a = a + 1;
// should print 2
print(a);'''
    source2 = '''
function add(a: int, b: int) int {
    return a + b;
}
// should print 2
print(add(1, 1));
'''
    source3 = '''
function fibonacci(n: int) int {
    if (n <= 1) {
        return n;
    }
    return fibonacci(n-1) + fibonacci(n-2);
}
print(fibonacci(10));
'''
    sources = [source1, source2, source3]
    for source in sources:
        lexer = Lexer(CharStream(source))
        parser = Parser(lexer)
        program = parser.parse()
        program.dump()
        print('=' * 80)
        # 建立符号表，记录每个符号的类型和作用域
        entry = Entry()
        entry.visit(program)
        program.dump()
        print('*' * 80)
        # 消解符号和定义间的引用
        # 函数、变量、类型等
        resolver = RefResolver()
        resolver.visit(program)
        program.dump()
        print('+' * 80)
        interpretor = Interpretor()
        # 2024-02-29顺利打印出11
        # 没有区分类型，按理应该是1 + 1 = 2 已修改
        # call expression callee没有resolve
        interpretor.visit(program)
        print('-' * 80)


if __name__ == '__main__':
    main1()

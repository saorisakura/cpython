#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 词法分析器
# 词法分析器的作用是将源代码转换为单词流，即Token序列
from dataclasses import dataclass

# Token的种类
KeyWord = 1
Identifier = 2
Operator = 3
Separator = 4
StringLiteral = 5
IntegerLiteral = 6
DecimalLiteral = 7
NullLiteral = 8
BooleanLiteral = 9
EOF = 10
Unknown = 11

@dataclass
class Token:
    kind: int
    value: str


class CharStream:
    def __init__(self, s: str):
        self.s = s
        self.pos = 0
        self.line = 1
        self.column = 1

    def __str__(self):
        return self.s[self.pos:]

    def __repr__(self):
        return self.s[self.pos:]

    def eof(self):
        return self.pos >= len(self.s)

    def peek(self):
        if self.pos >= len(self.s):
            return None
        return self.s[self.pos]

    def next(self):
        if self.pos >= len(self.s):
            return None
        c = self.s[self.pos]
        self.pos += 1
        if c == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        return c


# 词法分析器
class Lexer:
    def __init__(self, stream: CharStream):
        self.stream = stream
        self.tokens = []
        self.next_token = Token(EOF, '')

    def get_position(self):
        return (self.stream.line, self.stream.column)

    def is_space(self, c):
        return c in [' ', '\t', '\n']

    def is_letter(self, c):
        return c.isalpha() or c == '_'

    def is_digit(self, c):
        return c.isdigit()

    def is_separator(self, c):
        return c in ['(', ')', '{', '}', '[', ']', ',', ';']

    def is_quote(self, c):
        return c in ['"', "'"]

    def next(self) -> Token:
        if self.next_token.kind == EOF and not self.stream.eof():
            self.next_token = self.get_token()
        token = self.next_token
        self.next_token = self.get_token()
        return token

    def peek(self) -> Token:
        if self.next_token.kind == EOF and not self.stream.eof():
            self.next_token = self.get_token()
        return self.next_token

    def skip_space(self):
        while not self.stream.eof() and self.is_space(self.stream.peek()):
            self.stream.next()

    def get_identifier(self) -> Token:
        value = ''
        while not self.stream.eof():
            c = self.stream.peek()
            if self.is_letter(c) or self.is_digit(c):
                value += self.stream.next()
            else:
                break
        # is keyword
        if value in [
            "function", "class",     "break",       "delete",    "return",
            "case",      "do",        "if",          "switch",    "var",
            "catch",     "else",      "in",          "this",      "void",
            "continue",  "false",     "instanceof",  "throw",     "while",
            "debugger",  "finally",   "new",         "true",      "with",
            "default",   "for",       "null",        "try",       "typeof",
            # 下面这些用于严格模式
            "implements","let",       "private",     "public",    "yield",
            "interface", "package",   "protected",   "static", "await",
            "abstract",  "boolean",   "byte",        "char",      "double",
            "final",     "float",     "goto",        "int",       "long",
            "native",    "short",    "synchronized","transient", "volatile",
            "arguments", "eval",      "super",       "constructor", "prototype",
            "null",      "true", "false",
        ]:
            return Token(KeyWord, value)
        return Token(Identifier, value)

    def get_literal(self) -> Token:
        value = ''
        while not self.stream.eof():
            c = self.stream.peek()
            if self.is_digit(c):
                value += self.stream.next()
            else:
                break
        # decimal
        if self.stream.peek() == '.':
            value += self.stream.next()
            while not self.stream.eof():
                c = self.stream.peek()
                if self.is_digit(c):
                    value += self.stream.next()
                else:
                    break
            return Token(DecimalLiteral, value)
        return Token(IntegerLiteral, value)

    def get_string(self) -> Token:
        quote = self.stream.next()
        value = ''
        while not self.stream.eof():
            c = self.stream.next()
            if c == quote:
                break
            value += c
        return Token(StringLiteral, value)

    def get_separator(self) -> Token:
        value = self.stream.next()
        return Token(Separator, value)

    def get_comment(self):
        while not self.stream.eof():
            c = self.stream.next()
            if c == '\n':
                break

    def get_block_comment(self):
        while not self.stream.eof():
            c = self.stream.next()
            if c == '*':
                c1 = self.stream.next()
                if c1 == '/':
                    break

    def get_token(self) -> Token:
        self.skip_space()
        if self.stream.eof():
            return Token(EOF, '')
        c = self.stream.peek()
        if self.is_letter(c):
            return self.get_identifier()
        elif self.is_digit(c):
            return self.get_literal()
        elif self.is_quote(c):
            return self.get_string()
        elif self.is_separator(c):
            return self.get_separator()
        elif c == '/':
            self.stream.next()
            c1 = self.stream.peek()
            if c1 == '/':
                self.get_comment()
                return self.get_token()
            elif c1 == '*':
                self.get_block_comment()
                return self.get_token()
            elif c1 == '=':
                self.stream.next()
                return Token(Operator, '/=')
            else:
                return Token(Operator, '/')
        elif c == '+':
            self.stream.next()
            c1 = self.stream.peek()
            if c1 == '+':
                self.stream.next()
                return Token(Operator, '++')
            elif c1 == '=':
                self.stream.next()
                return Token(Operator, '+=')
            else:
                return Token(Operator, '+')
        elif c == '-':
            self.stream.next()
            c1 = self.stream.peek()
            if c1 == '-':
                self.stream.next()
                return Token(Operator, '--')
            elif c1 == '=':
                self.stream.next()
                return Token(Operator, '-=')
            else:
                return Token(Operator, '-')
        elif c == '*':
            self.stream.next()
            c1 = self.stream.peek()
            if c1 == '=':
                self.stream.next()
                return Token(Operator, '*=')
            else:
                return Token(Operator, '*')
        elif c == '%':
            self.stream.next()
            c1 = self.stream.peek()
            if c1 == '=':
                self.stream.next()
                return Token(Operator, '%=')
            else:
                return Token(Operator, '%')
        elif c == '=':
            self.stream.next()
            c1 = self.stream.peek()
            if c1 == '=':
                self.stream.next()
                return Token(Operator, '==')
            else:
                return Token(Operator, '=')
        elif c == '!':
            self.stream.next()
            c1 = self.stream.peek()
            if c1 == '=':
                self.stream.next()
                return Token(Operator, '!=')
            else:
                return Token(Operator, '!')
        elif c == '<':
            self.stream.next()
            c1 = self.stream.peek()
            if c1 == '=':
                self.stream.next()
                return Token(Operator, '<=')
            else:
                return Token(Operator, '<')
        elif c == '>':
            self.stream.next()
            c1 = self.stream.peek()
            if c1 == '=':
                self.stream.next()
                return Token(Operator, '>=')
            else:
                return Token(Operator, '>')
        elif c == '&':
            self.stream.next()
            c1 = self.stream.peek()
            if c1 == '&':
                self.stream.next()
                return Token(Operator, '&&')
            else:
                return Token(Operator, '&')
        elif c == '|':
            self.stream.next()
            c1 = self.stream.peek()
            if c1 == '|':
                self.stream.next()
                return Token(Operator, '||')
            else:
                return Token(Operator, '|')
        elif c == '^':
            self.stream.next()
            return Token(Operator, '^')
        elif c == '~':
            self.stream.next()
            return Token(Operator, '~')
        elif c == '?':
            self.stream.next()
            return Token(Operator, '?')
        elif c == ':':
            self.stream.next()
            return Token(Operator, ':')
        else:
            self.stream.next()
            return Token(Unknown, c)

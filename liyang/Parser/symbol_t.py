#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import List


class Symbol:
    def __init__(self, name: str, type: any, index: int = 0):
        self.name = name
        self.type = type
        self.index = index

    def __eq__(self, other):
        return self.name == other.name and self.type == other.type

    def __str__(self):
        return f"{self.name}: {self.type}"


class SymbolTable:
    def __init__(self, parent: any = None):
        self.parent = parent
        self.symbols = []

    def add(self, symbol: Symbol):
        self.symbols.append(symbol)

    def find(self, name: str):
        for symbol in self.symbols:
            if symbol.name == name:
                return symbol
        if self.parent:
            return self.parent.find(name)
        return None

    def __str__(self):
        return "\n".join(map(str, self.symbols))


class SymbolTableStack:
    def __init__(self):
        self.stack: List[SymbolTable] = [SymbolTable()]

    def push(self, symbol_table: SymbolTable):
        self.stack.append(symbol_table)

    def pop(self):
        return self.stack.pop()

    def peek(self):
        return self.stack[-1]

    def add(self, symbol: Symbol):
        self.peek().add(symbol)

    def find(self, name: str):
        return self.peek().find(name)

    def __str__(self):
        return "\n".join(map(str, self.stack))


class FunctionSymbol(Symbol):
    def __init__(self, name: str, type: any, index: int = 0, param_types: List[any] = []):
        super().__init__(name, type, index)
        self.param_types = param_types

    def __eq__(self, other):
        return super().__eq__(other) and self.param_types == other.param_types

    def __str__(self):
        return f"{self.name}: {self.type} ({', '.join(map(str, self.param_types))})"


class StructSymbol(Symbol):
    def __init__(self, name: str, type: any, index: int = 0, fields: dict[str, any] = {}):
        super().__init__(name, type, index)
        self.fields = fields

    def __eq__(self, other):
        return super().__eq__(other) and self.fields == other.fields

    def __str__(self):
        return f"{self.name}: {self.type} {{{', '.join(f'{k}: {v}' for k, v in self.fields.items())}}}"


class VariableSymbol(Symbol):
    def __init__(self, name: str, type: any, index: int = 0):
        super().__init__(name, type, index)

    def __str__(self):
        return f"{self.name}: {self.type}"


class SymbolTableBuilder:
    def __init__(self):
        self.stack = SymbolTableStack()

    def visit(self, node: any):
        if isinstance(node, FunctionSymbol):
            return self.visit_function(node)
        elif isinstance(node, StructSymbol):
            return self.visit_struct(node)
        else:
            raise Exception("Unknown symbol")

    def visit_function(self, symbol: FunctionSymbol):
        self.stack.add(symbol)
        return symbol

    def visit_struct(self, symbol: StructSymbol):
        self.stack.add(symbol)
        return symbol

    def visit_variable(self, symbol: VariableSymbol):
        self.stack.add(symbol)
        return symbol


class SymbolTableVisitor:
    def visit(self, node: any):
        if isinstance(node, FunctionSymbol):
            return self.visit_function(node)
        elif isinstance(node, StructSymbol):
            return self.visit_struct(node)
        elif isinstance(node, VariableSymbol):
            return self.visit_variable(node)
        else:
            raise Exception("Unknown symbol")

    def visit_function(self, symbol: FunctionSymbol):
        pass

    def visit_struct(self, symbol: StructSymbol):
        pass

    def visit_variable(self, symbol: VariableSymbol):
        pass

built_ins = SymbolTable()
built_ins.add(FunctionSymbol("print", None, 0, [None]))
built_ins.add(FunctionSymbol("input", None, 1, []))
built_ins.add(FunctionSymbol("int", None, 2, []))
built_ins.add(FunctionSymbol("float", None, 3, []))
built_ins.add(FunctionSymbol("str", None, 4, []))
built_ins.add(FunctionSymbol("bool", None, 5, []))
built_ins.add(FunctionSymbol("void", None, 6, []))
built_ins.add(FunctionSymbol("len", None, 7, [None]))
built_ins.add(StructSymbol("list", None, 0, {"items": None}))
built_ins.add(StructSymbol("dict", None, 1, {"items": None}))
built_ins.add(StructSymbol("set", None, 2, {"items": None}))
built_ins.add(StructSymbol("tuple", None, 3, {"items": None}))
built_ins.add(StructSymbol("range", None, 4, {"start": None, "stop": None, "step": None}))
built_ins.add(StructSymbol("slice", None, 5, {"start": None, "stop": None, "step": None}))
built_ins.add(StructSymbol("str", None, 6, {"value": None}))
built_ins.add(StructSymbol("int", None, 7, {"value": None}))
built_ins.add(StructSymbol("float", None, 8, {"value": None}))
built_ins.add(StructSymbol("bool", None, 9, {"value": None}))
built_ins.add(StructSymbol("void", None, 10, {}))
built_ins.add(VariableSymbol("None", None, 0))
built_ins.add(VariableSymbol("True", None, 1))
built_ins.add(VariableSymbol("False", None, 2))
built_ins.add(VariableSymbol("self", None, 3))
built_ins.add(VariableSymbol("class", None, 4))
built_ins.add(VariableSymbol("args", None, 5))
built_ins.add(VariableSymbol("kwargs", None, 6))

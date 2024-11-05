#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import List, Tuple


class Scope:
    def __init__(self, parent: "Scope" = None):
        self.parent = parent
        self.children: List[Scope] = []
        self.symbols: dict[str, Tuple[int, int]] = {}

    def get(self, name: str) -> Tuple[int, int]:
        if name in self.symbols:
            return self.symbols[name]
        if self.parent is not None:
            return self.parent.get(name)
        return None

    def put(self, name: str, kind: int, type_index: int):
        self.symbols[name] = (kind, type_index)

    def create_child(self):
        child = Scope(self)
        self.children.append(child)
        return child

    def __str__(self):
        return str(self.symbols)


class ScopeVisitor:
    def __init__(self):
        self.root = Scope()
        self.current = self.root

    def enter_scope(self):
        self.current = self.current.create_child()

    def exit_scope(self):
        self.current = self.current.parent

    def put(self, name: str, kind: int, type_index: int):
        self.current.put(name, kind, type_index)

    def get(self, name: str) -> Tuple[int, int]:
        return self.current.get(name)

    def __str__(self):
        return str(self.root)

    def visit(self, node):
        method = f"visit_{node.__class__.__name__}"
        visitor = getattr(self, method, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        for child in node.children:
            self.visit(child)

    def visit_Program(self, node):
        self.enter_scope()
        self.generic_visit(node)
        self.exit_scope()

    def visit_Declaration(self, node):
        self.put(node.name, node.kind, node.type_index)
        self.generic_visit(node)

    def visit_Variable(self, node):
        self.put(node.name, node.kind, node.type_index)
        self.generic_visit(node)

    def visit_Function(self, node):
        self.put(node.name, node.kind, node.type_index)
        self.enter_scope()
        self.generic_visit(node)
        self.exit_scope()

    def visit_Parameter(self, node):
        self.put(node.name, node.kind, node.type_index)
        self.generic_visit(node)

    def visit_Call(self, node):
        self.generic_visit(node)
        self.get(node.name)

    def visit_Identifier(self, node):
        self.get(node.name)
        self.generic_visit(node)

    def visit_Assignment(self, node):
        self.get(node.name)
        self.generic_visit(node)

    def visit_If(self, node):
        self.enter_scope()
        self.generic_visit(node)
        self.exit_scope()

    def visit_While(self, node):
        self.enter_scope()
        self.generic_visit(node)
        self.exit_scope()

    def visit_For(self, node):
        self.enter_scope()
        self.generic_visit(node)
        self.exit_scope()

    def visit_Return(self, node):
        self.generic_visit(node)

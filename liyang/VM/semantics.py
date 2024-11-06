#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 语义分析
from VM.asts import AstVisitor, AST, BlockStatement, CallExpression, ForStatement, FunctionDeclaration, Program, Variable, VariableDeclaration, Assignment
from VM.scope import Scope
from VM.symbol_t import FunctionSymbol, VariableSymbol, built_ins
from VM.type import FunctionType, SystemType
from typing import Mapping, Any, Optional


class SemanticAstVisitor(AstVisitor):
    errors = []
    warnings = []

    def add_error(self, error: AST, message: str):
        self.errors.append({
            'error': error,
            'message': message
        })

    def add_warning(self, warning: AST, message: str):
        self.warnings.append({
            'warning': warning,
            'message': message
        })


class Entry(SemanticAstVisitor):

    def __init__(self, scope: Scope = None, symbol: FunctionSymbol = None):
        super().__init__()
        self.scope = scope or Scope()
        self.symbol = symbol

    def visit_program(self, node: Program, additional=None):
        symbol = FunctionSymbol('main', FunctionType('main', [], SystemType.int_type))
        node.symbol = symbol
        self.symbol = symbol
        return super().visit_program(node, additional)

    def visit_function_declaration(self, node: FunctionDeclaration, additional=None):
        current_scope = self.scope
        function_name = node.name

        params_type = []
        for param in node.parameters:
            params_type.append(param.symbol.type)

        function_type = FunctionType(function_name, params_type, node.return_type)
        symbol = FunctionSymbol(function_name, function_type)
        symbol.decl = node
        node.symbol = symbol

        if current_scope.lookup(function_name, True):
            self.add_error(node, f"Function '{function_name}' already defined.")
        else:
            current_scope.put(function_name, symbol)

        old_symbol = self.symbol
        self.symbol = symbol

        old_scope = self.scope
        self.scope = Scope(self.scope)
        node.scope = self.scope

        super().visit_function_declaration(node, additional='function')

        self.symbol = old_symbol
        self.scope = old_scope

    def visit_block_statement(self, node: BlockStatement, additional=None):
        # 创建新的作用域
        # 外侧作用域有可能是函数作用域
        old_scope = self.scope
        self.scope = Scope(self.scope)
        node.scope = self.scope

        super().visit_block_statement(node)

        self.scope = old_scope

    def visit_variable_declaration(self, node: VariableDeclaration, additional=None):
        current_scope = self.scope
        variable_name = node.name

        if current_scope.lookup(variable_name, True):
            raise Exception(f"Variable '{variable_name}' already defined.")

        symbol = VariableSymbol(variable_name, node.inferredType)
        node.symbol = symbol
        symbol.decl = node
        current_scope.put(variable_name, symbol)

        # 生成代码时，将变量添加到函数符号中
        if self.symbol and isinstance(self.symbol, FunctionSymbol):
            self.symbol.vars.append(symbol)

    def visit_for_statement(self, node: ForStatement, additional=None):
        old_scope = self.scope
        self.scope = Scope(self.scope)
        node.scope = self.scope

        super().visit_for_statement(node)

        self.scope = old_scope

    def visit_assignment_expression(self, node: Assignment, additional=None):
        current_scope = self.scope
        variable_name = node.left.name
        if not isinstance(node.left, Variable):
            raise Exception(f"Invalid assignment target.")

        symbol = current_scope.lookup(variable_name)
        if symbol is None:
            raise Exception(f"Variable '{variable_name}' is not defined.")
        node.left.symbol = symbol
        self.visit(node.right)

    def visit_variable(self, node: Variable, additional=None):
        current_scope = self.scope
        # 如果是函数声明，不需要检查变量是否定义
        if isinstance(additional, str) and additional == 'function':
            current_scope.put(node.name, node.symbol)
            return
        variable_name = node.name
        finded = current_scope.lookup(variable_name)
        if finded is False:
            raise Exception(f"Variable '{variable_name}' is not defined.")
        symbol = current_scope.get(variable_name)
        node.symbol = symbol


class RefResolver(SemanticAstVisitor):

    def __init__(self):
        super().__init__()
        self.scope = Scope()
        self.declared_vars: Mapping[Scope, Mapping[str, VariableSymbol]] = {}

    def visit_function_declaration(self, node: FunctionDeclaration, additional=None):
        old_scope = self.scope
        self.scope = node.scope

        assert self.scope is not None, "Scope is None"

        self.declared_vars[self.scope] = {}

        super().visit_function_declaration(node, additional='function')

        self.scope = old_scope

    def visit_block_statement(self, node: BlockStatement, additional=None):
        old_scope = self.scope
        self.scope = node.scope

        assert self.scope is not None, "Scope is None"

        self.declared_vars[self.scope] = {}

        super().visit_block_statement(node)

        self.scope = old_scope

    def visit_for_statement(self, node: ForStatement, additional=None):
        old_scope = self.scope
        self.scope = node.scope

        assert self.scope is not None, "Scope is None"

        self.declared_vars[self.scope] = {}

        super().visit_for_statement(node)

        self.scope = old_scope

    def visit_variable_declaration(self, node: VariableDeclaration, additional=None):
        current_scope = self.scope
        declared_vars = self.declared_vars[current_scope]

        variable_name = node.name
        symbol = current_scope.get(variable_name)
        if symbol is not None:
            declared_vars[variable_name] = symbol

        super().visit_variable_declaration(node)

    def visit_assignment_expression(self, node: Assignment, additional=None):
        current_scope = self.scope
        if not isinstance(node.left, Variable):
            raise Exception(f"Invalid assignment target.")

        declared_vars = self.declared_vars[current_scope]
        variable_name = node.left.name
        symbol = declared_vars.get(variable_name)
        if symbol is not None:
            node.left.symbol = symbol
        else:
            raise Exception(f"Variable '{variable_name}' is not defined.")

        node.left.declaration = symbol.decl
        self.visit(node.right)

    def visit_variable(self, node: Variable, additional=None):
        current_scope = self.scope
        if isinstance(additional, str) and additional == 'function':
            current_scope.put(node.name, node.symbol)
            return
        sym = self.find_variable(node, current_scope)
        if sym is not None:
            node.symbol = sym
            node.declaration = node.symbol.decl
        else:
            raise Exception(f"Variable '{node.name}' is not defined.")

    def find_variable(self, node: Variable, scope: Scope) -> Optional[VariableSymbol]:
        declared_vars: Mapping[str, VariableSymbol] = self.declared_vars[scope]
        symbol_in_scope = scope.get(node.name)
        if symbol_in_scope is not None:
            if declared_vars.get(node.name):
                return declared_vars[node.name]
            else:
                if isinstance(symbol_in_scope, VariableSymbol):
                    return symbol_in_scope
                else:
                    self.add_error(node, f"Variable '{node.name}' is not a variable.")
        else:
            if scope.parent is not None:
                return self.find_variable(node, scope.parent)
            else:
                self.add_error(node, f"Variable '{node.name}' is not defined.")
        return None

    def visit_call_expression(self, node: CallExpression, additional=None):
        current_scope = self.scope
        if node.name == "print":
            for arg in node.arguments:
                self.visit(arg)
            node.callee = built_ins.find(node.name)
            return None
        elif node.name == "input":
            return None
        elif node.name == "int":
            return None
        elif node.name == "float":
            return None
        elif node.name == "str":
            return None
        elif node.name == "bool":
            return None
        elif node.name == "void":
            return None
        elif node.name == "len":
            return None
        else:
            existed = current_scope.lookup(node.name)
            if existed is False:
                self.add_error(node, f"Function '{node.name}' is not defined.")
            else:
                symbol = current_scope.get(node.name)
                node.symbol = symbol
                node.callee = symbol.decl


class SemanticAnalyzer:
    def __init__(self):
        pass

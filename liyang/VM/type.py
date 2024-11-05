#!/usr/bin/env python
# -*- coding: utf-8 -*-
# TODO: 循环引用检查如何实现，可以参考Python的类型系统
# 类型系统
from typing import List
from VM._typ import Type, ObjectType, Union, Any


class SystemType(Type):
    # 系统类型
    object_type = ObjectType("Object")

    any_type = ObjectType("Any", [object_type])

    string_type = ObjectType("String", [object_type])
    int_type = ObjectType("Int", [object_type])
    decimal_type = ObjectType("Decimal", [object_type])
    bool_type = ObjectType("Bool", [object_type])
    void_type = ObjectType("Void", [object_type])
    null_type = ObjectType("Null", [object_type])

    @staticmethod
    def is_system_type(t: Type):
        return t in [SystemType.string_type, SystemType.int_type, SystemType.decimal_type, SystemType.bool_type, SystemType.void_type, SystemType.null_type]


class PrimitiveType(ObjectType):
    def __init__(self, name: Union[str, Any], index: int = 0):
        super().__init__(name, [SystemType.object_type], index)


class StructType(Type):
    def __init__(self, name: Union[str, Any], index: int = 0, fields: dict[str, Type] = {}):
        super().__init__(name, index)
        self.fields = fields

    def less_eq(self, other):
        if not isinstance(other, StructType):
            return False
        if len(self.fields) != len(other.fields):
            return False
        for key in self.fields:
            if key not in other.fields or not self.fields[key].less_eq(other.fields[key]):
                return False
        return True


class FunctionType(Type):
    def __init__(self, name: Union[str, Any], param_types: List[Type], return_type: Type, index: int = 0):
        super().__init__(name, index)
        self.param_types = param_types
        self.return_type = return_type

    def less_eq(self, other):
        if not isinstance(other, FunctionType):
            return False
        if len(self.param_types) != len(other.param_types):
            return False
        for i in range(len(self.param_types)):
            if not self.param_types[i].less_eq(other.param_types[i]):
                return False
        return self.return_type.less_eq(other.return_type)


class TypeVisitor:
    def visit(self, t: Type):
        if isinstance(t, ObjectType):
            return self.visit_object(t)
        elif isinstance(t, PrimitiveType):
            return self.visit_primitive(t)
        elif isinstance(t, StructType):
            return self.visit_struct(t)
        elif isinstance(t, FunctionType):
            return self.visit_function(t)
        else:
            raise Exception("Unknown type")

    def visit_object(self, t: ObjectType):
        pass

    def visit_primitive(self, t: PrimitiveType):
        pass

    def visit_struct(self, t: StructType):
        pass

    def visit_function(self, t: FunctionType):
        pass

    def visit_system(self, t: SystemType):
        pass

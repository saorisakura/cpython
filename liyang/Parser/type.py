#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 类型系统
from abc import ABC, abstractmethod
from typing import List


class Type(ABC):
    def __init__(self, name):
        self.name = name

    @abstractmethod
    def less_eq(self, other):
        pass


class ObjectType(Type):
    def __init__(self, name: str, upper_bound: List[Type] = [], lower_bound: List[Type] = []):
        super().__init__(name)
        self.upper_bound = upper_bound
        self.lower_bound = lower_bound

    def less_eq(self, other):
        return self == other


class SystemType(Type):
    pass

from abc import ABC, abstractmethod
from typing import List, Union, Any


class Type(ABC):
    def __init__(self, name: Union[str, Any], index: int = 0):
        self.index = index  # 用于区分重载
        if isinstance(name, str):
            self.name = name
        else:
            self.name = f'function_{name}_{index+1}'

    @abstractmethod
    def less_eq(self, other):
        pass


class ObjectType(Type):
    def __init__(self, name: Union[str, Any], index: int = 0, upper_bound: List[Type] = [], lower_bound: List[Type] = []):
        super().__init__(name, index)
        # 支持继承和多态
        self.upper_bound = upper_bound
        self.lower_bound = lower_bound

    def less_eq(self, other):
        return self == other

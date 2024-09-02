"""符号表"""
from enum import Enum, auto
from typing import NamedTuple


class Kind(Enum):
    STATIC = auto()
    FIELD = auto()
    ARG = auto()
    VAR = auto()


class SymbolTableItem(NamedTuple):
    type_: str
    kind: Kind
    index: int


class SymbolTable:
    def __init__(self):
        self.class_name = None
        self.subroutine_name = None

        self.static_index = 0
        self.field_index = 0
        self.class_table: dict[str, SymbolTableItem] = {}

        self.arg_index = 0
        self.var_index = 0
        self.subroutine_table: dict[str, SymbolTableItem] = {}

        self.while_count = 0
        self.if_count = 0

    def start_subroutine(self, subroutine_name: str) -> None:
        self.arg_index = 0
        self.var_index = 0
        self.subroutine_name = subroutine_name
        self.subroutine_table: dict[str, SymbolTableItem] = {}

        self.while_count = 0
        self.if_count = 0

    def define(self, name: str, type_: str, kind: Kind) -> None:
        if kind == Kind.STATIC:
            self.class_table[name] = SymbolTableItem(
                type_, kind, self.static_index
            )
            self.static_index += 1
        elif kind == Kind.FIELD:
            self.class_table[name] = SymbolTableItem(
                type_, kind, self.field_index
            )
            self.field_index += 1
        elif kind == Kind.ARG:
            self.subroutine_table[name] = SymbolTableItem(
                type_, kind, self.arg_index
            )
            self.arg_index += 1
        elif kind == Kind.VAR:
            self.subroutine_table[name] = SymbolTableItem(
                type_, kind, self.var_index
            )
            self.var_index += 1
        else:
            raise ValueError(f'Invalid kind: {kind}')

    def var_count(self, kind: Kind) -> int:
        if kind == Kind.STATIC:
            return self.static_index
        elif kind == Kind.FIELD:
            return self.field_index
        elif kind == Kind.ARG:
            return self.arg_index
        elif kind == Kind.VAR:
            return self.var_index
        else:
            raise ValueError(f'Invalid kind: {kind}')

    def kind_of(self, name: str) -> Kind | None:
        if name in self.subroutine_table:
            result = self.subroutine_table[name]
            return result.kind
        elif name in self.class_table:
            result = self.class_table[name]
            return result.kind
        else:
            return None

    def type_of(self, name: str) -> str:
        if name in self.subroutine_table:
            result = self.subroutine_table[name]
            return result.type_
        elif name in self.class_table:
            result = self.class_table[name]
            return result.type_
        else:
            # name 是类名或方法名，直接原样返回
            return name

    def index_of(self, name: str) -> int:
        if name in self.subroutine_table:
            result = self.subroutine_table[name]
            return result.index
        elif name in self.class_table:
            result = self.class_table[name]
            return result.index
        else:
            raise ValueError(f'{name} 是类名或方法名，不能作为变量名')

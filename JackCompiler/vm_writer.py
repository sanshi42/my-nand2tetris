"""
生成 VM 代码的输出模块：输出到 VM 代码到特定的目标文件
"""
from enum import Enum, auto
from pathlib import Path


class Segment(Enum):
    CONSTANT = auto()
    ARGUMENT = auto()
    LOCAL = auto()
    STATIC = auto()
    POINTER = auto()
    THIS = auto()
    THAT = auto()
    TEMP = auto()


class Command(Enum):
    ADD = auto()
    SUB = auto()
    NEG = auto()
    EQ = auto()
    GT = auto()
    LT = auto()
    AND = auto()
    OR = auto()
    NOT = auto()


class VMWriter:
    def __init__(self, output_file: Path):
        self.output_file = output_file

    def write_push(self, segment: Segment, index: int) -> None:
        result = f'push {segment.name.lower()} {index}'
        with self.output_file.open('a') as f:
            f.write(result + '\n')

    def write_pop(self, segment: Segment, index: int) -> None:
        result = f'pop {segment.name.lower()} {index}'
        with self.output_file.open('a') as f:
            f.write(result + '\n')

    def write_arithmetic(self, command: Command) -> None:
        result = f'{command.name.lower()}'
        with self.output_file.open('a') as f:
            f.write(result + '\n')

    def write_label(self, label: str) -> None:
        result = f'label {label}'
        with self.output_file.open('a') as f:
            f.write(result + '\n')

    def write_goto(self, label: str) -> None:
        result = f'goto {label}'
        with self.output_file.open('a') as f:
            f.write(result + '\n')

    def write_if(self, label: str) -> None:
        result = f'if-goto {label}'
        with self.output_file.open('a') as f:
            f.write(result + '\n')

    def write_call(self, name: str, n_args: int) -> None:
        result = f'call {name} {n_args}'
        with self.output_file.open('a') as f:
            f.write(result + '\n')

    def write_function(self, name: str, n_locals: int) -> None:
        result = f'function {name} {n_locals}'
        with self.output_file.open('a') as f:
            f.write(result + '\n')

    def write_return(self) -> None:
        result = 'return'
        with self.output_file.open('a') as f:
            f.write(result + '\n')

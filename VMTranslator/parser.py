"""
主要功能：将 VM 命令分解为其所表达的内在含义（域和符号）
"""

from typing import List

COMMAND_TYPE_DICT = {
    "return": "C_RETURN",
    "function": "C_FUNCTION",
    "call": "C_CALL",
    "goto": "C_GOTO",
    "if-goto": "C_IF",
    "label": "C_LABEL",
    "push": "C_PUSH",
    "pop": "C_POP",
    "add": "C_ARITHMETIC",
    "sub": "C_ARITHMETIC",
    "neg": "C_ARITHMETIC",
    "eq": "C_ARITHMETIC",
    "gt": "C_ARITHMETIC",
    "lt": "C_ARITHMETIC",
    "and": "C_ARITHMETIC",
    "or": "C_ARITHMETIC",
    "not": "C_ARITHMETIC",
}


class Parser:
    def __init__(self, command_lines: List[str]) -> None:
        """"""
        self.command_lines = []
        for line in command_lines:
            line = self._remove_comments(line.strip())
            line = line.strip()
            if line:
                self.command_lines.append(line)

    def _remove_comments(self, line: str) -> str:
        if "//" in line:
            line = line.split("//")[0]
        return line

    def has_more_commands(self) -> bool:
        return len(self.command_lines) > 0

    def advance(self) -> str:
        if self.has_more_commands():
            return self.command_lines.pop(0)
        else:
            raise ValueError("No more commands")

    def command_type(self) -> str:
        command_line = self.command_lines[0].split()
        if command_line[0] not in COMMAND_TYPE_DICT:
            raise ValueError("Invalid command")
        return COMMAND_TYPE_DICT[command_line[0]]

    def arg1(self) -> str:
        """返回当前命令的第一个参数"""
        match self.command_type():
            case "C_ARITHMETIC":
                return self.command_lines[0]
            case (
                "C_PUSH"
                | "C_POP"
                | "C_FUNCTION"
                | "C_CALL"
                | "C_LABEL"
                | "C_GOTO"
                | "C_IF"
            ):
                command_line = self.command_lines[0].split()
                return command_line[1]
            case "C_RETURN":
                raise ValueError("Return command has no first  argument")
            case _:
                raise ValueError("Invalid command")

    def arg2(self) -> int:
        command_line = self.command_lines[0].split()
        match self.command_type():
            case "C_PUSH" | "C_POP" | "C_FUNCTION" | "C_CALL":
                return int(command_line[2])
            case _:
                raise ValueError("Invalid command")

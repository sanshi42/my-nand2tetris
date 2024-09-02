"""
主要功能：将汇编命令分解为其所表达的内在含义（域和符号）。
"""
from typing import List


class Parser:
    """封装对输入代码的访问操作。

    功能包括：
    1. 读取汇编语言命令并对其进行解析；
    2. 提供“方便访问汇编命令成分（域和符号）”的方案；
    3. 去掉所有的空格和注释。
    """

    def __init__(self, command_lines: List[str]):
        """打开输入文本/输入流，为语法解析作准备。"""
        self.lines = []
        for command_line in command_lines:
            line = self._remove_comment(command_line)
            if line:
                self.lines.append(line)

    def _remove_comment(self, line: str) -> str | None:
        """去掉注释。"""
        if "//" in line:
            line = line.split("//")[0]
        return line if line else None

    def has_more_commands(self) -> bool:
        """判断是否还有更多命令。"""
        return len(self.lines) > 0

    def advance(self):
        """从输入中读取下一条命令。"""
        if self.has_more_commands():
            return self.lines.pop(0)
        return None  # TODO 应该抛出异常的，需要在测试修改

    def command_type(self) -> str:
        """返回当前命令的类型。"""
        if self.lines[0].startswith("@"):
            return "A_COMMAND"
        elif self.lines[0].startswith("("):
            return "L_COMMAND"
        else:
            return "C_COMMAND"

    def symbol(self) -> str:
        """返回当前命令的符号或十进制值（当且仅当当前命令为A-指令或L-指令时）。"""
        if self.command_type() == "A_COMMAND":
            return self.lines[0][1:]
        elif self.command_type() == "L_COMMAND":
            return self.lines[0][1:-1]
        else:
            raise Exception("symbol() called when command_type() != A_COMMAND")

    def dest(self) -> str:
        """返回当前C-指令的dest助记符。"""
        if self.command_type() == "C_COMMAND":
            result = self.lines[0].split("=")[0]
            return result if result else ""
        else:
            raise Exception("dest() called when command_type() != C_COMMAND")

    def comp(self) -> str:
        """返回当前C-指令的comp助记符。"""
        if self.command_type() == "C_COMMAND":
            try:
                result = self.lines[0].split("=")[1].split(";")[0]
                return result if result else ""
            except Exception:
                return self.lines[0].split(";")[0]
        else:
            raise Exception("comp() called when command_type() != C_COMMAND")

    def jump(self) -> str:
        """返回当前C-指令的jump助记符。"""
        if self.command_type() == "C_COMMAND":
            try:
                return self.lines[0].split(";")[1]
            except Exception:
                return ""
        else:
            raise Exception("jump() called when command_type() != C_COMMAND")

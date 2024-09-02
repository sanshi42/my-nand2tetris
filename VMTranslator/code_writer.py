"""将 VM 命令翻译成 Hack 汇编代码"""

from typing import List

ARITHMETIC_LOGIC_MAPPING = {
    "add": "M=D+M",
    "sub": "M=M-D",
    "neg": "M=-M",
    "eq": "D;JNE",
    "gt": "D;JLE",
    "lt": "D;JGE",
    "and": "M=D&M",
    "or": "M=D|M",
    "not": "M=!M",
}
MEMORY_SEGMENT_MAPPING = {
    "local": "LCL",
    "argument": "ARG",
    "this": "THIS",
    "that": "THAT",
    "temp": "5",
    "pointer": "3",
    "static": "R16",
}


class CodeWriter:
    """删除了直接写入文件，而是返回一个列表"""

    def __init__(self, file_name: str = '') -> None:
        """需要给定目标文件名，用于生成静态变量名"""
        self.label_index = 0
        self.return_index = 0
        self.file_name = file_name.split(".")[0]

    @staticmethod
    def write_init() -> List[str]:
        """初始化"""
        init_command = []
        # 初始寄存器赋值
        initial_register_map = {
            "SP": "256",
            "LCL": "1",
            "ARG": "2",
            "THIS": "3",
            "THAT": "4",
        }
        for register, value in initial_register_map.items():
            init_command += [
                f"@{value}",
                "D=A",
                f"@{register}",
                "M=D",
            ]

        # 将寄存器中的值设置到全局堆栈中
        push_D = [
            "@SP",
            "A=M",
            "M=D",
            "@SP",
            "M=M+1",
        ]
        # push 返回地址
        init_command += ["@bootstrap", "D=A"] + push_D
        # push 其他设置
        for register in ["LCL", "ARG", "THIS", "THAT"]:
            init_command += [f"@{register}", "D=M"] + push_D

        # ARG=SP-n-5
        init_command += ["@5", "D=A", "@SP", "D=M-D", "@ARG", "M=D"]
        # LCL=CP
        init_command += ["@SP", "D=M", "@LCL", "M=D"]
        init_command += ["@Sys.init", "0;JMP", "(bootstrap)"]
        return init_command

    def set_file_name(self, file_name: str) -> None:
        self.file_name = file_name.split(".")[0]

    def write_arithmetic(self, command: str) -> List[str]:
        sepcific_command_lines = ARITHMETIC_LOGIC_MAPPING[command]
        command_comment = f"// {command}"
        if command in ["not", "neg"]:
            generic_command_lines = ["@SP", "A=M-1"]
            return [command_comment] + generic_command_lines + [sepcific_command_lines]
        elif command in ["eq", "gt", "lt"]:
            generic_command_lines = ["@SP", "AM=M-1", "D=M", "A=A-1", "D=M-D", "M=0"]
            label = f"{command}_{self.label_index}"
            self.label_index += 1
            return (
                [command_comment]
                + generic_command_lines
                + [
                    f"@{label}",
                    sepcific_command_lines,
                    "@SP",
                    "A=M-1",
                    "M=-1",
                    f"({label})",
                ]
            )
        elif command in ["add", "sub", "and", "or"]:
            generic_command_lines = ["@SP", "AM=M-1", "D=M", "A=A-1"]
            return [command_comment] + generic_command_lines + [sepcific_command_lines]
        else:
            raise ValueError(f"Invalid command: {command}")

    def write_push(self, segment: str, index: int | str) -> List[str]:
        """将 segment[index] 的值压入栈顶"""
        command_comment = f"// push {segment} {index}"
        if segment == "constant":
            command = [
                f"@{index}",
                "D=A",
            ]
        elif segment in ["local", "argument", "this", "that"]:
            command = [
                f"@{index}",
                "D=A",
                f"@{MEMORY_SEGMENT_MAPPING[segment]}",
                "A=D+M",
                "D=M",
            ]
        elif segment in ["pointer", "temp"]:
            command = [
                f"@{index}",
                "D=A",
                f"@{MEMORY_SEGMENT_MAPPING[segment]}",
                "A=D+A",
                "D=M",
            ]
        elif segment == "static":
            command = [
                f"@{self.file_name.split('.')[0]}.{index}",
                "D=M",
            ]
        else:
            raise ValueError(f"Invalid segment: {segment}")
        # 将 D 值压入栈顶，并调整栈顶指针
        command += [
            "@SP",
            "A=M",
            "M=D",
            "@SP",
            "M=M+1",
        ]
        return [command_comment] + command

    def write_pop(self, segment: str, index: int) -> List[str]:
        """将栈顶的值弹出到 segment[index]"""
        command_comment = f"// pop {segment} {index}"
        if segment in ["local", "argument", "this", "that"]:
            # 取出segment[index]地址放到 R13
            command = [
                f"@{index}",
                "D=A",
                f"@{MEMORY_SEGMENT_MAPPING[segment]}",
                "D=D+M",
                "@R13",
                "M=D",
            ]
        elif segment in ["pointer", "temp"]:
            # 取出segment[index]地址放到 R13
            command = [
                f"@{index}",
                "D=A",
                f"@{MEMORY_SEGMENT_MAPPING[segment]}",
                "D=D+A",
                "@R13",
                "M=D",
            ]
        elif segment == "static":
            # 将栈顶元素弹出然后赋值给静态变量名，不用要再弹出
            command = [
                f"@{self.file_name.split('.')[0]}.{index}",
                "D=A",  # 只要传递地址就行，因为本身就是地址
                "@R13",
                "M=D",
            ]
        else:
            raise ValueError(f"Invalid segment: {segment}")
        # 弹出栈顶的值放到 segment[index]
        command += [
            "@SP",
            "AM=M-1",
            "D=M",
            "@R13",
            "A=M",
            "M=D",
        ]
        return [command_comment] + command

    def write_label(self, label: str) -> List[str]:
        """生成 label"""
        return [f"// {self.file_name}${label}", f"({self.file_name}${label})"]

    def write_goto(self, label: str) -> List[str]:
        """跳转到 label"""
        return [
            f"// goto {self.file_name}${label}",
            f"@{self.file_name}${label}",
            "0;JMP",
        ]

    def write_if(self, label: str) -> List[str]:
        """如果栈顶的值为f非零，跳转到 label"""
        return [
            f"// if-goto {self.file_name}${label}",
            "@SP",
            "AM=M-1",
            "D=M",
            f"@{self.file_name}${label}",
            "D;JNE",
        ]

    def write_function(self, function_name: str, num_locals: int) -> List[str]:
        """函数命令

        形式为 function {funcition_name} {num_locals}，表示函数名为 {function_name}，
        函数的局部变量数量为 {num_locals}
        """
        command = [f"// function {function_name} {num_locals}", f"({function_name})"]
        for _ in range(num_locals):
            command += ["@SP", "A=M", "M=0", "@SP", "M=M+1"]
        return command

    def write_call(self, function_name: str, num_args: int) -> List[str]:
        """在调用函数之前，需要先将函数的返回地址和参数压入栈中"""
        comment = f"// call {function_name} {num_args}"
        push_D = ["@SP", "A=M", "M=D", "@SP", "M=M+1"]
        label = f"End${function_name}${self.return_index}"
        self.return_index += 1
        command = ["@" + label, "D=A"] + push_D
        for symbol in ["LCL", "ARG", "THIS", "THAT"]:
            command += [
                f"@{symbol}",
                "D=M",
            ] + push_D
        return (
            [comment]
            + command
            + [
                f"@{num_args + 5}",
                "D=A",
                "@SP",
                "D=M-D",
                "@ARG",
                "M=D",  # ARG = SP - n - 5
                "@SP",
                "D=M",
                "@LCL",
                "M=D",  # LCL = SP
                f"@{function_name}",
                "0;JMP",  # goto f
                f"({label})",
            ]
        )

    def write_return(self) -> List[str]:
        """返回命令

        伪代码如下：
        1. FRAM = LCL
        2. RET = *(FRAM - 5)
        3. *ARG = pop()
        4. SP = ARG + 1
        5. THAT = *(FRAM - 1)
        6. THIS = *(FRAM - 2)
        7. ARG = *(FRAM - 3)
        8. LCL = *(FRAM - 4)
        9. goto RET
        """
        command = [
            "// return",
            "@LCL",
            "D=M",
            "@R13",
            "M=D",  # FRAME = LCL
            "@5",
            "D=A",
            "@R13",
            "A=M-D",
            "D=M",
            "@R14",
            "M=D",  # RET = *(FRAME - 5)
            "@SP",
            "AM=M-1",
            "D=M",
            "@ARG",
            "A=M",
            "M=D",  # *ARG = pop()
            "@ARG",
            "D=M+1",
            "@SP",
            "M=D",  # SP = ARG+1
        ]
        # 依次赋值THAT, THIS, ARG, LCL
        command += ["@R13", "A=M-1", "D=M", "@THAT", "M=D"]
        for i, seg in enumerate(["THIS", "ARG", "LCL"]):
            command += [
                f"@{i+2}",
                "D=A",
                "@R13",
                "A=M-D",
                "D=M",
                f"@{seg}",
                "M=D",
            ]
        # goto RET
        command += [
            "@R14",
            "A=M",
            "0;JMP",
        ]
        return command

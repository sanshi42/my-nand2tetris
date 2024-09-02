from parser import Parser
from pathlib import Path

from code_writer import CodeWriter


def main(source_file_path: Path):
    """VM to Assembly Code Compiler

    Args:
        source_file_path (Path): 单一的 file_name.vm 文件路径，或者包含多个 .vm 文件的 directory_name 文件夹路径

    Output:
        file_name.asm 文件 或 directory_name.asm 文件

    解析过程：
    1. 构造一个 CodeWriter 对象
    2. 如果输入的是 .vm 文件，则
        - 构造一个 Parser 对象去处理输入文件
        - 遍历输入文件，解析每一行并生成对应的编码
    3. 如果输入的是 .vm 文件夹，则
        - 遍历文件夹，对每个 .vm 文件进行处理
    """
    dest_command = []
    if source_file_path.is_dir():
        """如果输入的是文件夹，则遍历文件夹，对每个 .vm 文件进行处理，这些文件会被编译成一个 .asm 文件"""
        file_names = [
            file_name.name
            for file_name in source_file_path.iterdir()
            if file_name.suffix == ".vm"
        ]
        dest_command += CodeWriter.write_init()

        code_writer = CodeWriter(file_name='')
        for file_name in file_names:
            with open(source_file_path / file_name, "r") as f:
                command_line = f.readlines()
            parser = Parser(command_lines=command_line)
            code_writer.set_file_name(file_name=file_name)
            while parser.has_more_commands():
                command_type = parser.command_type()
                if command_type == "C_ARITHMETIC":
                    code_lines = code_writer.write_arithmetic(command=parser.arg1())
                elif command_type == "C_PUSH":
                    code_lines = code_writer.write_push(
                        segment=parser.arg1(), index=parser.arg2()
                    )
                elif command_type == "C_POP":
                    code_lines = code_writer.write_pop(
                        segment=parser.arg1(), index=parser.arg2()
                    )
                elif command_type == "C_LABEL":
                    code_lines = code_writer.write_label(label=parser.arg1())
                elif command_type == "C_GOTO":
                    code_lines = code_writer.write_goto(label=parser.arg1())
                elif command_type == "C_IF":
                    code_lines = code_writer.write_if(label=parser.arg1())
                elif command_type == "C_FUNCTION":
                    code_lines = code_writer.write_function(
                        function_name=parser.arg1(), num_locals=parser.arg2()
                    )
                elif command_type == "C_RETURN":
                    code_lines = code_writer.write_return()
                elif command_type == "C_CALL":
                    code_lines = code_writer.write_call(
                        function_name=parser.arg1(), num_args=parser.arg2()
                    )
                else:
                    raise ValueError(f"Invalid command type: {command_type}")
                dest_command.extend(code_lines)
                parser.advance()

        destination_file_path = source_file_path / (
            source_file_path.name + ".asm"
        )

        with open(destination_file_path, "w") as f:
            for command in dest_command:
                f.write(f"{command}\n")
    else:
        with open(source_file_path, "r") as f:
            command_lines = f.readlines()
        parser = Parser(command_lines=command_lines)
        code_writer = CodeWriter(file_name=source_file_path.name)
        dest_command = []
        while parser.has_more_commands():
            command_type = parser.command_type()
            if command_type == "C_ARITHMETIC":
                code_lines = code_writer.write_arithmetic(command=parser.arg1())
                dest_command.extend(code_lines)
            elif command_type == "C_PUSH":
                code_lines = code_writer.write_push(
                    segment=parser.arg1(), index=parser.arg2()
                )
                dest_command.extend(code_lines)
            elif command_type == "C_POP":
                code_lines = code_writer.write_pop(
                    segment=parser.arg1(), index=parser.arg2()
                )
                dest_command.extend(code_lines)
            elif command_type == "C_LABEL":
                code_lines = code_writer.write_label(label=parser.arg1())
                dest_command.extend(code_lines)
            elif command_type == "C_GOTO":
                code_lines = code_writer.write_goto(label=parser.arg1())
                dest_command.extend(code_lines)
            elif command_type == "C_IF":
                code_lines = code_writer.write_if(label=parser.arg1())
                dest_command.extend(code_lines)
            elif command_type == "C_FUNCTION":
                code_lines = code_writer.write_function(
                    function_name=parser.arg1(), num_locals=parser.arg2()
                )
                dest_command.extend(code_lines)
            elif command_type == "C_RETURN":
                code_lines = code_writer.write_return()
                dest_command.extend(code_lines)
            elif command_type == "C_CALL":
                code_lines = code_writer.write_call(
                    function_name=parser.arg1(), num_args=parser.arg2()
                )
                dest_command.extend(code_lines)
            else:
                raise ValueError(f"Invalid command type: {command_type}")
            parser.advance()

        destination_file_path = source_file_path.parent / (
            source_file_path.name.split(".")[0] + ".asm"
        )

        with open(destination_file_path, "w") as f:
            for command in dest_command:
                f.write(f"{command}\n")


if __name__ == "__main__":
    FUNCTION_CALLS_DATA_ROOT = Path(r"data/FunctionCalls")
    file_name = "NestedCall"
    source_file_path = FUNCTION_CALLS_DATA_ROOT / file_name
    main(source_file_path=source_file_path)

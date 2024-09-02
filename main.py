import pathlib
from parser import Parser

from my_code import MyCode
from symbol_table import SymbolTable

DATA_ROOT = pathlib.Path(r"data")


def main(source_file_name: str, dest_file_name: str):
    source_file_path = DATA_ROOT / source_file_name
    with open(source_file_path, "r") as f:
        command_lines = f.readlines()
    command_lines = [line.strip() for line in command_lines]

    # 第一遍：构建符号表但不生成代码
    commmand_line_num = 0
    parser = Parser(command_lines=command_lines)
    symbol_table = SymbolTable()
    while parser.has_more_commands():
        command_type = parser.command_type()
        if command_type == "L_COMMAND":
            com = parser.symbol()
            if not symbol_table.contains(com):
                # 仅仅保存下一条命令的地址作为其值
                symbol_table.add_entry(com, commmand_line_num)
        else:
            commmand_line_num += 1
        parser.advance()  # 下一条命令

    # 第二遍：生成代码
    mycode = MyCode(symbol_table=symbol_table)
    parser = Parser(command_lines=command_lines)
    dest_command = []
    register_num = 16
    # 将源文件转换为目标文件添加到目标文件中
    while parser.has_more_commands():
        command_type = parser.command_type()
        if command_type == "A_COMMAND":
            com = parser.symbol()
            if not com.isdecimal() and not symbol_table.contains(com):
                # 从16开始增加地址
                symbol_table.add_entry(com, register_num)
                register_num += 1
            dest_command.append("0" + mycode.symbol(com))
        elif command_type == "C_COMMAND":
            dest_command.append(
                "111"
                + MyCode.comp(parser.comp())
                + MyCode.dest(parser.dest())
                + MyCode.jump(parser.jump())
            )
        elif command_type == "L_COMMAND":
            pass
        parser.advance()  # 下一条命令

    dest_file_path = DATA_ROOT / dest_file_name
    with open(dest_file_path, "w") as f:
        for line in dest_command:
            f.write(line + "\n")
    return dest_command


if __name__ == "__main__":
    main("add/Add.asm", "add/Add.hack")

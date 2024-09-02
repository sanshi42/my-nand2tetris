from parser import Parser
from pathlib import Path

import pytest

from code_writer import CodeWriter
from main import main


class TestParser:
    def test_init(self):
        parser = Parser(["push constant 1"])
        assert parser.command_lines == ["push constant 1"]

        file_name = "SimpleAdd"
        SIMPLE_ARITHMETIC_DATA_ROOT = Path(r"data/StackArithmetic")
        file_path = SIMPLE_ARITHMETIC_DATA_ROOT / file_name / (file_name + ".vm")
        with open(file_path, "r") as f:
            command_lines = f.readlines()
        parser = Parser(command_lines=command_lines)

        assert parser.command_lines == [
            "push constant 7",
            "push constant 8",
            "add",
        ]

    def test_has_more_commands(self):
        parser = Parser(["push constant 1"])
        assert parser.has_more_commands() is True

    def test_advance(self):
        parser1 = Parser(["push constant 1"])
        assert parser1.command_lines == ["push constant 1"]

        parser1.advance()
        assert parser1.command_lines == []

    def test_command_type(self):
        parser1 = Parser(["push constant 1"])
        assert parser1.command_type() == "C_PUSH"

        parser2 = Parser(["pop constant 1"])
        assert parser2.command_type() == "C_POP"

        parser3 = Parser(["add"])
        assert parser3.command_type() == "C_ARITHMETIC"

        parser4 = Parser(["label L1"])
        assert parser4.command_type() == "C_LABEL"

        parser5 = Parser(["goto L1"])
        assert parser5.command_type() == "C_GOTO"

        parser6 = Parser(["if-goto L1"])
        assert parser6.command_type() == "C_IF"

        parser7 = Parser(["function f 1"])
        assert parser7.command_type() == "C_FUNCTION"

        parser8 = Parser(["return"])
        assert parser8.command_type() == "C_RETURN"

        parser9 = Parser(["call f 1"])
        assert parser9.command_type() == "C_CALL"

    def test_arg1(self):
        parser1 = Parser(["push constant 1"])
        assert parser1.arg1() == "constant"

        parser2 = Parser(["add"])
        assert parser2.arg1() == "add"

        parser3 = Parser(["return"])
        with pytest.raises(ValueError):
            parser3.arg1()

    def test_arg2(self):
        parser1 = Parser(["push constant 1"])
        assert parser1.arg2() == 1

        parser2 = Parser(["add"])
        with pytest.raises(ValueError):
            parser2.arg2()


class TestCodeWriter:
    def test_arithmetic(self):
        # arithmetic_ = ["add", "sub", "neg", "eq", "gt", "lt", "and", "or", "not"]
        code_writer = CodeWriter(file_name="test.vm")

        assert code_writer.write_arithmetic("add") == [
            "// add",
            "@SP",
            "AM=M-1",
            "D=M",
            "A=A-1",
            "M=D+M",
        ]

        assert code_writer.write_arithmetic("sub") == [
            "// sub",
            "@SP",
            "AM=M-1",
            "D=M",
            "A=A-1",
            "M=M-D",
        ]

        assert code_writer.write_arithmetic("neg") == [
            "// neg",
            "@SP",
            "A=M-1",
            "M=-M",
        ]

        assert code_writer.write_arithmetic("eq") == [
            "// eq",
            "@SP",
            "AM=M-1",
            "D=M",
            "A=A-1",
            "D=M-D",
            "M=-1",  # -1表示真，0表示假
            "@eq_0",
            "D;JEQ",
            "@SP",
            "A=M-1",
            "M=0",
            "(eq_0)",
        ]

    def test_push(self):
        code_writer = CodeWriter(file_name="test.vm")
        assert code_writer.write_push("constant", 1) == [
            "// push constant 1",
            "@1",
            "D=A",
            "@SP",
            "A=M",
            "M=D",
            "@SP",
            "M=M+1",
        ]
        assert code_writer.write_push("local", 2) == [
            "// push local 2",
            "@2",
            "D=A",
            "@LCL",
            "A=D+M",
            "D=M",
            "@SP",
            "A=M",
            "M=D",
            "@SP",
            "M=M+1",
        ]
        assert code_writer.write_push("pointer", 0) == [
            "// push pointer 0",
            "@0",
            "D=A",
            "@R3",
            "A=D+A",
            "D=M",
            "@SP",
            "A=M",
            "M=D",
            "@SP",
            "M=M+1",
        ]
        assert code_writer.write_push("argument", 2) == [
            "// push argument 2",
            "@2",
            "D=A",
            "@ARG",
            "A=D+M",
            "D=M",
            "@SP",
            "A=M",
            "M=D",
            "@SP",
            "M=M+1",
        ]
        assert code_writer.write_push("static", 0) == [
            "// push static 0",
            "@test.0",
            "D=M",
            "@SP",
            "A=M",
            "M=D",
            "@SP",
            "M=M+1",
        ]

    def test_pop(self):
        code_writer = CodeWriter(file_name="test.vm")
        assert code_writer.write_pop("local", 2) == [
            "// pop local 2",
            "@2",
            "D=A",
            "@LCL",
            "D=D+M",
            "@R13",
            "M=D",  # 让 R13 获得指向 local[2] 的地址
            "@SP",
            "AM=M-1",
            "D=M",
            "@R13",  # 先弹出栈顶的值，然后存储到 local[2] 的地址
            "A=M",
            "M=D",
        ]
        assert code_writer.write_pop("pointer", 0) == [
            "// pop pointer 0",
            "@0",
            "D=A",
            "@3",
            "D=D+A",
            "@R13",
            "M=D",
            "@SP",
            "AM=M-1",
            "D=M",
            "@R13",
            "A=M",
            "M=D",
        ]
        assert code_writer.write_pop("argument", 2) == [
            "// pop argument 2",
            "@2",
            "D=A",
            "@ARG",
            "D=D+M",
            "@R13",
            "M=D",
            "@SP",
            "AM=M-1",
            "D=M",
            "@R13",  # 先弹出栈顶的值，然后存储到 argument[2] 的地址
            "A=M",
            "M=D",
        ]
        assert code_writer.write_pop("this", 2) == [
            "// pop this 2",
            "@2",
            "D=A",
            "@THIS",
            "D=D+M",
            "@R13",
            "M=D",
            "@SP",
            "AM=M-1",
            "D=M",
            "@R13",
            "A=M",
            "M=D",
        ]
        assert code_writer.write_pop("that", 2) == [
            "// pop that 2",
            "@2",
            "D=A",
            "@THAT",
            "D=D+M",
            "@R13",
            "M=D",
            "@SP",
            "AM=M-1",
            "D=M",
            "@R13",
            "A=M",
            "M=D",
        ]
        assert code_writer.write_pop("static", 0) == [
            "// pop static 0",
            "@test.0",
            "D=A",
            "@R13",
            "M=D",
            "@SP",
            "AM=M-1",
            "D=M",
            "@R13",
            "A=M",
            "M=D",
        ]

        assert code_writer.write_pop("temp", 0) == [
            "// pop temp 0",
            "@0",
            "D=A",
            "@R5",
            "D=D+A",
            "@R13",
            "M=D",
            "@SP",
            "AM=M-1",
            "D=M",
            "@R13",
            "A=M",
            "M=D",
        ]

    def test_label(self):
        code_writer = CodeWriter(file_name="test.vm")
        assert code_writer.write_label("L1") == [
            "// test$L1",
            "(test$L1)",
        ]

    def test_goto(self):
        code_writer = CodeWriter(file_name="test.vm")
        assert code_writer.write_goto("L1") == [
            "// goto test$L1",
            "@test$L1",
            "0;JMP",
        ]

    def test_if(self):
        code_writer = CodeWriter(file_name="test.vm")
        assert code_writer.write_if("L1") == [
            "// if-goto test$L1",
            "@SP",
            "AM=M-1",
            "D=M",
            "@test$L1",
            "D;JNE",
        ]

    def test_function(self):
        code_writer = CodeWriter(file_name="test.vm")
        assert code_writer.write_function("f", 1) == [
            "// function f 1",
            "(f)",
            "@0",
            "D=A",
            "@SP",
            "A=M",
            "M=D",
            "@SP",
            "M=M+1",
        ]

    def test_call(self):
        code_writer = CodeWriter(file_name="test.vm")
        # 将 D 值压入栈顶，并调整栈顶指针
        push_D = [
            "@SP",
            "A=M",
            "M=D",
            "@SP",
            "M=M+1",
        ]
        expected_command = ["// call f 1"]
        expected_command += ["@End$f$0", "D=A"] + push_D
        for symbol in ["LCL", "ARG", "THIS", "THAT"]:
            expected_command += [
                f"@{symbol}",
                "D=M",
            ] + push_D
        expected_command += [
            "@6",
            "D=A",
            "@SP",
            "D=M-D",
            "@ARG",
            "M=D",  # ARG = SP - n - 5
            "@SP",
            "D=M",
            "@LCL",
            "M=D",  # LCL = SP
            "@f",
            "0;JMP",  # goto f
            "(End$f$0)",
        ]
        assert code_writer.write_call("f", 1) == expected_command

    def test_return(self):
        code_writer = CodeWriter(file_name="test.vm")
        expected = [
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
            "@1",
            "D=A",
            "@R13",
            "A=M-D",  # FRAME--
            "D=M",
            "@THAT",
            "M=D",
            "@2",
            "D=A",
            "@R13",
            "A=M-D",  # FRAME--
            "D=M",
            "@THIS",
            "M=D",
            "@3",
            "D=A",
            "@R13",
            "A=M-D",
            "D=M",
            "@ARG",
            "M=D",  # *ARG = pop()
            "@4",
            "D=A",
            "@R13",
            "A=M-D",
            "D=M",
            "@LCL",
            "M=D",  # *LCL = pop()
            "@R14",
            "A=M",
            "0;JMP",  # goto RET
        ]

        assert code_writer.write_return() == expected


class TestMain:
    def test_main_file(self):
        ARITHMETIC_DATA_ROOT = Path(r"data/StackArithmetic")
        file_name = "SimpleAdd"
        source_file_path = ARITHMETIC_DATA_ROOT / file_name / (file_name + ".vm")
        main(source_file_path=source_file_path)

        file_name = "StackTest"
        source_file_path = ARITHMETIC_DATA_ROOT / file_name / (file_name + ".vm")
        main(source_file_path=source_file_path)

        MEMORY_DATA_ROOT = Path(r"data/MemoryAccess")
        file_name = "BasicTest"
        source_file_path = MEMORY_DATA_ROOT / file_name / (file_name + ".vm")
        main(source_file_path=source_file_path)

        file_name = "PointerTest"
        source_file_path = MEMORY_DATA_ROOT / file_name / (file_name + ".vm")
        main(source_file_path=source_file_path)

        file_name = "StaticTest"
        source_file_path = MEMORY_DATA_ROOT / file_name / (file_name + ".vm")
        main(source_file_path=source_file_path)

        PROGRAM_FLOW_DATA_ROOT = Path(r"data/ProgramFlow")
        file_name = "BasicLoop"
        source_file_path = PROGRAM_FLOW_DATA_ROOT / file_name / (file_name + ".vm")
        main(source_file_path=source_file_path)

        file_name = "FibonacciSeries"
        source_file_path = PROGRAM_FLOW_DATA_ROOT / file_name / (file_name + ".vm")
        main(source_file_path=source_file_path)

        FUNCTION_CALLS_DATA_ROOT = Path(r"data/FunctionCalls")
        file_name = "SimpleFunction"
        source_file_path = FUNCTION_CALLS_DATA_ROOT / file_name / (file_name + ".vm")
        main(source_file_path=source_file_path)

        file_name = "NestedCall"
        source_file_path = FUNCTION_CALLS_DATA_ROOT / file_name
        main(source_file_path=source_file_path)

        file_name = "FibonacciElement"
        source_file_path = FUNCTION_CALLS_DATA_ROOT / file_name
        main(source_file_path=source_file_path)

        file_name = "StaticsTest"
        source_file_path = (
            FUNCTION_CALLS_DATA_ROOT / file_name
        )  # TODO 文件夹需要特殊处理
        main(source_file_path=source_file_path)

    def test_fibo_call(self):
        with open("data/FunctionCalls/FibonacciElement/FibonacciElement.asm.bk") as f:
            expected = f.readlines()
        expected = [line.strip() for line in expected]

        with open("data/FunctionCalls/FibonacciElement/FibonacciElement.asm") as f:
            actual = f.readlines()
        actual = [line.strip() for line in actual]

        for i, (expected_line, actual_line) in enumerate(zip(expected, actual)):
            if expected_line.startswith("//") and actual_line.startswith("//"):
                continue
            if expected_line == "D=A+D" and actual_line.startswith("D=D+A"):
                continue
            if expected_line == "@R15" and actual_line.startswith("@R13"):
                continue
            if expected_line == "(Sys.init$LOOP)" and actual_line.startswith(
                "(Sys$LOOP)"
            ):
                continue
            if expected_line == "@Sys.init$LOOP" and actual_line.startswith(
                "@Sys$LOOP"
            ):
                continue
            if expected_line == "D=M+D" and actual_line.startswith("D=D+M"):
                continue
            if expected_line == "A=M+D" and actual_line.startswith("A=D+M"):
                continue
            if expected_line == "M=M+D" and actual_line.startswith("M=D+M"):
                continue
            if expected_line.startswith("@Main.fibonacci$") and actual_line.startswith(
                "@Main$"
            ):
                continue
            if expected_line.startswith("(Main.fibonacci$") and actual_line.startswith(
                "(Main$"
            ):
                continue
            if expected_line.startswith("(Sys.init$") and actual_line.startswith(
                "(Sys$"
            ):
                continue
            if expected_line.startswith("@Sys.init$") and actual_line.startswith(
                "@Sys$"
            ):
                continue
            assert (i + 1, expected_line) == (i + 1, actual_line)


if __name__ == "__main__":
    pytest.main(["-v"])

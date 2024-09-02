from parser import Parser

import pytest

from main import main
from code_writer import CodeWriter
from symbol_table import SymbolTable


class TestParser:
    def test_read_command_file(self):
        source_file_path = r"data/add/Add.asm"
        with open(source_file_path, "r") as f:
            command_lines = f.readlines()
        command_lines = [x.strip() for x in command_lines]

        parser = Parser(command_lines=command_lines)

        assert type(parser.lines) is list
        assert len(parser.lines) == 6
        assert parser.lines[0] == "@2"

    def test_advance(self):
        source_file_path = r"data/add/Add.asm"

        with open(source_file_path, "r") as f:
            command_lines = f.readlines()
        command_lines = [x.strip() for x in command_lines]
        parser = Parser(command_lines=command_lines)

        assert parser.advance() == "@2"
        assert parser.advance() == "D=A"
        assert parser.advance() == "@3"
        assert parser.advance() == "D=D+A"
        assert parser.advance() == "@0"
        assert parser.advance() == "M=D"
        assert parser.advance() is None

    def test_command_type(self):
        command_lines = ["@2", "D=A", ""]

        parser = Parser(command_lines=command_lines)
        assert parser.command_type() == "A_COMMAND"

        parser.advance()
        assert parser.command_type() == "C_COMMAND"

    def test_symbol(self):
        command_lines = ["@2", "D=A"]

        parser = Parser(command_lines=command_lines)
        assert parser.symbol() == "2"

        parser.advance()
        with pytest.raises(Exception):
            parser.symbol()

    def test_dest(self):
        command_lines = ["@2", "D=A"]

        parser = Parser(command_lines=command_lines)
        with pytest.raises(Exception):
            parser.dest()

        parser.advance()
        assert parser.dest() == "D"

    def test_comp(self):
        command_lines = ["@2", "D=A"]

        parser = Parser(command_lines=command_lines)
        with pytest.raises(Exception):
            parser.comp()

        parser.advance()
        assert parser.comp() == "A"

    def test_jump(self):
        command_lines = ["@2", "D=A", "D;JGT"]

        parser = Parser(command_lines=command_lines)
        with pytest.raises(Exception):
            parser.jump()

        parser.advance()
        assert parser.jump() == ""

        parser.advance()
        assert parser.jump() == "JGT"


class TestCode:
    def test_symbol(self):
        symbol = "2"
        code_writer = CodeWriter(symbol_table=SymbolTable())

        assert code_writer.symbol(symbol) == "000000000000010"

    def test_dest(self):
        dest_symbol = "M"
        assert CodeWriter.dest(dest_symbol) == "001"

        dest_symbol = "D"
        assert CodeWriter.dest(dest_symbol) == "010"

    def test_comp(self):
        comp_symbol = "A"
        assert CodeWriter.comp(comp_symbol) == "0110000"

        comp_symbol = "D+A"
        assert CodeWriter.comp(comp_symbol) == "0000010"

        comp_symbol = "D"
        assert CodeWriter.comp(comp_symbol) == "0001100"

    def test_jump(self):
        jump_symbol = None
        assert CodeWriter.jump(jump_symbol) == "000"


class TestMain:

    def test_main_file_add(self):
        expert = [
            "0000000000000010",
            "1110110000010000",
            "0000000000000011",
            "1110000010010000",
            "0000000000000000",
            "1110001100001000",
        ]
        main(source_file_name="add/Add.asm", dest_file_name="add/Add.hack")
        with open("data/add/Add.hack", "r") as f:
            actual = f.readlines()

        actual = [x.strip() for x in actual]
        assert actual == expert

    def test_main_file_maxl(self):
        main(source_file_name="max/MaxL.asm", dest_file_name="max/MaxL.hack")
        with open("data/max/MaxL.hack", "r") as f:
            actual = f.readlines()
        actual = [x.strip() for x in actual]
        assert len(actual) == 16

    def test_main_file_max(self):
        main(source_file_name="max/Max.asm", dest_file_name="max/Max.hack")
        with open("data/max/Max.hack", "r") as f:
            actual = f.readlines()
        actual = [x.strip() for x in actual]
        assert len(actual) == 16

    def test_main_file_rectl(self):
        main(source_file_name="rect/RectL.asm", dest_file_name="rect/RectL.hack")
        with open("data/rect/RectL.hack", "r") as f:
            actual = f.readlines()
        actual = [x.strip() for x in actual]
        assert len(actual) == 25

    def test_main_file_rect(self):
        main(source_file_name="rect/Rect.asm", dest_file_name="rect/Rect.hack")
        with open("data/rect/Rect.hack", "r") as f:
            actual = f.readlines()
        actual = [x.strip() for x in actual]
        assert len(actual) == 25

    def test_main_file_pongl(self):
        main(source_file_name="pong/PongL.asm", dest_file_name="pong/PongL.hack")
        with open("data/pong/PongL.hack", "r") as f:
            actual = f.readlines()
        actual = [x.strip() for x in actual]
        assert len(actual) == 27483

    def test_main_file_pong(self):
        main(source_file_name="pong/Pong.asm", dest_file_name="pong/Pong.hack")
        with open("data/pong/Pong.hack", "r") as f:
            actual = f.readlines()
        actual = [x.strip() for x in actual]
        assert len(actual) == 27483


class TestSymbolTable:
    def test_symbol_table_constructor(self):
        symbol_table = SymbolTable()

        assert len(symbol_table) == 23


if __name__ == "__main__":
    pytest.main()

"""
将Hack汇编语言翻译成二进制码
"""

from symbol_table import SymbolTable

COMP_SYMBOL_DICT = {
    "0": "0101010",
    "1": "0111111",
    "-1": "0111010",
    "D": "0001100",
    "A": "0110000",
    "!D": "0001101",
    "!A": "0110001",
    "-D": "0001111",
    "-A": "0110011",
    "D+1": "0011111",
    "A+1": "0110111",
    "D-1": "0001110",
    "A-1": "0110010",
    "D+A": "0000010",
    "D-A": "0010011",
    "A-D": "0000111",
    "D&A": "0000000",
    "D|A": "0010101",
    "M": "1110000",
    "!M": "1110001",
    "-M": "1110011",
    "M+1": "1110111",
    "M-1": "1110010",
    "D+M": "1000010",
    "D-M": "1010011",
    "M-D": "1000111",
    "D&M": "1000000",
    "D|M": "1010101",
}
JUMP_SYMBOL_DICT = {
    "JGT": "001",
    "JEQ": "010",
    "JGE": "011",
    "JLT": "100",
    "JNE": "101",
    "JLE": "110",
    "JMP": "111",
}
DEST_SYMBOL_DICT = {
    "M": "001",
    "D": "010",
    "MD": "011",
    "A": "100",
    "AM": "101",
    "AD": "110",
    "AMD": "111",
}


class MyCode:
    def __init__(self, symbol_table: SymbolTable) -> None:
        self.symbol_table = symbol_table

    def symbol(self, symbol: str) -> str:
        """返回symbol对应的 15 位二进制字符串"""
        if symbol.isnumeric():
            return f"{int(symbol):015b}"
        else:
            if self.symbol_table.contains(symbol):
                return f"{int(self.symbol_table.get_address(symbol)):015b}"
            else:
                raise ValueError(f"{symbol} is not a valid symbol")

    @staticmethod
    def dest(dest_symbol: str) -> str:
        """返回dest助记符对应的 3 bits二进制码"""
        try:
            return DEST_SYMBOL_DICT[dest_symbol]
        except KeyError:
            return "000"

    @staticmethod
    def comp(comp_symbol: str):
        """返回comp助记符对应的 7 bits二进制码"""
        try:
            return COMP_SYMBOL_DICT[comp_symbol]
        except KeyError:
            raise ValueError(f"{comp_symbol} is not a valid comp symbol")

    @staticmethod
    def jump(jump_symbol: str):
        """返回jump助记符对应的 3 bits二进制码"""
        try:
            return JUMP_SYMBOL_DICT[jump_symbol]
        except KeyError:
            return "000"

"""字元转换器：从输入流中删除所有的注释和空白字符，并根据 Jack 语言的语法规则，将输入流分解成 Jack 语言的字元（终结符）。

Jack 语言包括 5 种终结元素（即字元）：
1. 关键字；
2. 符号；
3. 整数常量；
4. 字符串常量；
5. 标识符。
"""
from pathlib import Path

KEYWORDS = {
    'class',
    'constructor',
    'function',
    'method',
    'field',
    'static',
    'var',
    'int',
    'char',
    'boolean',
    'void',
    'true',
    'false',
    'null',
    'this',
    'let',
    'do',
    'if',
    'else',
    'while',
    'return',
}
SYMBOLS = {
    '{',
    '}',
    '(',
    ')',
    '[',
    ']',
    '.',
    ',',
    ';',
    '+',
    '-',
    '*',
    '/',
    '&',
    '|',
    '<',
    '>',
    '=',
    '~',
}
MAX_INTEGER_CONSTANT = 32767


class JackTokenizer:
    """词法分析（Lexical Analysis）"""

    def __init__(self, source_code_lines: list[str]) -> None:
        """接收输入的源代码行列表，并删除所有的注释和空白字符，初始化得到清理之后的源代码行列表。"""
        source_code_lines = self._remove_whitespace(source_code_lines)
        self.source_code = self._remove_comments(source_code_lines)
        self.token_stream = self._tokenize(self.source_code)

    @staticmethod
    def _remove_whitespace(source_code_lines: list[str]) -> list[str]:
        """删除所有的空白字符。"""
        return [line.strip() for line in source_code_lines if line.strip()]

    @staticmethod
    def _remove_comments(source_code_lines: list[str]) -> list[str]:
        results = []
        is_comment = False
        for line in source_code_lines:
            if '//' in line:
                cur_line = line.split('//')[0].strip()
            elif '/*' in line:
                cur_line = line.split('/*')[0].strip()
                if '*/' not in line:
                    is_comment = True
            elif '*/' in line:
                cur_line = line.split('*/')[1].strip()
                is_comment = False
            elif is_comment:
                continue
            else:
                cur_line = line.strip()
            if cur_line:
                results.append(cur_line)
        return results

    @classmethod
    def _tokenize(cls, source_code: list[str]) -> list[str]:
        """逐个将代码行字元化为一个个字元

        一般的字元可以通过空格区分，但是符号需要特殊处理（一般和其它类型字元之间没有空格）。
        """
        results = []
        for line in source_code:
            results.extend(cls.tokenize_line_characters(line))
        return results

    @classmethod
    def tokenize_line_characters(cls, line: str) -> list[str]:
        """将一行字元化为一个个字元。"""
        results = []
        if '"' not in line:
            current_line_tokens = line.split()  # 初步使用空格进行分割
            for index, token in enumerate(current_line_tokens):
                if set(token) & SYMBOLS:  # 如果当前 token 包含符号，则需要进一步分割
                    temp_token = []
                    for char in token:
                        if char in SYMBOLS:
                            if temp_token:
                                results.append(''.join(temp_token))
                                temp_token = []
                            results.append(char)
                        else:
                            temp_token.append(char)
                    if temp_token:
                        results.append(''.join(temp_token))
                else:
                    results.append(token)
        else:
            # 处理使用双引号进行分割的字符串，暂时认为字符串不换行
            start_index = line.index('"')
            end_index = line.index('"', start_index + 1)
            pre_tokens = cls.tokenize_line_characters(line[:start_index])
            post_tokens = cls.tokenize_line_characters(line[end_index + 1 :])
            results = (
                pre_tokens + [line[start_index : end_index + 1]] + post_tokens
            )
        return results

    def has_more_tokens(self) -> bool:
        """判断是否还有更多可读的 token。"""
        return len(self.token_stream) > 0

    def advance(self) -> None:
        """从输入流中读取下一个 token，使其成为当前字元。"""
        self.token_stream.pop(0)

    def token_type(self) -> str:
        """返回当前 token 的类型。"""
        if self.token_stream[0] in KEYWORDS:
            return 'keyword'
        elif self.token_stream[0] in SYMBOLS:
            return 'symbol'
        elif (
            self.token_stream[0].isdigit()
            and 0 <= int(self.token_stream[0]) <= MAX_INTEGER_CONSTANT
        ):
            return 'integerConstant'
        elif self.token_stream[0].startswith('"'):
            return 'stringConstant'
        else:
            return 'identifier'

    def keyword(self) -> str:
        """返回当前 token 的关键字。"""
        if self.token_type() == 'keyword':
            return self.token_stream[0]

    def symbol(self) -> str:
        """返回当前 token 的符号。"""
        if self.token_type() == 'symbol':
            return self.token_stream[0]

    def identifier(self) -> str:
        """返回当前 token 的标识符。"""
        if self.token_type() == 'identifier':
            return self.token_stream[0]

    def int_val(self) -> int:
        """返回当前 token 的整数值。"""
        if self.token_type() == 'integerConstant':
            return int(self.token_stream[0])

    def string_val(self) -> str:
        """返回当前 token 的字符串值。"""
        if self.token_type() == 'stringConstant':
            return self.token_stream[0][1:-1]

    def export_to_xml(self, output_file: Path) -> None:
        """将当前 token 写入到输出文件中。"""
        cur_text_lines = ['<tokens>']
        while self.has_more_tokens():
            if self.token_type() == 'symbol':
                cur_token = self.symbol()
            elif self.token_type() == 'keyword':
                cur_token = self.keyword()
            elif self.token_type() == 'identifier':
                cur_token = self.identifier()
            elif self.token_type() == 'integerConstant':
                cur_token = self.int_val()
            elif self.token_type() == 'stringConstant':
                cur_token = self.string_val()
            else:
                raise ValueError(f'Invalid token type: {self.token_type()}')
            if cur_token == '<':
                cur_token = '&lt;'
            elif cur_token == '>':
                cur_token = '&gt;'
            elif cur_token == '&':
                cur_token = '&amp;'
            cur_text_lines.append(
                f'<{self.token_type()}> {cur_token} </{self.token_type()}>'
            )
            self.advance()
        cur_text_lines += ['</tokens>']
        with output_file.open('w') as f:
            for line in cur_text_lines:
                f.writelines(line + '\n')

from pathlib import Path

import pytest

from Jack_tokenizer import JackTokenizer


class TestJackTokenizer:
    def test_init(self):
        source = Path('chapter10_data/Square/Main.jack')
        with open(source, 'r') as f:
            source_code = f.readlines()
        tokenizer = JackTokenizer(source_code)
        assert len(tokenizer.source_code) == 26

        source = Path('chapter10_data/Square/Square.jack')
        with open(source, 'r') as f:
            source_code = f.readlines()
        tokenizer = JackTokenizer(source_code)
        assert len(tokenizer.source_code) == 81

        source = Path('chapter10_data/Square/SquareGame.jack')
        with open(source, 'r') as f:
            source_code = f.readlines()
        tokenizer = JackTokenizer(source_code)
        assert len(tokenizer.source_code) == 45

        tokenizer = JackTokenizer(['            let s = "string constant";'])
        assert tokenizer.token_stream == [
            'let',
            's',
            '=',
            '"string constant"',
            ';',
        ]

    def test_has_more_tokens(self):
        source_code = []
        tokenizer = JackTokenizer(source_code)
        assert tokenizer.has_more_tokens() == False

        source_code = ['class Main {', '}']
        tokenizer = JackTokenizer(source_code)
        assert tokenizer.has_more_tokens() == True

    def test_advance(self):
        source_code = ['class Main {', '}']
        tokenizer = JackTokenizer(source_code)
        assert tokenizer.token_stream[0] == 'class'

        tokenizer.advance()
        assert tokenizer.token_stream[0] == 'Main'

    def test_token_type(self):
        source_code = ['class Main {', '5', '"Hello, World!"', '}']
        tokenizer = JackTokenizer(source_code)
        assert tokenizer.token_type() == 'keyword'

        tokenizer.advance()
        assert tokenizer.token_type() == 'identifier'

        tokenizer.advance()
        assert tokenizer.token_type() == 'symbol'

        tokenizer.advance()
        assert tokenizer.token_type() == 'integerConstant'

        tokenizer.advance()
        assert tokenizer.token_type() == 'stringConstant'

    def test_keyword(self):
        source_code = ['class method this']
        tokenizer = JackTokenizer(source_code)
        assert tokenizer.keyword() == 'class'

        tokenizer.advance()
        assert tokenizer.keyword() == 'method'

        tokenizer.advance()
        assert tokenizer.keyword() == 'this'

    def test_symbol(self):
        source_code = ['{a}']
        tokenizer = JackTokenizer(source_code)
        assert tokenizer.symbol() == '{'
        tokenizer.advance()
        assert tokenizer.identifier() == 'a'
        tokenizer.advance()
        assert tokenizer.symbol() == '}'

    def test_identifier(self):
        source_code = ['Main {', '5', '"Hello, World!"', '}']
        tokenizer = JackTokenizer(source_code)
        assert tokenizer.identifier() == 'Main'

    def test_int_val(self):
        source_code = ['5', '"Hello, World!"', '}']
        tokenizer = JackTokenizer(source_code)
        assert tokenizer.int_val() == 5

    def test_string_val(self):
        source_code = ['"Hello, World!"', '}']
        tokenizer = JackTokenizer(source_code)
        assert tokenizer.string_val() == 'Hello, World!'

    def test_overall_tokenizer(self):
        source = Path('chapter10_data/Square')
        target = Path('syntax_analysis_outputs/Square')
        target.mkdir(parents=True, exist_ok=True)
        for file_name in source.iterdir():
            if file_name.suffix != '.jack':
                continue
            with file_name.open() as f:
                source_code = f.readlines()
            tokenizer = JackTokenizer(source_code)
            cur_target = target / (file_name.stem + 'T.xml')
            tokenizer.export_to_xml(cur_target)

        source = Path('chapter10_data/ArrayTest')
        target = Path('syntax_analysis_outputs/ArrayTest')
        target.mkdir(parents=True, exist_ok=True)
        for file_name in source.iterdir():
            if file_name.suffix != '.jack':
                continue
            with file_name.open() as f:
                source_code = f.readlines()
            tokenizer = JackTokenizer(source_code)
            cur_target = target / (file_name.stem + 'T.xml')
            tokenizer.export_to_xml(cur_target)


if __name__ == '__main__':
    pytest.main()

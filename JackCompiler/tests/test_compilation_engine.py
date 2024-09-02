from pathlib import Path

import pytest

from compilation_engine import CompilationEngineAsXML, CompilationEngineAsVM
from Jack_tokenizer import JackTokenizer


class TestCompilationEngine:
    def test_compile_class_as_xml(self):
        tokenizer = JackTokenizer(['class Test {', '}'])
        compilation_engine = CompilationEngineAsXML()
        assert compilation_engine(tokenizer) == [
            '<class>',
            '<keyword> class </keyword>',
            '<identifier> Test </identifier>',
            '<symbol> { </symbol>',
            '<symbol> } </symbol>',
            '</class>',
        ]

    def test_compile_seven(self):
        source = Path('chapter11_data/Seven/Main.jack')
        target = Path('syntax_analysis_outputs/Seven/Main.vm')
        if target.exists():
            target.unlink()
        target.parent.mkdir(parents=True, exist_ok=True)

        with source.open() as f:
            source_code = f.readlines()
        tokenizer = JackTokenizer(source_code)
        compilation_engine = CompilationEngineAsVM(target)
        compilation_engine(tokenizer)
        actual = [line for line in target.read_text().split('\n') if line]
        answer = Path('chapter11_data/Seven/Main.vm')
        expected = [line for line in answer.read_text().split('\n') if line]
        for a, e in zip(actual, expected):
            assert a == e

    def test_compile_convert_to_bin(self):
        source = Path('chapter11_data/ConvertToBin/Main.jack')
        target = Path('syntax_analysis_outputs/ConvertToBin/Main.vm')
        if target.exists():
            target.unlink()
        target.parent.mkdir(parents=True, exist_ok=True)

        with source.open() as f:
            source_code = f.readlines()
        tokenizer = JackTokenizer(source_code)
        compilation_engine = CompilationEngineAsVM(target)
        compilation_engine(tokenizer)
        actual = [line for line in target.read_text().split('\n') if line]
        answer = Path('chapter11_data/ConvertToBin/Main.vm')
        expected = [line for line in answer.read_text().split('\n') if line]
        for a, e in zip(actual, expected):
            assert a == e

    def test_compile_square(self):
        source_dir = Path('chapter11_data/Square')
        target_dir = Path('syntax_analysis_outputs/Square')

        for source in source_dir.iterdir():
            if source.suffix != '.jack':
                continue
            target = target_dir / (source.stem + '.vm')
            if target.exists():
                target.unlink()
            target.parent.mkdir(parents=True, exist_ok=True)

            with source.open() as f:
                source_code = f.readlines()
            tokenizer = JackTokenizer(source_code)
            compilation_engine = CompilationEngineAsVM(target)
            compilation_engine(tokenizer)
            actual = [line for line in target.read_text().split('\n') if line]
            answer = Path('chapter11_data/Square') / (source.stem + '.vm')
            expected = [
                line for line in answer.read_text().split('\n') if line
            ]
            for a, e in zip(actual, expected):
                assert a == e

    def test_compile_average(self):
        source = Path('chapter11_data/Average/Main.jack')
        target = Path('syntax_analysis_outputs/Average/Main.vm')
        if target.exists():
            target.unlink()
        target.parent.mkdir(parents=True, exist_ok=True)

        with source.open() as f:
            source_code = f.readlines()
        tokenizer = JackTokenizer(source_code)
        compilation_engine = CompilationEngineAsVM(target)
        compilation_engine(tokenizer)
        actual = [line for line in target.read_text().split('\n') if line]
        answer = Path('chapter11_data/Average/Main.vm')
        expected = [line for line in answer.read_text().split('\n') if line]
        for a, e in zip(actual, expected):
            assert a == e

    def test_compile_pong(self):
        source_dir = Path('chapter11_data/Pong')
        target_dir = Path('syntax_analysis_outputs/Pong')

        for source in source_dir.iterdir():
            if source.suffix != '.jack':
                continue
            target = target_dir / (source.stem + '.vm')
            if target.exists():
                target.unlink()
            target.parent.mkdir(parents=True, exist_ok=True)

            with source.open() as f:
                source_code = f.readlines()
            tokenizer = JackTokenizer(source_code)
            compilation_engine = CompilationEngineAsVM(target)
            compilation_engine(tokenizer)
            actual = [line for line in target.read_text().split('\n') if line]
            answer = Path('chapter11_data/Pong') / (source.stem + '.vm')
            expected = [
                line for line in answer.read_text().split('\n') if line
            ]
            for a, e in zip(actual, expected):
                assert a == e

    def test_compile_complex_arrays(self):
        source_dir = Path('chapter11_data/ComplexArrays')
        target_dir = Path('syntax_analysis_outputs/ComplexArrays')

        for source in source_dir.iterdir():
            if source.suffix != '.jack':
                continue
            target = target_dir / (source.stem + '.vm')
            if target.exists():
                target.unlink()
            target.parent.mkdir(parents=True, exist_ok=True)

            with source.open() as f:
                source_code = f.readlines()
            tokenizer = JackTokenizer(source_code)
            compilation_engine = CompilationEngineAsVM(target)
            compilation_engine(tokenizer)
            actual = [line for line in target.read_text().split('\n') if line]
            answer = Path('chapter11_data/ComplexArrays') / (source.stem + '.vm')
            expected = [
                line for line in answer.read_text().split('\n') if line
            ]
            for a, e in zip(actual, expected):
                assert a == e

    def test_compile_class_var_dec(self):
        tokenizer = JackTokenizer(['static int a, b;'])
        assert CompilationEngineAsXML.compile_class_var_dec(tokenizer) == [
            '<classVarDec>',
            '<keyword> static </keyword>',
            '<keyword> int </keyword>',
            '<identifier> a </identifier>',
            '<symbol> , </symbol>',
            '<identifier> b </identifier>',
            '<symbol> ; </symbol>',
            '</classVarDec>',
        ]

    def test_compile_subroutine(self):
        tokenizer = JackTokenizer(['function void test() {', '}'])
        assert CompilationEngineAsXML.compile_subroutine(tokenizer) == [
            '<subroutineDec>',
            '<keyword> function </keyword>',
            '<keyword> void </keyword>',
            '<identifier> test </identifier>',
            '<symbol> ( </symbol>',
            '<parameterList>',
            '</parameterList>',
            '<symbol> ) </symbol>',
            '<subroutineBody>',
            '<symbol> { </symbol>',
            '<symbol> } </symbol>',
            '</subroutineBody>',
            '</subroutineDec>',
        ]

    def test_compile_parameter_list(self):
        tokenizer = JackTokenizer(['int a, boolean b'])
        assert CompilationEngineAsXML.compile_parameter_list(tokenizer) == [
            '<parameterList>',
            '<keyword> int </keyword>',
            '<identifier> a </identifier>',
            '<symbol> , </symbol>',
            '<keyword> boolean </keyword>',
            '<identifier> b </identifier>',
            '</parameterList>',
        ]

    def test_compile_var_dec(self):
        tokenizer = JackTokenizer(['var int a, b;'])
        assert CompilationEngineAsXML.compile_var_dec(tokenizer) == [
            '<varDec>',
            '<keyword> var </keyword>',
            '<keyword> int </keyword>',
            '<identifier> a </identifier>',
            '<symbol> , </symbol>',
            '<identifier> b </identifier>',
            '<symbol> ; </symbol>',
            '</varDec>',
        ]

    def test_compile_statements(self):
        tokenizer = JackTokenizer(['let a = 1;', 'return 2;'])
        assert CompilationEngineAsXML.compile_statements(tokenizer) == [
            '<statements>',
            '<letStatement>',
            '<keyword> let </keyword>',
            '<identifier> a </identifier>',
            '<symbol> = </symbol>',
            '<expression>',
            '<term>',
            '<integerConstant> 1 </integerConstant>',
            '</term>',
            '</expression>',
            '<symbol> ; </symbol>',
            '</letStatement>',
            '<returnStatement>',
            '<keyword> return </keyword>',
            '<expression>',
            '<term>',
            '<integerConstant> 2 </integerConstant>',
            '</term>',
            '</expression>',
            '<symbol> ; </symbol>',
            '</returnStatement>',
            '</statements>',
        ]

    def test_compile_do(self):
        tokenizer = JackTokenizer(['do Test.test();'])
        assert CompilationEngineAsXML.compile_do(tokenizer) == [
            '<doStatement>',
            '<keyword> do </keyword>',
            '<identifier> Test </identifier>',
            '<symbol> . </symbol>',
            '<identifier> test </identifier>',
            '<symbol> ( </symbol>',
            '<expressionList>',
            '</expressionList>',
            '<symbol> ) </symbol>',
            '<symbol> ; </symbol>',
            '</doStatement>',
        ]

    def test_compile_let(self):
        tokenizer = JackTokenizer(['let a = 1;'])
        assert CompilationEngineAsXML.compile_let(tokenizer) == [
            '<letStatement>',
            '<keyword> let </keyword>',
            '<identifier> a </identifier>',
            '<symbol> = </symbol>',
            '<expression>',
            '<term>',
            '<integerConstant> 1 </integerConstant>',
            '</term>',
            '</expression>',
            '<symbol> ; </symbol>',
            '</letStatement>',
        ]

    def test_compile_while(self):
        tokenizer = JackTokenizer(['while (true) {', '}'])
        assert CompilationEngineAsXML.compile_while(tokenizer) == [
            '<whileStatement>',
            '<keyword> while </keyword>',
            '<symbol> ( </symbol>',
            '<expression>',
            '<term>',
            '<keyword> true </keyword>',
            '</term>',
            '</expression>',
            '<symbol> ) </symbol>',
            '<symbol> { </symbol>',
            '<statements>',
            '</statements>',
            '<symbol> } </symbol>',
            '</whileStatement>',
        ]

    def test_compile_return(self):
        tokenizer = JackTokenizer(['return 1;'])
        assert CompilationEngineAsXML.compile_return(tokenizer) == [
            '<returnStatement>',
            '<keyword> return </keyword>',
            '<expression>',
            '<term>',
            '<integerConstant> 1 </integerConstant>',
            '</term>',
            '</expression>',
            '<symbol> ; </symbol>',
            '</returnStatement>',
        ]

        tokenizer = JackTokenizer(['return;'])
        assert CompilationEngineAsXML.compile_return(tokenizer) == [
            '<returnStatement>',
            '<keyword> return </keyword>',
            '<symbol> ; </symbol>',
            '</returnStatement>',
        ]

    def test_compile_if(self):
        tokenizer = JackTokenizer(['if (true) {', '}'])
        assert CompilationEngineAsXML.compile_if(tokenizer) == [
            '<ifStatement>',
            '<keyword> if </keyword>',
            '<symbol> ( </symbol>',
            '<expression>',
            '<term>',
            '<keyword> true </keyword>',
            '</term>',
            '</expression>',
            '<symbol> ) </symbol>',
            '<symbol> { </symbol>',
            '<statements>',
            '</statements>',
            '<symbol> } </symbol>',
            '</ifStatement>',
        ]

    def test_compile_expression(self):
        tokenizer = JackTokenizer(['1 + 2'])
        assert CompilationEngineAsXML.compile_expression(tokenizer) == [
            '<expression>',
            '<term>',
            '<integerConstant> 1 </integerConstant>',
            '</term>',
            '<symbol> + </symbol>',
            '<term>',
            '<integerConstant> 2 </integerConstant>',
            '</term>',
            '</expression>',
        ]

    def test_compile_expression_list(self):
        tokenizer = JackTokenizer(['1, 2'])
        assert CompilationEngineAsXML.compile_expression_list(tokenizer) == [
            '<expressionList>',
            '<expression>',
            '<term>',
            '<integerConstant> 1 </integerConstant>',
            '</term>',
            '</expression>',
            '<symbol> , </symbol>',
            '<expression>',
            '<term>',
            '<integerConstant> 2 </integerConstant>',
            '</term>',
            '</expression>',
            '</expressionList>',
        ]

    def test_compile_term(self):
        tokenizer = JackTokenizer(['1'])
        assert CompilationEngineAsXML.compile_term(tokenizer) == [
            '<term>',
            '<integerConstant> 1 </integerConstant>',
            '</term>',
        ]

        tokenizer = JackTokenizer(['(1)'])
        assert CompilationEngineAsXML.compile_term(tokenizer) == [
            '<term>',
            '<symbol> ( </symbol>',
            '<expression>',
            '<term>',
            '<integerConstant> 1 </integerConstant>',
            '</term>',
            '</expression>',
            '<symbol> ) </symbol>',
            '</term>',
        ]

        tokenizer = JackTokenizer(['-1'])
        assert CompilationEngineAsXML.compile_term(tokenizer) == [
            '<term>',
            '<symbol> - </symbol>',
            '<term>',
            '<integerConstant> 1 </integerConstant>',
            '</term>',
            '</term>',
        ]

    def test_overall_tokenizer(self):
        source = Path('chapter10_data/ExpressionLessSquare')
        target = Path('syntax_analysis_outputs/ExpressionLessSquare')
        target.mkdir(parents=True, exist_ok=True)
        for file_name in source.iterdir():
            if file_name.suffix != '.jack':
                continue
            with file_name.open() as f:
                source_code = f.readlines()
            tokenizer = JackTokenizer(source_code)

            cur_target = target / (file_name.stem + '.xml')
            compilation_engine = CompilationEngineAsXML(cur_target)
            compilation_engine(tokenizer)

        source = Path('chapter10_data/Square')  # TODO 失败了 2024/08/15 22:01:58
        target = Path('syntax_analysis_outputs/Square')
        target.mkdir(parents=True, exist_ok=True)
        for file_name in source.iterdir():
            if file_name.suffix != '.jack':
                continue
            with file_name.open() as f:
                source_code = f.readlines()
            tokenizer = JackTokenizer(source_code)

            cur_target = target / (file_name.stem + '.xml')
            compilation_engine = CompilationEngineAsXML(cur_target)
            compilation_engine(tokenizer)

        source = Path('chapter10_data/ArrayTest')
        target = Path('syntax_analysis_outputs/ArrayTest')
        target.mkdir(parents=True, exist_ok=True)
        for file_name in source.iterdir():
            if file_name.suffix != '.jack':
                continue
            with file_name.open() as f:
                source_code = f.readlines()
            tokenizer = JackTokenizer(source_code)

            cur_target = target / (file_name.stem + '.xml')
            compilation_engine = CompilationEngineAsXML(cur_target)
            compilation_engine(tokenizer)


if __name__ == '__main__':
    pytest.main(['-vv'])

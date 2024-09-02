from abc import ABC, abstractmethod
from pathlib import Path

from Jack_tokenizer import JackTokenizer
from symbol_table import Kind, SymbolTable
from vm_writer import Command, Segment, VMWriter

OP_SET = {'+', '-', '*', '/', '&', '|', '<', '>', '='}
UNARY_OP_SET = {'-', '~'}
KEYWORD_CONSTANT = {
    'true',
    'false',
    'null',
    'this',
}


class CompilationEngine(ABC):
    @abstractmethod
    def __call__(self, tokenizer: JackTokenizer) -> list[str] | None:
        pass


class CompilationEngineAsVM(CompilationEngine):
    def __init__(self, output_file: Path):
        self.output_file = output_file
        self.vm_writer = VMWriter(output_file)
        self.symbol_table = SymbolTable()

    def __call__(self, tokenizer: JackTokenizer):
        self.compile_class(tokenizer)

    def compile_class(self, tokenizer: JackTokenizer):
        assert tokenizer.keyword() == 'class'
        tokenizer.advance()

        class_name = tokenizer.identifier()
        self.symbol_table.class_name = class_name
        tokenizer.advance()

        assert tokenizer.symbol() == '{'
        tokenizer.advance()

        while tokenizer.has_more_tokens() and tokenizer.symbol() != '}':
            if (
                tokenizer.keyword() == 'static'
                or tokenizer.keyword() == 'field'
            ):
                self.compile_class_var_dec(tokenizer)
            elif (
                tokenizer.keyword() == 'constructor'
                or tokenizer.keyword() == 'function'
                or tokenizer.keyword() == 'method'
            ):
                self.compile_subroutine(tokenizer)
            else:
                raise NotImplementedError('未实现的属性/方法')

    def compile_class_var_dec(self, tokenizer: JackTokenizer) -> None:
        if tokenizer.keyword() == 'static':
            kind = Kind.STATIC
        elif tokenizer.keyword() == 'field':
            kind = Kind.FIELD
        else:
            raise NotImplementedError()
        tokenizer.advance()

        if tokenizer.token_type() == 'keyword':  # type
            type_ = tokenizer.keyword()
        else:
            type_ = tokenizer.identifier()
        tokenizer.advance()

        var_name = tokenizer.identifier()
        tokenizer.advance()

        self.symbol_table.define(var_name, type_, kind)

        while tokenizer.has_more_tokens() and tokenizer.symbol() == ',':
            tokenizer.advance()
            var_name = tokenizer.identifier()
            tokenizer.advance()
            self.symbol_table.define(var_name, type_, kind)

        assert tokenizer.symbol() == ';'
        tokenizer.advance()

    def compile_subroutine(self, tokenizer: JackTokenizer):
        subroutine_kind = tokenizer.keyword()  # constructor/function/method
        tokenizer.advance()

        subroutine_return_type = (
            tokenizer.keyword()
        )  # void/int/boolean/char/className
        tokenizer.advance()

        subroutine_name = (
            f'{self.symbol_table.class_name}.{tokenizer.identifier()}'
        )
        tokenizer.advance()
        self.symbol_table.start_subroutine(subroutine_name)

        if subroutine_kind == 'method':
            self.symbol_table.define('this', self.symbol_table.class_name, Kind.ARG)

        assert tokenizer.symbol() == '('
        tokenizer.advance()

        self.compile_parameter_list(tokenizer)

        assert tokenizer.symbol() == ')'
        tokenizer.advance()

        assert tokenizer.symbol() == '{'
        tokenizer.advance()

        n_locals = 0
        while tokenizer.has_more_tokens() and tokenizer.keyword() == 'var':
            cur_n_locals = self.compile_var_dec(tokenizer)
            n_locals += cur_n_locals

        self.vm_writer.write_function(
            subroutine_name, n_locals
        )  # 这里的这个是局部变量的个数

        if subroutine_kind == 'method':
            self.vm_writer.write_push(Segment.ARGUMENT, 0)  # 方法的第一个参数是this
            self.vm_writer.write_pop(Segment.POINTER, 0)

        if subroutine_kind == 'constructor':
            self.vm_writer.write_push(
                Segment.CONSTANT, self.symbol_table.var_count(Kind.FIELD)
            )
            self.vm_writer.write_call('Memory.alloc', 1)
            self.vm_writer.write_pop(Segment.POINTER, 0)

        while tokenizer.has_more_tokens() and tokenizer.symbol() != '}':
            self.compile_statements(tokenizer)

        assert tokenizer.symbol() == '}'
        tokenizer.advance()

    def compile_parameter_list(self, tokenizer: JackTokenizer):
        if not tokenizer.has_more_tokens() or tokenizer.symbol() == ')':
            return
        while tokenizer.has_more_tokens():
            if tokenizer.token_type() == 'identifier':
                type_ = tokenizer.identifier()
            else:
                type_ = tokenizer.keyword()
            tokenizer.advance()

            var_name = tokenizer.identifier()
            tokenizer.advance()
            self.symbol_table.define(var_name, type_, Kind.ARG)

            if tokenizer.symbol() != ',':
                break
            tokenizer.advance()

    def compile_var_dec(self, tokenizer: JackTokenizer) -> int:
        """需要返回变量个数"""
        cur_n_locals = 0
        assert tokenizer.keyword() == 'var'
        tokenizer.advance()

        if tokenizer.token_type() == 'keyword':  # type
            type_ = tokenizer.keyword()
        else:
            type_ = tokenizer.identifier()
        tokenizer.advance()

        var_name = tokenizer.identifier()
        tokenizer.advance()
        self.symbol_table.define(var_name, type_, Kind.VAR)
        cur_n_locals += 1

        while tokenizer.has_more_tokens() and tokenizer.symbol() == ',':
            tokenizer.advance()

            var_name = tokenizer.identifier()
            tokenizer.advance()
            self.symbol_table.define(var_name, type_, Kind.VAR)
            cur_n_locals += 1

        assert tokenizer.symbol() == ';'
        tokenizer.advance()

        return cur_n_locals

    def compile_statements(self, tokenizer: JackTokenizer):
        while tokenizer.has_more_tokens() and tokenizer.symbol() != '}':
            statement_type = tokenizer.keyword()
            if statement_type == 'do':
                self.compile_do(tokenizer)
            elif statement_type == 'let':
                self.compile_let(tokenizer)
            elif statement_type == 'while':
                self.compile_while(tokenizer)
            elif statement_type == 'return':
                self.compile_return(tokenizer)
            elif statement_type == 'if':
                self.compile_if(tokenizer)

    def compile_do(self, tokenizer: JackTokenizer):
        expression_list_length = 0

        assert tokenizer.keyword() == 'do'
        tokenizer.advance()

        name = tokenizer.identifier()  # SubroutineName | ClassName | VarName
        tokenizer.advance()

        if self.symbol_table.kind_of(name) == Kind.STATIC:
            self.vm_writer.write_push(
                Segment.STATIC, self.symbol_table.index_of(name)
            )
            expression_list_length += 1

        elif self.symbol_table.kind_of(name) == Kind.FIELD:
            self.vm_writer.write_push(
                Segment.THIS, self.symbol_table.index_of(name)
            )
            expression_list_length += 1

        elif self.symbol_table.kind_of(name) == Kind.VAR:
            self.vm_writer.write_push(
                Segment.LOCAL, self.symbol_table.index_of(name)
            )
            expression_list_length += 1

        elif self.symbol_table.kind_of(name) == Kind.ARG:
            self.vm_writer.write_push(
                Segment.ARGUMENT, self.symbol_table.index_of(name)
            )
            expression_list_length += 1

        # 否者是一个类，则name是ClassName（如果后面有'.'）或者 SubroutineName（后面没有'.'）
        type_name = self.symbol_table.type_of(name)

        # 如果下一个是一个 .，表示这是一个另一个类的方法，则当前的name可能是ClassName或者VarName
        if tokenizer.symbol() == '.':  # 子程序名称总是要翻译成 ClassName.subroutineName
            tokenizer.advance()
            sub_name = tokenizer.identifier()
            tokenizer.advance()
            subroutine_name = f'{type_name}.{sub_name}'
        else:
            self.vm_writer.write_push(Segment.POINTER, 0)
            subroutine_name = f'{self.symbol_table.class_name}.{name}'
            expression_list_length += 1

        assert tokenizer.symbol() == '('
        tokenizer.advance()

        expression_list_length += self.compile_expression_list(tokenizer)

        assert tokenizer.symbol() == ')'
        tokenizer.advance()

        assert tokenizer.symbol() == ';'
        tokenizer.advance()

        self.vm_writer.write_call(subroutine_name, expression_list_length)

        self.vm_writer.write_pop(Segment.TEMP, 0)

    def compile_let(self, tokenizer: JackTokenizer):
        assert tokenizer.keyword() == 'let'
        tokenizer.advance()

        var_name = tokenizer.identifier()
        tokenizer.advance()

        if tokenizer.symbol() == '[':
            tokenizer.advance()

            self.compile_expression(tokenizer)

            assert tokenizer.symbol() == ']'
            tokenizer.advance()

            if self.symbol_table.kind_of(var_name) == Kind.FIELD:
                self.vm_writer.write_push(
                    Segment.POINTER, self.symbol_table.index_of(var_name)
                )
            elif self.symbol_table.kind_of(var_name) == Kind.STATIC:
                self.vm_writer.write_push(
                    Segment.STATIC, self.symbol_table.index_of(var_name)
                )
            elif self.symbol_table.kind_of(var_name) == Kind.ARG:
                self.vm_writer.write_push(
                    Segment.ARGUMENT, self.symbol_table.index_of(var_name)
                )
            elif self.symbol_table.kind_of(var_name) == Kind.VAR:
                self.vm_writer.write_push(
                    Segment.LOCAL, self.symbol_table.index_of(var_name)
                )
            else:
                raise NotImplementedError('这个数组我没见过。')
            self.vm_writer.write_arithmetic(Command.ADD)

            assert tokenizer.symbol() == '='
            tokenizer.advance()

            self.compile_expression(tokenizer)

            self.vm_writer.write_pop(Segment.TEMP, 0)
            self.vm_writer.write_pop(Segment.POINTER, 1)
            self.vm_writer.write_push(Segment.TEMP, 0)
            self.vm_writer.write_pop(Segment.THAT, 0)
        else:
            assert tokenizer.symbol() == '='
            tokenizer.advance()

            self.compile_expression(tokenizer)

            var_kind = self.symbol_table.kind_of(var_name)
            if var_kind == Kind.STATIC:
                self.vm_writer.write_pop(
                    Segment.STATIC, self.symbol_table.index_of(var_name)
                )
            elif var_kind == Kind.FIELD:
                self.vm_writer.write_pop(
                    Segment.THIS, self.symbol_table.index_of(var_name)
                )
            elif var_kind == Kind.VAR:
                self.vm_writer.write_pop(
                    Segment.LOCAL, self.symbol_table.index_of(var_name)
                )
            elif var_kind == Kind.ARG:
                self.vm_writer.write_pop(
                    Segment.ARGUMENT, self.symbol_table.index_of(var_name)
                )
            else:
                raise Exception('Unknown var kind')

        assert tokenizer.symbol() == ';'
        tokenizer.advance()

    def compile_while(self, tokenizer: JackTokenizer):
        assert tokenizer.keyword() == 'while'
        tokenizer.advance()

        cur_while_count = self.symbol_table.while_count
        self.symbol_table.while_count += 1
        self.vm_writer.write_label(f'WHILE_EXP{cur_while_count}')  # label L1

        assert tokenizer.symbol() == '('
        tokenizer.advance()

        self.compile_expression(tokenizer)

        assert tokenizer.symbol() == ')'
        tokenizer.advance()

        self.vm_writer.write_arithmetic(Command.NOT)  # 计算 ~(cond) 的值

        self.vm_writer.write_if(f'WHILE_END{cur_while_count}')  # if-goto L2

        assert tokenizer.symbol() == '{'
        tokenizer.advance()

        self.compile_statements(tokenizer)

        assert tokenizer.symbol() == '}'
        tokenizer.advance()

        self.vm_writer.write_goto(f'WHILE_EXP{cur_while_count}')  # goto L1
        self.vm_writer.write_label(f'WHILE_END{cur_while_count}')  # label L2

    def compile_return(self, tokenizer: JackTokenizer) -> None:
        assert tokenizer.keyword() == 'return'
        tokenizer.advance()

        if tokenizer.symbol() == ';':
            tokenizer.advance()
            self.vm_writer.write_push(Segment.CONSTANT, 0)
            self.vm_writer.write_return()
        else:
            self.compile_expression(tokenizer)
            self.vm_writer.write_return()

            assert tokenizer.symbol() == ';'
            tokenizer.advance()

    def compile_if(self, tokenizer: JackTokenizer):
        assert tokenizer.keyword() == 'if'
        tokenizer.advance()

        assert tokenizer.symbol() == '('
        tokenizer.advance()

        self.compile_expression(tokenizer)

        assert tokenizer.symbol() == ')'
        tokenizer.advance()

        cur_if_count = self.symbol_table.if_count
        self.symbol_table.if_count += 1

        self.vm_writer.write_if(f'IF_TRUE{cur_if_count}')  # if-goto L1
        self.vm_writer.write_goto(f'IF_FALSE{cur_if_count}')  # goto L2

        self.vm_writer.write_label(f'IF_TRUE{cur_if_count}')  # label L1
        assert tokenizer.symbol() == '{'
        tokenizer.advance()

        self.compile_statements(tokenizer)

        assert tokenizer.symbol() == '}'
        tokenizer.advance()

        if tokenizer.has_more_tokens() and tokenizer.keyword() == 'else':
            tokenizer.advance()

            self.vm_writer.write_goto(f'IF_END{cur_if_count}')

            self.vm_writer.write_label(f'IF_FALSE{cur_if_count}')  # label L2

            assert tokenizer.symbol() == '{'  # {
            tokenizer.advance()

            self.compile_statements(tokenizer)

            assert tokenizer.symbol() == '}'
            tokenizer.advance()

            self.vm_writer.write_label(f'IF_END{cur_if_count}')  # label L2

        else:
            self.vm_writer.write_label(f'IF_FALSE{cur_if_count}')  # label L2

    def compile_expression(self, tokenizer: JackTokenizer) -> list[str] | None:

        self.compile_term(tokenizer)

        while tokenizer.has_more_tokens() and tokenizer.symbol() in OP_SET:
            op = tokenizer.symbol()
            tokenizer.advance()

            self.compile_term(tokenizer)

            if op == '+':
                self.vm_writer.write_arithmetic(Command.ADD)
            elif op == '-':
                self.vm_writer.write_arithmetic(Command.SUB)
            elif op == '*':
                self.vm_writer.write_call('Math.multiply', 2)
            elif op == '/':
                self.vm_writer.write_call('Math.divide', 2)
            elif op == '&':
                self.vm_writer.write_arithmetic(Command.AND)
            elif op == '|':
                self.vm_writer.write_arithmetic(Command.OR)
            elif op == '<':
                self.vm_writer.write_arithmetic(Command.LT)
            elif op == '>':
                self.vm_writer.write_arithmetic(Command.GT)
            elif op == '=':
                self.vm_writer.write_arithmetic(Command.EQ)
            else:
                raise NotImplementedError()

    def compile_term(self, tokenizer: JackTokenizer):
        token_type = tokenizer.token_type()
        if token_type == 'integerConstant':
            self.vm_writer.write_push(Segment.CONSTANT, tokenizer.int_val())
            tokenizer.advance()
        elif token_type == 'stringConstant':
            string_val = tokenizer.string_val()
            tokenizer.advance()

            self.vm_writer.write_push(Segment.CONSTANT, len(string_val))
            self.vm_writer.write_call('String.new', 1)
            for c in string_val:
                self.vm_writer.write_push(Segment.CONSTANT, ord(c))
                self.vm_writer.write_call('String.appendChar', 2)
        elif tokenizer.keyword() in KEYWORD_CONSTANT:
            if tokenizer.keyword() == 'null' or tokenizer.keyword() == 'false':
                tokenizer.advance()
                self.vm_writer.write_push(Segment.CONSTANT, 0)
            elif tokenizer.keyword() == 'true':
                tokenizer.advance()
                self.vm_writer.write_push(Segment.CONSTANT, 0)
                self.vm_writer.write_arithmetic(Command.NOT)
            elif tokenizer.keyword() == 'this':  # TODO 这个 this 的使用不是很理解
                tokenizer.advance()
                self.vm_writer.write_push(Segment.POINTER, 0)
            else:
                raise NotImplementedError('关键字常量暂未实现')
        elif token_type == 'identifier':
            name = tokenizer.identifier()
            tokenizer.advance()

            if tokenizer.symbol() == '[':  # 如果是数组，则需要计算索引
                tokenizer.advance()

                self.compile_expression(tokenizer)

                assert tokenizer.symbol() == ']'
                tokenizer.advance()

                if self.symbol_table.kind_of(name) == Kind.FIELD:
                    self.vm_writer.write_push(
                        Segment.POINTER, self.symbol_table.index_of(name)
                    )
                elif self.symbol_table.kind_of(name) == Kind.STATIC:
                    self.vm_writer.write_push(
                        Segment.STATIC, self.symbol_table.index_of(name)
                    )
                elif self.symbol_table.kind_of(name) == Kind.ARG:
                    self.vm_writer.write_push(
                        Segment.ARGUMENT, self.symbol_table.index_of(name)
                    )
                elif self.symbol_table.kind_of(name) == Kind.VAR:
                    self.vm_writer.write_push(
                        Segment.LOCAL, self.symbol_table.index_of(name)
                    )
                else:
                    raise NotImplementedError('这个数组我没见过。')
                self.vm_writer.write_arithmetic(Command.ADD)
                self.vm_writer.write_pop(Segment.POINTER, 1)
                self.vm_writer.write_push(Segment.THAT, 0)

            elif tokenizer.symbol() == '(' or tokenizer.symbol() == '.':
                n_args = 0
                if tokenizer.symbol() == '.':
                    tokenizer.advance()
                    if self.symbol_table.kind_of(name) == Kind.FIELD:
                        n_args += 1
                        self.vm_writer.write_push(Segment.THIS, self.symbol_table.index_of(name))
                    elif self.symbol_table.kind_of(name) == Kind.STATIC:
                        n_args += 1
                        self.vm_writer.write_push(Segment.STATIC, self.symbol_table.index_of(name))
                    elif self.symbol_table.kind_of(name) == Kind.VAR:
                        n_args += 1
                        self.vm_writer.write_push(Segment.LOCAL, self.symbol_table.index_of(name))
                    elif self.symbol_table.kind_of(name) == Kind.ARG:
                        n_args += 1
                        self.vm_writer.write_push(Segment.ARGUMENT, self.symbol_table.index_of(name))
                    subroutine_name = f'{self.symbol_table.type_of(name)}.{tokenizer.identifier()}'
                    tokenizer.advance()
                else:
                    subroutine_name = name
                assert tokenizer.symbol() == '('
                tokenizer.advance()

                n_args += self.compile_expression_list(tokenizer)

                assert tokenizer.symbol() == ')'
                tokenizer.advance()
                self.vm_writer.write_call(subroutine_name, n_args)
            else:
                kind_name = self.symbol_table.kind_of(name)
                if kind_name == Kind.STATIC:
                    self.vm_writer.write_push(
                        Segment.STATIC, self.symbol_table.index_of(name)
                    )
                elif kind_name == Kind.FIELD:
                    self.vm_writer.write_push(
                        Segment.THIS, self.symbol_table.index_of(name)
                    )
                elif kind_name == Kind.ARG:
                    self.vm_writer.write_push(
                        Segment.ARGUMENT, self.symbol_table.index_of(name)
                    )
                elif kind_name == Kind.VAR:
                    self.vm_writer.write_push(
                        Segment.LOCAL, self.symbol_table.index_of(name)
                    )
                else:
                    raise NotImplementedError()

        elif tokenizer.symbol() == '(':
            tokenizer.advance()
            self.compile_expression(tokenizer)
            assert tokenizer.symbol() == ')'
            tokenizer.advance()
        elif tokenizer.symbol() in UNARY_OP_SET:
            op = tokenizer.symbol()
            tokenizer.advance()

            self.compile_term(tokenizer)
            if op == '-':
                self.vm_writer.write_arithmetic(Command.NEG)
            elif op == '~':
                self.vm_writer.write_arithmetic(Command.NOT)
            else:
                raise NotImplementedError()
        else:
            raise NotImplementedError()

    def compile_expression_list(self, tokenizer: JackTokenizer) -> int:
        # 需要返回表达式列表的长度，因为调用函数的时候需要知道参数个数
        expression_list_length = 0
        if tokenizer.symbol() == ')':
            return 0
        while tokenizer.symbol() != ')':
            self.compile_expression(tokenizer)
            if tokenizer.symbol() == ',':
                tokenizer.advance()
            expression_list_length += 1
        return expression_list_length


class CompilationEngineAsXML(CompilationEngine):
    def __init__(self, output_file: Path | None = None):
        self.output_file = output_file

    def __call__(self, tokenizer: JackTokenizer) -> list[str] | None:
        """调用CompilationEngine的对象时，将根据初始时设置的out_file来设置保存位置"""
        results = [
            *self.compile_class(tokenizer),
        ]

        if self.output_file:
            self.output_file.write_text('\n'.join(results))
        else:
            return results

    @classmethod
    def compile_class(cls, tokenizer: JackTokenizer) -> list[str] | None:
        """编译类"""
        results = ['<class>']
        results.extend(
            [f'<keyword> {tokenizer.keyword()} </keyword>']
        )  # class
        tokenizer.advance()

        results.extend(
            [
                f'<identifier> {tokenizer.identifier()} </identifier>',
            ]  # className
        )
        tokenizer.advance()

        results.extend([f'<symbol> {tokenizer.symbol()} </symbol>'])  # {
        tokenizer.advance()
        while tokenizer.has_more_tokens and (
            tokenizer.keyword() == 'static' or tokenizer.keyword() == 'field'
        ):  # classVarDec
            results.extend(
                cls.compile_class_var_dec(tokenizer),
            )
            tokenizer.advance()
        while tokenizer.has_more_tokens and (
            tokenizer.keyword() == 'constructor'
            or tokenizer.keyword() == 'function'
            or tokenizer.keyword() == 'method'
        ):  # subroutineDec
            results.extend(cls.compile_subroutine(tokenizer))
            tokenizer.advance()

        results.extend([f'<symbol> {tokenizer.symbol()} </symbol>'])  # }
        results.append('</class>')
        return results

    @classmethod
    def compile_class_var_dec(cls, tokenizer: JackTokenizer) -> list[str]:
        """编译静态声明或字段声明"""
        results = [
            '<classVarDec>',
            f'<{tokenizer.token_type()}> {tokenizer.keyword()} </{tokenizer.token_type()}>',
        ]  # static | field

        tokenizer.advance()

        if tokenizer.token_type() == 'keyword':  # type
            results.append(
                f'<{tokenizer.token_type()}> {tokenizer.keyword()} </{tokenizer.token_type()}>'
            )  # int | char | boolean
        else:
            results.append(
                f'<{tokenizer.token_type()}> {tokenizer.identifier()} </{tokenizer.token_type()}>'
            )  # className
        tokenizer.advance()

        results.append(
            f'<{tokenizer.token_type()}> {tokenizer.identifier()} </{tokenizer.token_type()}>'
        )  # varName
        tokenizer.advance()

        while (
            tokenizer.has_more_tokens() and tokenizer.symbol() == ','
        ):  # (, varName)*
            results.append(
                f'<{tokenizer.token_type()}> {tokenizer.symbol()} </{tokenizer.token_type()}>'
            )
            tokenizer.advance()
            results.append(
                f'<{tokenizer.token_type()}> {tokenizer.identifier()} </{tokenizer.token_type()}>'
            )
            tokenizer.advance()
        results.extend(
            [
                f'<{tokenizer.token_type()}> {tokenizer.symbol()} </{tokenizer.token_type()}>',
                '</classVarDec>',
            ]
        )   # ;
        return results

    @classmethod
    def compile_subroutine(cls, tokenizer: JackTokenizer) -> list[str]:
        """编译整个方法、函数或构造函数"""
        results = [
            '<subroutineDec>',
            f'<{tokenizer.token_type()}> {tokenizer.keyword()} </{tokenizer.token_type()}>',
        ]
        tokenizer.advance()

        if tokenizer.token_type() == 'keyword':  # void | type
            results.append(
                f'<{tokenizer.token_type()}> {tokenizer.keyword()} </{tokenizer.token_type()}>'
            )  # int | char | boolean | void
        else:
            results.append(
                f'<{tokenizer.token_type()}> {tokenizer.identifier()} </{tokenizer.token_type()}>'
            )  # className
        tokenizer.advance()

        results.append(
            f'<{tokenizer.token_type()}> {tokenizer.identifier()} </{tokenizer.token_type()}>'
        )  # subroutineName
        tokenizer.advance()

        results.append(
            f'<{tokenizer.token_type()}> {tokenizer.symbol()} </{tokenizer.token_type()}>'
        )  # (
        tokenizer.advance()

        results.extend(cls.compile_parameter_list(tokenizer))

        results.append(
            f'<{tokenizer.token_type()}> {tokenizer.symbol()} </{tokenizer.token_type()}>'
        )  # )
        tokenizer.advance()

        results.extend(
            [
                '<subroutineBody>',
                f'<{tokenizer.token_type()}> {tokenizer.symbol()} </{tokenizer.token_type()}>',
            ]
        )  # {
        tokenizer.advance()

        while (
            tokenizer.has_more_tokens() and tokenizer.keyword() == 'var'
        ):  # varDec*
            results.extend(cls.compile_var_dec(tokenizer))
            tokenizer.advance()

        if tokenizer.symbol() != '}':  # statements
            results.extend(cls.compile_statements(tokenizer))

        results.extend(
            [
                f'<{tokenizer.token_type()}> {tokenizer.symbol()} </{tokenizer.token_type()}>',
                '</subroutineBody>',
                '</subroutineDec>',
            ]
        )  # }
        return results

    @classmethod
    def compile_parameter_list(cls, tokenizer: JackTokenizer) -> list[str]:
        results = ['<parameterList>']
        if not tokenizer.has_more_tokens() or tokenizer.symbol() == ')':
            results.append('</parameterList>')
            return results
        if tokenizer.token_type() == 'keyword':  # type
            results.append(
                f'<{tokenizer.token_type()}> {tokenizer.keyword()} </{tokenizer.token_type()}>'
            )
        else:
            results.append(
                f'<{tokenizer.token_type()}> {tokenizer.identifier()} </{tokenizer.token_type()}>'
            )
        tokenizer.advance()

        results.append(
            f'<{tokenizer.token_type()}> {tokenizer.identifier()} </{tokenizer.token_type()}>'
        )  # varName
        tokenizer.advance()

        while tokenizer.has_more_tokens() and tokenizer.symbol() == ',':
            results.append(
                f'<{tokenizer.token_type()}> {tokenizer.symbol()} </{tokenizer.token_type()}>',
            )  # ,
            tokenizer.advance()

            if tokenizer.token_type() == 'keyword':  # type
                results.append(
                    f'<{tokenizer.token_type()}> {tokenizer.keyword()} </{tokenizer.token_type()}>'
                )
            else:
                results.append(
                    f'<{tokenizer.token_type()}> {tokenizer.identifier()} </{tokenizer.token_type()}>'
                )
            tokenizer.advance()

            results.append(
                f'<{tokenizer.token_type()}> {tokenizer.identifier()} </{tokenizer.token_type()}>'
            )  # varName
            tokenizer.advance()

        results.append('</parameterList>')
        return results

    @classmethod
    def compile_var_dec(cls, tokenizer: JackTokenizer) -> list[str]:
        results = [
            '<varDec>',
            f'<{tokenizer.token_type()}> {tokenizer.keyword()} </{tokenizer.token_type()}>',
        ]   # var
        tokenizer.advance()

        if tokenizer.token_type() == 'keyword':  # type
            results.append(
                f'<{tokenizer.token_type()}> {tokenizer.keyword()} </{tokenizer.token_type()}>'
            )  # int | char | boolean
        else:
            results.append(
                f'<{tokenizer.token_type()}> {tokenizer.identifier()} </{tokenizer.token_type()}>'
            )  # className
        tokenizer.advance()

        results.append(
            f'<{tokenizer.token_type()}> {tokenizer.identifier()} </{tokenizer.token_type()}>'
        )  # varName
        tokenizer.advance()

        while tokenizer.has_more_tokens() and tokenizer.symbol() == ',':
            results.append(
                f'<{tokenizer.token_type()}> {tokenizer.symbol()} </{tokenizer.token_type()}>'
            )  # ,
            tokenizer.advance()

            results.append(
                f'<{tokenizer.token_type()}> {tokenizer.identifier()} </{tokenizer.token_type()}>'
            )  # varName
            tokenizer.advance()

        results.extend(
            [
                f'<{tokenizer.token_type()}> {tokenizer.symbol()} </{tokenizer.token_type()}>',
                '</varDec>',
            ]
        )  # ;
        return results

    @classmethod
    def compile_statements(cls, tokenizer: JackTokenizer) -> list[str]:
        results = ['<statements>']
        if tokenizer.keyword() not in {'do', 'let', 'while', 'return', 'if'}:
            results.append('</statements>')
            return results
        while tokenizer.has_more_tokens() and tokenizer.keyword() in {
            'do',
            'let',
            'while',
            'return',
            'if',
        }:
            if tokenizer.keyword() == 'do':
                results.extend(cls.compile_do(tokenizer))
            elif tokenizer.keyword() == 'let':
                results.extend(cls.compile_let(tokenizer))
            elif tokenizer.keyword() == 'while':
                results.extend(cls.compile_while(tokenizer))
            elif tokenizer.keyword() == 'return':
                results.extend(cls.compile_return(tokenizer))
            elif tokenizer.keyword() == 'if':
                results.extend(cls.compile_if(tokenizer))
            else:
                raise ValueError(f'Invalid keyword: {tokenizer.keyword()}')
        results.append('</statements>')
        return results

    @classmethod
    def compile_do(cls, tokenizer: JackTokenizer) -> list[str]:
        results = [
            '<doStatement>',
            f'<{tokenizer.token_type()}> {tokenizer.keyword()} </{tokenizer.token_type()}>',
        ]  # do
        tokenizer.advance()

        results.append(
            f'<{tokenizer.token_type()}> {tokenizer.identifier()} </{tokenizer.token_type()}>'
        )  # className | varName | subroutineName
        tokenizer.advance()

        if tokenizer.symbol() == '.':
            results.append(
                f'<{tokenizer.token_type()}> {tokenizer.symbol()} </{tokenizer.token_type()}>'
            )  # .
            tokenizer.advance()

            results.append(
                f'<{tokenizer.token_type()}> {tokenizer.identifier()} </{tokenizer.token_type()}>'
            )  # subroutineName
            tokenizer.advance()

        results.append(
            f'<{tokenizer.token_type()}> {tokenizer.symbol()} </{tokenizer.token_type()}>'
        )  # (
        tokenizer.advance()

        results.extend(cls.compile_expression_list(tokenizer))

        results.append(
            f'<{tokenizer.token_type()}> {tokenizer.symbol()} </{tokenizer.token_type()}>'
        )  # )
        tokenizer.advance()

        results.extend(
            [
                f'<{tokenizer.token_type()}> {tokenizer.symbol()} </{tokenizer.token_type()}>',  # ;
                '</doStatement>',
            ]
        )
        tokenizer.advance()

        return results

    @classmethod
    def compile_let(cls, tokenizer: JackTokenizer) -> list[str]:
        results = [
            '<letStatement>',
            f'<{tokenizer.token_type()}> {tokenizer.keyword()} </{tokenizer.token_type()}>',
        ]   # let
        tokenizer.advance()

        results.append(
            f'<{tokenizer.token_type()}> {tokenizer.identifier()} </{tokenizer.token_type()}>'
        )   # varName
        tokenizer.advance()

        if tokenizer.symbol() == '[':
            results.append(
                f'<{tokenizer.token_type()}> {tokenizer.symbol()} </{tokenizer.token_type()}>'
            )  # [
            tokenizer.advance()

            results.extend(cls.compile_expression(tokenizer))  # expression

            results.append(
                f'<{tokenizer.token_type()}> {tokenizer.symbol()} </{tokenizer.token_type()}>'
            )  # ]
            tokenizer.advance()

        results.append(
            f'<{tokenizer.token_type()}> {tokenizer.symbol()} </{tokenizer.token_type()}>'
        )   # =
        tokenizer.advance()

        results.extend(cls.compile_expression(tokenizer))

        results.append(
            f'<{tokenizer.token_type()}> {tokenizer.symbol()} </{tokenizer.token_type()}>'
        )  # ;
        tokenizer.advance()

        results.append('</letStatement>')
        return results

    @classmethod
    def compile_while(cls, tokenizer: JackTokenizer) -> list[str]:
        results = [
            '<whileStatement>',
            f'<{tokenizer.token_type()}> {tokenizer.keyword()} </{tokenizer.token_type()}>',
        ]
        tokenizer.advance()

        results.append(
            f'<{tokenizer.token_type()}> {tokenizer.symbol()} </{tokenizer.token_type()}>'
        )
        tokenizer.advance()

        results.extend(cls.compile_expression(tokenizer))

        results.append(
            f'<{tokenizer.token_type()}> {tokenizer.symbol()} </{tokenizer.token_type()}>'
        )
        tokenizer.advance()

        results.append(
            f'<{tokenizer.token_type()}> {tokenizer.symbol()} </{tokenizer.token_type()}>'
        )
        tokenizer.advance()

        results.extend(cls.compile_statements(tokenizer))

        results.append(
            f'<{tokenizer.token_type()}> {tokenizer.symbol()} </{tokenizer.token_type()}>'
        )
        tokenizer.advance()

        results.append('</whileStatement>')
        return results

    @classmethod
    def compile_return(cls, tokenizer: JackTokenizer) -> list[str]:
        results = [
            '<returnStatement>',
            f'<{tokenizer.token_type()}> {tokenizer.keyword()} </{tokenizer.token_type()}>',
        ]
        tokenizer.advance()

        if tokenizer.symbol() != ';':
            results.extend(cls.compile_expression(tokenizer))

        results.extend(
            [
                f'<{tokenizer.token_type()}> {tokenizer.symbol()} </{tokenizer.token_type()}>',
                '</returnStatement>',
            ]
        )
        tokenizer.advance()

        return results

    @classmethod
    def compile_if(cls, tokenizer: JackTokenizer) -> list[str]:
        results = [
            '<ifStatement>',
            f'<{tokenizer.token_type()}> {tokenizer.keyword()} </{tokenizer.token_type()}>',
        ]
        tokenizer.advance()

        results.append(
            f'<{tokenizer.token_type()}> {tokenizer.symbol()} </{tokenizer.token_type()}>'
        )  # (
        tokenizer.advance()

        results.extend(cls.compile_expression(tokenizer))

        results.append(
            f'<{tokenizer.token_type()}> {tokenizer.symbol()} </{tokenizer.token_type()}>'
        )  # )
        tokenizer.advance()

        results.append(
            f'<{tokenizer.token_type()}> {tokenizer.symbol()} </{tokenizer.token_type()}>'
        )  # {
        tokenizer.advance()

        results.extend(cls.compile_statements(tokenizer))

        results.append(
            f'<{tokenizer.token_type()}> {tokenizer.symbol()} </{tokenizer.token_type()}>'
        )   # }
        tokenizer.advance()

        if tokenizer.has_more_tokens() and tokenizer.keyword() == 'else':
            results.append(
                f'<{tokenizer.token_type()}> {tokenizer.keyword()} </{tokenizer.token_type()}>'
            )
            tokenizer.advance()

            results.append(
                f'<{tokenizer.token_type()}> {tokenizer.symbol()} </{tokenizer.token_type()}>'
            )  # {
            tokenizer.advance()

            results.extend(cls.compile_statements(tokenizer))

            results.append(
                f'<{tokenizer.token_type()}> {tokenizer.symbol()} </{tokenizer.token_type()}>'
            )   # }
            tokenizer.advance()

        results.append('</ifStatement>')
        return results

    @classmethod
    def compile_expression(cls, tokenizer: JackTokenizer) -> list[str]:
        results = ['<expression>']
        results.extend(cls.compile_term(tokenizer))

        while tokenizer.has_more_tokens() and tokenizer.symbol() in OP_SET:
            cur_token = tokenizer.symbol()
            if cur_token == '<':
                cur_token = '&lt;'
            elif cur_token == '>':
                cur_token = '&gt;'
            elif cur_token == '&':
                cur_token = '&amp;'
            results.append(
                f'<{tokenizer.token_type()}> {cur_token} </{tokenizer.token_type()}>'
            )  # op
            tokenizer.advance()

            results.extend(cls.compile_term(tokenizer))

        results.append('</expression>')
        return results

    @classmethod
    def compile_term(cls, tokenizer: JackTokenizer) -> list[str]:
        results = ['<term>']
        if tokenizer.token_type() == 'integerConstant':  # integerConstant
            results.append(
                f'<{tokenizer.token_type()}> {tokenizer.int_val()} </{tokenizer.token_type()}>'
            )
            tokenizer.advance()
        elif tokenizer.token_type() == 'stringConstant':  # stringConstant
            results.append(
                f'<{tokenizer.token_type()}> {tokenizer.string_val()} </{tokenizer.token_type()}>'
            )
            tokenizer.advance()
        elif tokenizer.keyword() in {
            'true',
            'false',
            'null',
            'this',
        }:  # keywordConstant
            results.append(
                f'<{tokenizer.token_type()}> {tokenizer.keyword()} </{tokenizer.token_type()}>'
            )
            tokenizer.advance()
        elif (
            tokenizer.token_type() == 'identifier'
        ):  # varName | varName[expression] | subroutineCall
            results.append(
                f'<{tokenizer.token_type()}> {tokenizer.identifier()} </{tokenizer.token_type()}>'
            )
            tokenizer.advance()

            # 需要判断后续是否是有括号
            if tokenizer.symbol() in '[':  # varName[expression]
                results.append(
                    f'<{tokenizer.token_type()}> {tokenizer.symbol()} </{tokenizer.token_type()}>'
                )  # [
                tokenizer.advance()

                results.extend(cls.compile_expression(tokenizer))

                results.append(
                    f'<{tokenizer.token_type()}> {tokenizer.symbol()} </{tokenizer.token_type()}>'
                )  # ]
                tokenizer.advance()

            elif (
                tokenizer.symbol() == '(' or tokenizer.symbol() == '.'
            ):  # subroutineCall

                if tokenizer.symbol() == '.':
                    results.append(
                        f'<{tokenizer.token_type()}> {tokenizer.symbol()} </{tokenizer.token_type()}>'
                    )  # .
                    tokenizer.advance()

                    results.append(
                        f'<{tokenizer.token_type()}> {tokenizer.identifier()} </{tokenizer.token_type()}>'
                    )  # subroutineName
                    tokenizer.advance()

                results.append(
                    f'<{tokenizer.token_type()}> {tokenizer.symbol()} </{tokenizer.token_type()}>'
                )  # (
                tokenizer.advance()

                results.extend(cls.compile_expression_list(tokenizer))

                results.append(
                    f'<{tokenizer.token_type()}> {tokenizer.symbol()} </{tokenizer.token_type()}>'
                )  # )
                tokenizer.advance()

        elif tokenizer.symbol() == '(':
            results.append(
                f'<{tokenizer.token_type()}> {tokenizer.symbol()} </{tokenizer.token_type()}>'
            )
            tokenizer.advance()

            results.extend(cls.compile_expression(tokenizer))  # expression

            results.append(
                f'<{tokenizer.token_type()}> {tokenizer.symbol()} </{tokenizer.token_type()}>'
            )
            tokenizer.advance()
        elif tokenizer.symbol() in UNARY_OP_SET:  # unaryOp term
            results.append(
                f'<{tokenizer.token_type()}> {tokenizer.symbol()} </{tokenizer.token_type()}>'
            )
            tokenizer.advance()

            results.extend(cls.compile_term(tokenizer))
        else:
            raise NotImplementedError('Term is not implemented yet.')

        results.append('</term>')

        return results

    @classmethod
    def compile_expression_list(cls, tokenizer: JackTokenizer) -> list[str]:
        results = ['<expressionList>']
        if tokenizer.symbol() == ')':
            results.append('</expressionList>')
            return results

        results.extend(cls.compile_expression(tokenizer))

        while tokenizer.has_more_tokens() and tokenizer.symbol() == ',':
            results.append(
                f'<{tokenizer.token_type()}> {tokenizer.symbol()} </{tokenizer.token_type()}>'
            )
            tokenizer.advance()

            results.extend(cls.compile_expression(tokenizer))

        results.append('</expressionList>')

        return results


class CompilationEngineCreator:
    def create(self, *, engine_type: str, output_file: Path):
        if engine_type == 'xml':
            return CompilationEngineAsXML(output_file)
        elif engine_type == 'vm':
            return CompilationEngineAsVM(output_file)
        else:
            raise NotImplementedError('Engine type is not implemented yet.')


if __name__ == '__main__':
    target = Path('syntax_analysis_outputs/Pong/Bat.vm')
    actual = [line for line in target.read_text().split('\n') if line]

    answer = Path('chapter11_data/Pong/Bat.vm')
    expected = [line for line in answer.read_text().split('\n') if line]
    for line_no, (a, e) in enumerate(zip(actual, expected)):
        if e != a:
            print(f'{line_no + 1}: 答案是{e} != 实际是{a}')
            break


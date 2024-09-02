import pytest

from symbol_table import SymbolTable, Kind


class TestSymbolTable:
    def test_init(self) -> None:
        symbol_table = SymbolTable()
        assert symbol_table.class_table == {}
        assert symbol_table.subroutine_table == {}

    def test_define(self) -> None:
        symbol_table = SymbolTable()
        symbol_table.define('x', 'int', Kind.STATIC)
        assert symbol_table.class_table == {'x': ('int', Kind.STATIC, 0)}

        symbol_table.define('y', 'int', Kind.STATIC)
        assert symbol_table.class_table == {
            'x': ('int', Kind.STATIC, 0),
            'y': ('int', Kind.STATIC, 1),
        }

        symbol_table.define('z', 'int', Kind.FIELD)
        assert symbol_table.class_table == {
            'x': ('int', Kind.STATIC, 0),
            'y': ('int', Kind.STATIC, 1),
            'z': ('int', Kind.FIELD, 0),
        }

        symbol_table.define('w', 'int', Kind.ARG)
        assert symbol_table.subroutine_table == {'w': ('int', Kind.ARG, 0)}

        symbol_table.define('v', 'int', Kind.VAR)
        assert symbol_table.subroutine_table == {
            'w': ('int', Kind.ARG, 0),
            'v': ('int', Kind.VAR, 0),
        }

    def test_var_count(self) -> None:
        symbol_table = SymbolTable()
        assert symbol_table.var_count(Kind.STATIC) == 0

        symbol_table.define('x', 'int', Kind.STATIC)
        assert symbol_table.var_count(Kind.STATIC) == 1

        symbol_table.define('v', 'int', Kind.VAR)
        assert symbol_table.var_count(Kind.VAR) == 1

    def test_kind_of(self) -> None:
        symbol_table = SymbolTable()
        symbol_table.define('x', 'int', Kind.STATIC)
        assert symbol_table.kind_of('x') == Kind.STATIC

    def test_type_of(self) -> None:
        symbol_table = SymbolTable()
        symbol_table.define('x', 'int', Kind.STATIC)
        assert symbol_table.type_of('x') == 'int'

    def test_index_of(self) -> None:
        symbol_table = SymbolTable()
        symbol_table.define('x', 'int', Kind.STATIC)
        assert symbol_table.index_of('x') == 0


if __name__ == '__main__':
    pytest.main()

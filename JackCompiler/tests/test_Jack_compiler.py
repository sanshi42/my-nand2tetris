import pytest
from pathlib import Path
from Jack_compiler import execute_jack_compiler


class TestJackTokenizer:
    def test_simple_program(self) -> None:
        source = Path('chapter11_data/ArrayTest')
        target = Path('chapter11_data/ArrayTest')
        execute_jack_compiler(source, target)


if __name__ == '__main__':
    pytest.main()

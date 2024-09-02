from pathlib import Path

import pytest

from vm_writer import VMWriter, Segment, Command


class TestVMWriter:
    def test_write_push(self) -> None:
        vm_writer = VMWriter()
        assert vm_writer.write_push(Segment.CONSTANT, 0) == 'push constant 0'

    def test_write_pop(self) -> None:
        vm_writer = VMWriter()
        assert vm_writer.write_pop(Segment.CONSTANT, 0) == 'pop constant 0'

    def test_write_arithmetic(self) -> None:
        vm_writer = VMWriter()
        assert vm_writer.write_arithmetic(Command.ADD) == 'add'

    def test_write_label(self) -> None:
        vm_writer = VMWriter()
        assert vm_writer.write_label('test') == '(test)'

    def test_write_goto(self) -> None:
        vm_writer = VMWriter()
        assert vm_writer.write_goto('test') == 'goto test'

    def test_write_if(self) -> None:
        vm_writer = VMWriter()
        assert vm_writer.write_if('test') == 'if-goto test'

    def test_write_call(self) -> None:
        vm_writer = VMWriter()
        assert vm_writer.write_call('test', 2) == 'call test 2'

    def test_write_function(self) -> None:
        vm_writer = VMWriter()
        assert vm_writer.write_function('test', 2) == 'function test 2'

    def test_write_return(self) -> None:
        vm_writer = VMWriter()
        assert vm_writer.write_return() == 'return'


if __name__ == '__main__':
    pytest.main()

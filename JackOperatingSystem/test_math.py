from pathlib import Path
import os

import pytest


class TestMath:
    def test_math(self):
        source = Path('MathTest/Math.vm').read_text().split('\n')
        target = Path('Math.vm').read_text().split('\n')
        for i, (s, t) in enumerate(zip(source, target)):
            assert s == t, f'第 {i+1} 行不一致'


if __name__ == '__main__':
    output = os.popen(
        'bash /home/huanglei/workspace/my-software-architecture-learning/nand2tetris/tools/JackCompiler.sh /home/huanglei/workspace/my-software-architecture-learning/nand2tetris/JackOperatingSystem/MathTest/'
    ).read()
    print(output)
    pytest.main()

"""语法分析器的模块之一：建立和调用其他模块的顶层驱动模块"""
import sys
from pathlib import Path

from compilation_engine import CompilationEngineCreator
from Jack_tokenizer import JackTokenizer


def execute_jack_compiler(source_path: Path, target_path: Path) -> None:
    for file_name in source_path.iterdir():
        if file_name.suffix != '.jack':
            continue
        with file_name.open() as f:
            source_code = f.readlines()
        tokenizer = JackTokenizer(source_code)

        cur_target = target_path / (file_name.stem + '.vm')

        compilation_engine_creator = CompilationEngineCreator()
        compilation_engine = compilation_engine_creator.create(engine_type='vm', output_file=cur_target)

        compilation_engine(tokenizer)


def execute_syntax_analysis_as_xml(source: Path, target: Path) -> None:
    """Jack 语法分析程序

    对于每个源 xxx.jack 文件，执行以下步骤：
        1. 从 xxx.jack 输入中创建 JackTokenizer 对象；
        2. 创建名为 xxx.xml 的输出文件，准备写文件；
        3. 使用 CompilationEngine 来将输入的 JackTokenizer 对象编译成输出文件。

    Args:
        source: 形如 xxx.jack 的 Jack 源代码文件名或者包含若干个此类文件的路径名。
        target: 输出文件所在的路径。
    """
    target.mkdir(parents=True, exist_ok=True)
    for file_name in source.iterdir():
        if file_name.suffix != '.jack':
            continue
        with file_name.open() as f:
            source_code = f.readlines()
        tokenizer = JackTokenizer(source_code)

        cur_target = target / (file_name.stem + '.xml')
        compilation_engine_creator = CompilationEngineCreator()
        compilation_engine = compilation_engine_creator.create(engine_type='xml', output_file=cur_target)
        compilation_engine(tokenizer)


# if __name__ == '__main__':
#     if len(sys.argv) == 2:
#         source_path = sys.argv[1]
#         source = Path(source_path)
#         if source.is_dir():
#             execute_jack_compiler(source)
#         elif source.is_file():
#             execute_jack_compiler(source)
#
#


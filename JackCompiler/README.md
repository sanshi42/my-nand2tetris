# Jack 编译器

## 代码生成约定

**文件命名和函数命名**

- 每个 .jack 文件被编译成独立的 .vm 文件。
- Jack子程序（函数、方法和构造函数）被编译成下列的 VM 函数：
  - 在 Jack 程序中，类 Yyy 中的 Jack 子程序 Xxx

## 功能点

**第 1 阶段：字元转换器**

- [x] Square Dance：编写完成 xxxT.xml 并经过 TextCompare 测试通过
- [x] Array Test：编写完成 xxxT.xml 并经过 TextCompare 测试通过

**第 2 阶段：语法分析器**

- [x] ExpressionLessSquare
- [x] Square Dance：编写完成并经过 TextCompare 测试通过
- [x] Array Test：编写完成并经过 TextCompare 测试通过

**第 3 阶段：符号表**

- [x] 直接使用写的单元测试

**第 4 阶段：代码生成**

- [x] 需要重构，将之前写入 xml 的内容改为写到 vm_writer

2**测试程序：**

- [x] Seven
- [x] 十进制-二进制转换
- [x] Square Dance
- [x] Average
- [x] Pong
- [x] Complex Arrays
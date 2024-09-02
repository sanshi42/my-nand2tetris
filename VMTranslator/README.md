# VM 翻译器

修改整体的逻辑，

## 实现步骤

**第一阶段：**堆栈运算命令

- [x] VM 语言的 9 个堆栈运算命令和逻辑命令
- [x] push constant x 命令；

测试程序：

**第二阶段：**内存访问命令

- [x] VM 语言中的 push 和 pop 命令的完整实现，能够处理所有的 8 个内存段。
  - [x] 0. 能够处理 constant 段
  - [x] 1. local段、argument段、this段、that段
  - [x] 2. pointer段、temp段，能够允许修改this段和that段的基地址
  - [x] 3. 处理static段

**完整手工测试**

- [x] 完整地测试一下：测试通过

**第三阶段：**分支命令

- [x] label 命令
- [x] goto 命令
- [x] if-goto 命令

**第四阶段：**函数命令

- [x] function 命令
- [x] call 命令——有点潦草，后面改进一下
- [x] return 命令

**完整手工测试程序**

- [x] SimpleAdd

- [x] StackTest

- [x] BasicTest

- [x] PointerTest

- [x] StaticTest

- [x] BasicLoop

- [x] FibonacciSeries

- [x] SimpleFunction

- [x] NestedCall

- [x] FibonacciElement

- [x] StaticsTest

  之后，整体好好完善吧，现在只能算是能够运行，整体的逻辑还有待进一步完善

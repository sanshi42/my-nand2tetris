// 输出宽度为16 pixel，高度为R0 pixel
    @SCREEN
    D=A
    @addr
    M=D

    @R0
    D=M
    @n
    M=D

    @i
    M=0

    (LOOP)
    @i
    D=M
    @n
    D=D-M
    @END
    D;JGT

    @addr
    A=M
    M=-1

    @32
    D=A
    @addr
    M=M+D
    @i
    M=M+1
    @LOOP
    0;JMP

    (END)
    @END
    0;JMP

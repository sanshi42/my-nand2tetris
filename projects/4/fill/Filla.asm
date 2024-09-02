@SCREEN

(CHECK)
    @KBD
    D=M
    @BLACK
    D;JGT
    @WHITE
    0;JMP

(WHITE)
    // i = 0
    @i
    M=0
    (LOOPA)
        // if(i==8192) goto CHECK;
        @8192
        D=A
        @i
        D=M-D
        @CHECK
        D;JEQ

        @i
        D=M
        @SCREEN
        A=A+D
        M=0

        @i
        M=M+1

        @LOOPA
        0;JMP


(BLACK)
    // i = 0
    @i
    M=0
    (LOOPB)
        // if(i==8192) goto CHECK;
        @8192
        D=A
        @i
        D=M-D
        @CHECK
        D;JEQ

        @i
        D=M
        @SCREEN
        A=A+D
        M=-1

        @i
        M=M+1

        @LOOPB
        0;JMP

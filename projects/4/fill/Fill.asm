// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/4/Fill.asm

// Runs an infinite loop that listens to the keyboard input. 
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel. When no key is pressed, 
// the screen should be cleared.

//// Replace this comment with your code.
    (LOOP)
    @KBD
    D=M
    @BLACK
    D;JGT
    @WHITE
    0;JMP

    (WHITE)
    @i
    M=0
    (LOOPA)
    @i
    D=M
    @8192
    D=D-A
    @LOOP
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
    @i
    M=0

    (LOOPB)
    @i
    D=M
    @8192
    D=D-A
    @LOOP
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



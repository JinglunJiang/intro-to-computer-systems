//Set the initial value to 0
@2
M=0

//Store the first number in a
@0
D=M
@a
M=D

//Store the second number in b
@1
D=M
@b
M=D

//Loop until a <= 0
(LOOP)
    @a
    D=M
    @END
    D;JLE
    @b
    D=M
    @2
    M=M+D
    @a
    M=M-1
    @LOOP
    0;JMP

(END)
    @END
    0;JMP
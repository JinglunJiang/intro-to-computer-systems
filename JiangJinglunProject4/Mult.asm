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
    //The ending condition set
    @a
    D=M
    @END
    D;JLE

    //Increment value at R2
    @b
    D=M
    @2
    M=M+D

    //Decrement value at a
    @a
    M=M-1

    //Return back to the start of the loop
    @LOOP
    0;JMP

(END)
    //The infinite loop
    @END
    0;JMP
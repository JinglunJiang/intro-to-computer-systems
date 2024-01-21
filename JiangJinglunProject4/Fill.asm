// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen
// by writing 'black' in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen by writing
// 'white' in every pixel;
// the screen should remain fully clear as long as no key is pressed.

// Initialize the current pixel position to the start of the screen
@SCREEN
D=A
@current
M=D

(LOOP)
    // Check keyboard input
    @KBD
    D=M
    @BLACKEN
    D;JGT  // If key is pressed, go to BLACKEN
    @WHITEN
    D;JEQ  // If no key is pressed, go to WHITEN

    // Loop back to the start
    @LOOP
    0;JMP

(BLACKEN)
    // Check if we've reached the end of the screen
    @current
    D=M
    @KBD   //The address of the next address after screen
    D=D-A
    @LOOP
    D;JGE   // If at the end or beyond, go back to the main loop

    // Set the current pixel to black and move to next pixel
    @current
    A=M
    M=-1    // Set to black
    @current
    M=M+1   // Move to next pixel

    // Go back to the main loop
    @LOOP
    0;JMP

(WHITEN)
    // Check if we've reached the start of the screen
    @current
    D=M
    @16385  // Address after the first screen address
    D=D-A
    @LOOP
    D;JLE   // If at the start or below, go back to the main loop

    // Move to the previous pixel and set it to white
    @current
    M=M-1   // Move to previous pixel
    @current
    A=M
    M=0     // Set to white

    // Go back to the main loop
    @LOOP
    0;JMP
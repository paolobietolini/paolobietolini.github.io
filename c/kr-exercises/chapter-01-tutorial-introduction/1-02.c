/*
 * Exercise 1.2 Experiment to find out what happens when printf's argument string contains \c, 
 * where c is some character not listed above.
 */

#include <stdio.h>

int main(void){
    printf("Bell\a\n");
    printf("Backspace\b\n");
    printf("Form Feed \f\n");
    printf("New Line\n");
    printf("Carriage Return\r\n");
    printf("Horizontal Tab\t\n");
    printf("Vertical Tab\v\n");
    printf("Backslash \\ \n");
    printf("Single Quote \' \n");
    printf("Double Quote \" \n");
    printf("Hexadecimal character code 41 is \x41\n");
    printf("Octal character code 101 is \101\n");
    return 0;
}
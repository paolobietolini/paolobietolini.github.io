/*
 * Write a program to check a C program for rudimentary syntax errors 
 * like unbalanced parentheses, brackets and braces. Don't forget about 
 * quotes, both single and double, escape sequences, and comments. 
 * (This program is hard if you do it in full generality).
 */

#include <stdio.h>


int match(char open, char closed) {
    return 
        (open == '{' && closed == '}') ||
        (open == '[' && closed == ']') ||
        (open == '(' && closed == ')');
}
int check_parentesis(char c, stack[]) {
    char open =  pop();
    char close = c;

    if(!match(open, close)) {
        fprintf(stderr, "Match not found at row %d", row);
        return -1;
    }

    return 0;
}
/* check parentesis (int max stack) 
 * Si utilzza uno stack ma non capisco ancora perche
 *
 *
 * void pop()
 * void push()
 *
 *
 *
 *
 *      
 *
 * */
int main(void) {
    row = 1;
    int c;
    while ((c = getchar()) != EOF) {
        if (c =='\n')
            row++;
    }
    return 0;
}

/*
 * Write a program to print all input lines that are longer than 80 characters.
 */

#include <stdio.h>

#define MAXLENGTH 80 
#define MAXLINE 1000

int get_line(char line[], int limit);

int main(void) {
    char line[MAXLINE];
    int max, len;
    max = len = 0;
    while((len = get_line(line, MAXLINE)) > 0) {
        if (len > MAXLENGTH)
            printf("%s",line);
    }
    return 0;
}


int get_line(char line[], int limit) {
    /* Returns the length of the current line */
    int c, i;
    for (i = 0; i < limit - 1 && (c = getchar()) != EOF && c != '\n'; i++) 
        line [i] = c;

    if (c == '\n') {
        line[i] = c;
        i++;
    }

    line[i] = '\0';
    return i;
}

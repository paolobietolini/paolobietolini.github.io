/*
* Write a program to count blanks,
* tabs, and newlines
*/

#include <stdio.h>

int main(void) {
    int c, tb = 0, bl = 0, nl = 0;

    while ((c = getchar()) != EOF) {
        if (c == '\n')
            nl++;
        if (c == '\t')
            tb++;
        if (c == ' ')
            bl++;
    }

    printf("Your input has: %d new lines, %d tabs, %d blanks\n", nl, tb, bl);
    return 0;
}

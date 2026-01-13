/*
 * Write a program to print a histogram of the lengths of words in its input.
 * It is easy to draw the histogram with the bars horizontal;
 * a vertical orientation is more challenging
 */

#include <stdio.h>

#define MAXLEN 20 

int main(void) {
    int c, w = 0;
    int ndigit[MAXLEN] = {0};

    while ((c = getchar()) != EOF) {
        if ((c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z')) {
            w++;
        } else {
            if (w > 0 && w <= MAXLEN)
                ndigit[w - 1]++;
            w = 0;
        }
    }
    if (w > 0 && w <= MAXLEN)
        ndigit[w - 1]++;

    int max = 0;
    for (int i = 0; i < MAXLEN; i++)
        if (ndigit[i] > max)
            max = ndigit[i];

    for (int row = max; row > 0; row--) {
        for (int col = 0; col < MAXLEN; col++) {
            if (ndigit[col] >= row)
                printf("  * ");
            else
                printf("    ");
        }
        printf("\n");
    }

    for (int i = 0; i < MAXLEN; i++)
        printf("----");
    printf("\n");

    for (int i = 0; i < MAXLEN; i++)
        printf("%3d ", i + 1);
    printf("\n");

    return 0;
}
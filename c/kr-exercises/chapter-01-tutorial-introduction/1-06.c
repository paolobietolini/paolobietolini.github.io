/*
 * Verify that the expression getchar() != EOF is 0 or 1.
 */
#include <stdio.h>

int main(void)
{
    int c;

    while (c = getchar() != EOF)
        printf("value = %d\n", c);

    printf("after EOF, value = %d\n", c);
    return 0;
}


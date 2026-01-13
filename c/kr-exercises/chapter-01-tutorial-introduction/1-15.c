/*
 * Rewrite the temperature conversion program of Section 1.2 to use a function 
 * for conversion.
 */

#include <stdio.h>

#define ERROR_VALUE -9999.0f

float temp_convert(float value, char type) {
    if (type == 'F')
        return (5.0f / 9.0f) * (value - 32);
    else if (type == 'C')
        return (9.0f / 5.0f) * value + 32;
    else
        return ERROR_VALUE;
}

int main(void) {
    float fahr, celsius;
    int lower = 0, upper = 300, step = 10;

    printf("+-------+---------+\n");
    printf("|   F   |    C    |\n");
    printf("+-------+---------+\n");

    for (fahr = lower; fahr <= upper; fahr += step) {
        celsius = temp_convert(fahr, 'F');

        if (celsius == ERROR_VALUE) {
            fprintf(stderr, "Error: Wrong conversion type\n");
            return 1;
        }

        printf("| %5.1f | %7.2f |\n", fahr, celsius);
    }

    printf("+-------+---------+\n");

    return 0;
}

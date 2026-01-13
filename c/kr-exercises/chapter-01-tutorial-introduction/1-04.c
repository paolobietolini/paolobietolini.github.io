/*
 * Write a program to print the corresponding Celsius to Fahrenheit table.
 */
#include <stdio.h>

int main(void){
				float fahr, celsius;
				int step, lower, upper;

				lower = 0;
				step = 20;
				upper = 300;

				celsius  = lower;
				printf("%6s %6s\n","C", "F");
				while(celsius <= upper) {
								fahr = (9.0/5.0 * celsius) + 32.0;
								printf("%6.1f %6.0f\n",celsius, fahr);
								celsius += step;
				}

				return 0;
}

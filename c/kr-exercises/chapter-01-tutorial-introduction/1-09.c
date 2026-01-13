/*
 * Write a program to copy its input to
 * its output, replacing each string of one
 * or more blanks by a single blank.
 */


#include <stdio.h>

int main(void) {
				int was_space = 0;
				int c;

				while ((c = getchar()) != EOF) {
								if (c == ' '|| c == '\t') {
												if (!was_space) {
																putchar(c);
																was_space = 1;
												}
								} else {
												putchar(c);
												was_space = 0;
								}
				}
				return 0;
}

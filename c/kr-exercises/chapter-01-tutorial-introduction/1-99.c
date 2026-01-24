/*
 * Exercise 1-99.** Write a program that compresses its input by replacing
 * sequences of repeated characters with the character followed by its count.
 * For example, the input `aaabbccccdd` should produce `a3b2c4d2`. A character
 * that appears only once should still be followed by `1`.
 */

#include <stdio.h>
int main(void) {
  int c, prev_c = 0, counter = 0;
  while ((c = getchar()) != EOF) {
    if (counter > 0 && (prev_c != c || c == '\n')) {
      printf("%c%d", prev_c, counter);
      counter = 0;
    }
    if (c == '\n') {
      putchar('\n');
      counter = 0;
    } else {
      counter++;
      prev_c = c;
    }
  }
  putchar('\n');
  if (counter > 0)
    printf("%c%d\n", prev_c, counter);

  return 0;
}

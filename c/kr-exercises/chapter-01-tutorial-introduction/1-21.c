/*
 * Write a program entab that replaces strings of blanks by the minimum number
 * of tabs and blanks to achieve the same spacing. Use the same tab stops, say
 * every n columns. Should n be a variable or a symbolic parameter?
 */

#include <stdio.h>
#define TAB 8

int main(void) {

  int col = 0, spaces = 0, c;

  while ((c = getchar()) != EOF) {
    if (c == ' ') {
      spaces++;
      col++;
      if (col % TAB == 0) {
        putchar('\t');
        spaces = 0;
      }
    } else {
      while (spaces > 0) {
        putchar(' ');
        spaces--;
      }
      putchar(c);
      if (c == '\n')
        col = 0;
      else if (c == '\t')
        col += (TAB - col % TAB);
      else
        col++;
    }
  }
  return 0;
}
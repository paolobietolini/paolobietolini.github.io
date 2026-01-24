/*
 * Write a program to "fold" long input lines into two or more shorter lines
 * after the last > non-blank character that occurs before the n-th column of
 * input. Make sure your program does something intelligent with very long line,
 * and if there are > no blanks or tabs before the specified column.
 */
#include <stdio.h>

#define MAXCOL 10
void print_buffer(char buffer[], int limit) {
  for (int i = 0; i < limit; i++)
    putchar(buffer[i]);
}

int swap_buffer(char buffer[], int start) {
  // Returns the new length of the buffer
  int b = 0;
  for (int i = start; i < MAXCOL; i++) {
    buffer[b] = buffer[i];
    b++;
  }

  return b;
}
int main(void) {
  int c, col = 0, blanks = -1;
  char buffer[MAXCOL];

  while ((c = getchar()) != EOF) {
    if (c == '\n') {
      print_buffer(buffer, col);
      putchar('\n');
      col = 0;
      blanks = -1;
    } else {
      buffer[col] = c;
      if (c == '\t' || c == ' ')
        blanks = col;
      col++;

      if (col == MAXCOL) {
        if (blanks > -1) {
          print_buffer(buffer, blanks);
          putchar('\n');
          int new_col = swap_buffer(buffer, blanks + 1);
          col = new_col;
          blanks = -1;
          for (int i = 0; i < col; i++) {
            if (buffer[i] == ' ' || buffer[i] == '\t') {
              blanks = i;
            }
          }
        } else {
          print_buffer(buffer, MAXCOL);
          putchar('\n');
          col = 0;
          blanks = -1;
        }
      }
    }
  }
  if (col > 0) {
    print_buffer(buffer, col);
    putchar('\n');
  }
  return 0;
}
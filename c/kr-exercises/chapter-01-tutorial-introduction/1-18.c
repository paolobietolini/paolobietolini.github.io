/*
 * Write a program to remove trailing blanks and tabs from each line of input,
 * and to delete entirely blank lines.
 */

#include <stdio.h>
#define MAXLINE 1000
int trim(char line[], int limit);
int main(void) {
  char line[MAXLINE];
  int len;
  while ((len = trim(line, MAXLINE)) >= 0) {
    if (len > 0)
      printf("%s\n", line);
  };

  return 0;
}

int trim(char line[], int limit) {
  int c, end, i = 0;

  while (i < limit - 1 && (c = getchar()) != EOF && c != '\n') {
    line[i] = c;
    i++;
  }

  if (c == EOF && i == 0)
    return -1;

  end = i - 1;
  while (end >= 0 && (line[end] == ' ' || line[end] == '\t'))
    end--;

  line[end + 1] = '\0';
  return end + 1;
}
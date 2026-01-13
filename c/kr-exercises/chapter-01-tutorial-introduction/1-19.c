/*
 * Write a function reverse(s) that reverses the character string s.
 * Use it to write a program that reverses its input a line at a time.
 */

#include <stdio.h>
#define MAXSTRING 100

void reverse(char s[], int len);
int get_line(char s[], int max);

int main(void) {
  char line[MAXSTRING];
  int len;
  while ((len = get_line(line, MAXSTRING)) > 0) {
    reverse(line, len);
    printf("Reversed: %s\n", line);
  }
  return 0;
}

int get_line(char s[], int max) {
  int c, i;
  for (i = 0; i < max - 1 && (c = getchar()) != EOF && c != '\n'; i++)
    s[i] = c;
  s[i] = '\0';
  return (c == EOF && i == 0) ? 0 : i;
}

void reverse(char s[], int len) {
  int left = 0;
  int right = len - 1;

  while (left < right) {
    char t = s[left];
    s[left] = s[right];
    s[right] = t;
    left++;
    right--;
  }
}
#include <stdio.h>

#define NCHARS 128
#define SCALE 0          /* 0 = absolute, 1 = scaled */
#define MAXHIST 15       /* max width of histogram */

int freq[NCHARS] = {0};

int main(void) {
  int c, i, j, len, maxvalue = 0;

  while ((c = getchar()) != EOF) {
    if (c >= 0 && c < NCHARS)
      freq[c]++;
  }

  for (i = 0; i < NCHARS; i++)
    if (freq[i] > maxvalue)
      maxvalue = freq[i];

  for (i = 0; i < NCHARS; i++) {
    if (freq[i] > 0) {

#if SCALE
      len = freq[i] * MAXHIST / maxvalue;
      if (len <= 0)
        len = 1;
#else
      len = freq[i];
#endif

      if (i == ' ')
        printf("SPACE ");
      else if (i == '\t')
        printf("TAB   ");
      else if (i == '\n')
        printf("NL    ");
      else
        printf("%c     ", i);

      for (j = 0; j < len; j++)
        putchar('*');

      putchar('\n');
    }
  }

  return 0;
}

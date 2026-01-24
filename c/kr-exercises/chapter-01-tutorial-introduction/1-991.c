/*Exercise 1-991.** Write a program that expands escape sequences in its input.
 * The sequence `\n` should be replaced with an actual newline, `\t` with a tab,
 * and `\\` with a single backslash. Any other character following a backslash
 * should be printed as-is (e.g., `\x` becomes `x`). For example, the input
 * `Hello\nWorld` should print:
 * Hello
 * World
 */

#include <stdio.h>

int main(void) {
  int c, escaped = 0, i = 0;
  char lookup[] = {'t', 'n', 'b', 'v', '\\'};
  char escapes[] = {'\t', '\n', '\b', '\v', '\\'};
  int escapes_len = sizeof(escapes) / sizeof(char);
  while ((c = getchar()) != EOF) {
    if (c == '\\' && escaped == 0)
      escaped = 1;
    else {
      if (escaped == 1) {
        for (i = 0; i < escapes_len; i++) {
          if (lookup[i] == c) {
            printf("%c", escapes[i]);
            break;
          }
        }
        if (i == escapes_len)
          putchar(c);
        escaped = 0;
      } else {
        putchar(c);
      }
    }
  }
  if (escaped) {
    putchar('\\');
  }
}

/*
A switch-case it is more efficient than two arrays.

#include <stdio.h>

int main(void) {
    int c;
    int escaped = 0; // State flag: 0 = normal, 1 = just saw a backslash

    while ((c = getchar()) != EOF) {
        if (escaped) {
            // We previously saw a backslash, so we interpret 'c'
            switch (c) {
                case 'n':
                    putchar('\n');
                    break;
                case 't':
                    putchar('\t');
                    break;
                case '\\':
                    putchar('\\');
                    break;
                case 'b':
                    putchar('\b');
                    break;
                // Add other cases here as needed
                default:
                    // Requirement: "Any other character... printed as-is"
                    // e.g., "\x" becomes "x"
                    putchar(c);
                    break;
            }
            escaped = 0; // Reset state
        }
        else {
            if (c == '\\') {
                escaped = 1; // Enter escape sequence mode
            } else {
                putchar(c);  // Print normal characters immediately
            }
        }
    }

    // Edge case: Input ended with a hanging backslash (e.g., "text\")
    if (escaped) {
        putchar('\\');
    }

    return 0;
}


*/
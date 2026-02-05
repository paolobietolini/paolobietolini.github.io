#include <stdio.h>
#include <stdint.h>

/* Decode one UTF-8 codepoint */
int utf8_decode(FILE *in, uint32_t *codepoint) {
    int c = fgetc(in);
    if (c == EOF) return 0;

    if ((c & 0x80) == 0) {
        *codepoint = c;
        return 1;
    }

    int bytes;
    if ((c & 0xE0) == 0xC0) bytes = 2;
    else if ((c & 0xF0) == 0xE0) bytes = 3;
    else if ((c & 0xF8) == 0xF0) bytes = 4;
    else return 0;

    *codepoint = c & ((1 << (8 - bytes - 1)) - 1);

    for (int i = 1; i < bytes; i++) {
        c = fgetc(in);
        if ((c & 0xC0) != 0x80) return 0;
        *codepoint = (*codepoint << 6) | (c & 0x3F);
    }

    return bytes;
}

/* Check if codepoint is an emoji */
int is_emoji(uint32_t cp) {
    return
        (cp >= 0x1F300 && cp <= 0x1F5FF) ||  // symbols & pictographs
        (cp >= 0x1F600 && cp <= 0x1F64F) ||  // emoticons
        (cp >= 0x1F680 && cp <= 0x1F6FF) ||  // transport & map
        (cp >= 0x1F700 && cp <= 0x1F77F) ||
        (cp >= 0x1F780 && cp <= 0x1F7FF) ||
        (cp >= 0x1F800 && cp <= 0x1F8FF) ||
        (cp >= 0x1F900 && cp <= 0x1F9FF) ||
        (cp >= 0x1FA00 && cp <= 0x1FAFF) ||
        (cp >= 0x2600  && cp <= 0x26FF)  ||  // misc symbols
        (cp >= 0x2700  && cp <= 0x27BF);     // dingbats
}

/* Write UTF-8 codepoint */
void utf8_write(FILE *out, uint32_t cp) {
    if (cp <= 0x7F) {
        fputc(cp, out);
    } else if (cp <= 0x7FF) {
        fputc(0xC0 | (cp >> 6), out);
        fputc(0x80 | (cp & 0x3F), out);
    } else if (cp <= 0xFFFF) {
        fputc(0xE0 | (cp >> 12), out);
        fputc(0x80 | ((cp >> 6) & 0x3F), out);
        fputc(0x80 | (cp & 0x3F), out);
    } else {
        fputc(0xF0 | (cp >> 18), out);
        fputc(0x80 | ((cp >> 12) & 0x3F), out);
        fputc(0x80 | ((cp >> 6) & 0x3F), out);
        fputc(0x80 | (cp & 0x3F), out);
    }
}

int main(int argc, char *argv[]) {
    if (argc != 3) {
        fprintf(stderr, "Usage: %s input.md output.md\n", argv[0]);
        return 1;
    }

    FILE *in = fopen(argv[1], "rb");
    FILE *out = fopen(argv[2], "wb");

    if (!in || !out) {
        perror("File error");
        return 1;
    }

    uint32_t cp;
    while (utf8_decode(in, &cp)) {
        if (!is_emoji(cp)) {
            utf8_write(out, cp);
        }
    }

    fclose(in);
    fclose(out);
    return 0;
}


/* Exercise 1-24.
 * Write a program to check a C program for rudimentary syntax errors
 * like unbalanced parentheses, brackets and braces. Don't forget about
 * quotes, both single and double, escape sequences, and comments.
 * (This program is hard if you do it in full generality).
 */

#include <stdio.h>
#include <stdlib.h>
typedef struct Stack {
    char p;
    struct Stack* next;
} stack;

typedef enum {
    NORMAL,
    SLASH,
    BLOCKCOMM,
    STAR,
    LINECOMM,
    STRING,
    STRING_ESCAPE,
    CHAR,
    CHAR_ESCAPE
} States;
static int line_number = 1;
static int column_number = 1;
char peek(stack* head);
stack* newNode(char p);
void push(stack** head, char p);
char pop(stack** head, char* result);
char check_brackets(stack** main_stack, char c);
int matching(char open, char close);

int main(void) {
    int c;
    stack* main_stack = NULL;
    States state = NORMAL;
    while ((c = getchar()) != EOF) {
        if (c == '\n') {
            line_number++;
            column_number = 1;
        }
        else {
            column_number++;
        }

        switch (state) {
        case NORMAL:
            if (c == '/')
                state = SLASH;
            else if (c == '"') {
                putchar(c);
                state = STRING;
            }
            else if (c == '\'') {
                putchar(c);
                state = CHAR;
            }
            else {
                check_brackets(&main_stack, c);
                putchar(c);
            }
            break;

        case SLASH:
            if (c == '*')
                state = BLOCKCOMM;
            else if (c == '/')
                state = LINECOMM;
            else {
                putchar('/');
                check_brackets(&main_stack, c);
                putchar(c);
                state = NORMAL;
            }
            break;

        case BLOCKCOMM:
            if (c == '*')
                state = STAR;

            break;

        case LINECOMM:
            if (c == '\n') {
                putchar('\n');
                state = NORMAL;
            }
            break;

        case STAR:
            if (c == '/')
                state = NORMAL;
            else if (c != '*')
                state = BLOCKCOMM;
            break;

        case STRING:
            putchar(c);
            if (c == '\\')
                state = STRING_ESCAPE;
            else if (c == '"')
                state = NORMAL;

            break;

        case STRING_ESCAPE:
            putchar(c);
            state = STRING;
            break;

        case CHAR:
            putchar(c);
            if (c == '\\') {
                state = CHAR_ESCAPE;
            }
            else if (c == '\'')
                state = NORMAL;
            break;

        case CHAR_ESCAPE:
            putchar(c);
            state = CHAR;
            break;
        }
    }
    if (peek(main_stack) != -1) {
        printf("Line %d: Missing closing brackets\n", line_number);
        return 1;
    }
    return 0;
}

char peek(stack* head) {
    if (head == NULL)
        return -1;

    return head->p;
}

stack* newNode(char p) {
    stack* new = malloc(sizeof(stack));
    if (NULL == new)
        return NULL;
    new->next = NULL;
    new->p = p;

    return new;
}
void push(stack** head, char p) {
    stack* new = newNode(p);
    new->next = *head;
    *head = new;
    return;
}
char pop(stack** head, char* result) {
    if (*head == NULL)
        return -1;
    stack* popped = *head;
    *result = popped->p;
    *head = (*head)->next;
    free(popped);
    return 0;
}


char check_brackets(stack** main_stack, char c) {
    if (c == '(' || c == '{' || c == '[') {
        push(main_stack, c);
    }
    else if (c == ')' || c == '}' || c == ']') {
        char top;
        char ret = pop(main_stack, &top);
        if (ret != 0) {
            printf("Line %d, Col %d: Unbalanced brackets: extra closing '%c'\n",
                line_number, column_number, c);
            return 1;
        }
        if (!matching(top, c)) {
            printf("Line %d, Col %d: Mismatched brackets: '%c' closed by '%c'\n",
                line_number, column_number, top, c);
            return 1;
        }
    }
    return 0;
}

int matching(char open, char close) {
    return (open == '(' && close == ')') ||
        (open == '{' && close == '}') ||
        (open == '[' && close == ']');
}
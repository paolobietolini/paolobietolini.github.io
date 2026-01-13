/*
 * Revise the main routine of the longest-line program so it will correctly print 
 * the length of arbitrarily long input lines, and as much as possible of the text.
 */

#include <stdio.h>
#define MAXLINE 1000

int get_line(char line[], int maxline);

void copy(char destination[], char source[]);

int main(void){
    int len, max = 0;
    char line[MAXLINE], longest[MAXLINE];

    while((len = get_line(line, MAXLINE)) > 0)
        if (len > max) {
            max = len;
            copy(longest, line);
        }
    if (max > 0){
        printf("Text (truncated at %d): %s\n", MAXLINE, longest);
        printf("Actual total length: %d\n", max);
    }  
 
    return 0;
}

int get_line(char line[], int limit){
    int c;
    int i = 0;       
    int real_len = 0;
    
    while((c = getchar()) != EOF && c != '\n'){
        if(i < limit - 1)
            line[i++] = c;
        real_len++;
    }
    
    if(c == '\n'){
        if(i < limit - 1)  
            line[i++] = c;
        real_len++;
    }
    
    line[i] = '\0';  
    return real_len;
}
void copy(char destination[], char source[]){
     int i = 0;

    while((destination[i] = source[i]) != '\0')
        i++;
}

/*
 * How would you test the word count program ? 
 * What kind of input are most likey to uncover bugs if there are any ?
 */

#include <stdio.h>

#define IN 1
#define OUT 0
int main(void) {

				int c, nl, nw, nc, state;

				state = OUT;
				nl = nw = nc = 0;

				while((c = getchar()) != EOF){
								++nc;
								if(c == '\n')
												++nl;
								if(c == ' ' || c == '\n' || c == '\t')
												state = OUT;
								else if(state == OUT){
												state = IN;
												++nw;
								}
				}
				printf("Lines\tWords\tCharacters\n");
				printf("%3d\t%3d\t%6d\n",nl, nw, nc);
				return 0;
}




/*
 * No input
 * Lines   Words   Characters
 *  0       0          0
 *
 *  Empty input (new line)
 *  Lines   Words   Characters
 *   1       0         1
 *  
 *  Sentence + New line
 *  All your base are belong to us
 *  Lines   Words   Characters
 *    1       7         31

 */

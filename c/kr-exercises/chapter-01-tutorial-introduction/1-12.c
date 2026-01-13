/*
 * Write a program that prints its input one word per line.
 */

# include <stdio.h>

int main(void){
		int c, newline;
		newline = 0;
		while((c = getchar()) != EOF){
			// se e` spazio, tab , nuova linea e` new word. andiamo a capo altirmenti stampiamo c
		if(c == ' ' || c == '\t' || c == '\n')
						newline = 1;
		if((newline == 1) && (c != ' ') && (c != '\t')){
						printf("\n%c",c);
						newline = 0;
		}
		else
						printf("%c",c);
		}
return 0;
}

#include <stdio.h>
void swap(int *a, int *b)
{
    int temp = *a;
    *a = *b;
    *b = temp;
}
int main(void)
{
    /* ESERCIZI SUI PUNTATORI
     *
     * Esercizio 1:
     * Dichiara due variabili intere a = 10 e b = 20.
     * Crea un puntatore p che punti ad a.
     * Stampa il valore di a usando il puntatore p.
     * Poi fai puntare p a b e stampa il valore di b usando p.
     */
    printf("%s", "=============================\nEsercizio 1\n=============================\n");
    int a, b, *p;
    a = 10, b = 20;
    p = &a;
    printf("Valore di a, puntato da p: %d\n", *p);
    p = &b;
    printf("Valore di b, puntato da p: %d\n", *p);

    /* Esercizio 2:
     * Dichiara una variabile x = 100.
     * Crea un puntatore px che punti a x.
     * Usa il puntatore px per modificare il valore di x a 200.
     * Stampa x per verificare che sia cambiato.
     */
    printf("%s", "=============================\nEsercizio 2\n=============================\n");
    int x = 100;
    int *px = &x;
    *px = 200;
    printf("Valore di x dopo la riassegnazione: %d\n", *px);

    /* Esercizio 3:
     * Dichiara tre variabili: int val = 42, int *ptr, int **pptr.
     * Fai in modo che ptr punti a val.
     * Fai in modo che pptr punti a ptr (puntatore a puntatore).
     * Stampa il valore di val in tre modi diversi:
     * - usando val direttamente
     * - usando *ptr
     * - usando **pptr
     */

    // Il tuo codice qui
    printf("%s", "=============================\nEsercizio 3\n=============================\n");
    int val = 42;
    int *ptr, **pptr;
    ptr = &val;
    pptr = &ptr;
    printf("I valori di val:\n%d\n%d\n%d\n", val, *ptr, **pptr);

    /* Esercizio 4:
     * Scrivi una funzione swap(int *a, int *b) che scambia i valori
     * di due variabili usando i puntatori.
     * Nel main, dichiara x = 5 e y = 15, chiamala e verifica
     * che i valori siano stati scambiati.
     */
    printf("%s", "=============================\nEsercizio 4\n=============================\n");

    int xx = 5;
    int yy = 15;
    void swap(int *a, int *b);
    printf("Valori prima dello swap: %d, %d\n", xx, yy);
    swap(&xx, &yy);
    printf("Valori dopo lo swap: %d, %d\n", xx, yy);

    /* Esercizio 5 (più difficile):
     * Crea un array di 5 interi: arr[] = {10, 20, 30, 40, 50}.
     * Crea un puntatore p che punti al primo elemento dell'array.
     * Usando l'aritmetica dei puntatori (p++, *(p+1), ecc.),
     * stampa tutti gli elementi dell'array.
     */

    printf("%s", "=============================\nEsercizio 5\n=============================\n");

    int arr[] = {10, 20, 30, 40, 50};
    int *primo = arr;
    int len = sizeof(arr) / sizeof(int);
    for (int i = 0; i < len; i++)
    {
        printf("%d\n", *(primo++)); //accede al valore di primo e lo aumenta di 1
    }
    return 0;
}

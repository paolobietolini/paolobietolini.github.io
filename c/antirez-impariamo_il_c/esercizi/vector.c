#include <stdio.h>
#include <stdlib.h>
#define INITIAL_CAPACITY 8
typedef struct Vector {
  int *data;
  int size;     // Number of elements
  int capacity; // Available allocated memory
} Vector;
Vector *
vector_create(int initial_capacity); // Alloca la struttura e l'array iniziale.
                                     // Restituisce il puntatore al vettore.
void vector_push_back(Vector *v, int value); // Aggiunge un elemento in coda.

// Nota: Se size raggiunge capacity, devi ridimensionare l'array (usa realloc,
// tipicamente raddoppiando la capacità).
int vector_get(Vector *v,
               int index);   //: Restituisce l'elemento all'indice specificato
                             //: (gestisci l'errore se l'indice è fuori limiti,
                             //: magari restituendo -1 o stampando su stderr).
void vector_free(Vector *v); //: Libera correttamente tutta la memoria allocata.

int main(void) {
  printf("AHO World\n");
  printf("%p", vector_create(INITIAL_CAPACITY));
  return 0;
}

Vector *vector_create(int initial_capacity) {
  Vector *v = (Vector *)malloc(sizeof(Vector));

  if (v == NULL) {
    fprintf(stderr, "Issue while allocating memory for vector structure\n");
    return NULL;
  }
  v->data = (int *)malloc(initial_capacity * sizeof(int));
  if (v->data == NULL) {
    fprintf(stderr, "Issue while allocating memory for vector data\n");
    free(v);
    return NULL;
  }
  v->size = 0;
  v->capacity = initial_capacity;
  return v;
}
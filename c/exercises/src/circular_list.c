// Una lista circolare singola
// ha il primo e ultimo nodo collegati,
// come?quando creo il primo nodo lo colego a se stesso
//  A-> A

//  quando creo il secondo nodo
//  il next del nuovo e la vecchia testa
//  il next della vecchia testa e` nuovo
//  nuovo diventa testa

// A -> B -> C -> D -> E -> A

#include <stdio.h>
#include <string.h>
#include <stdlib.h>

typedef struct Book {
  char title[50];
  struct Book* next;
} book;

book* create_book(char* title) {
  book* new_book = malloc(sizeof(book));
  if (NULL == new_book) {
    fprintf(stderr, "Error while allocating memory.\n");
    return NULL;
  }

  strncpy(new_book->title, title, sizeof(new_book->title));
  new_book->title[sizeof(new_book->title) - 1] = '\0';
  new_book->next = NULL;

  return new_book;
}
void add(book** tail, char* title) {
  book* new_book = create_book(title);
  if (!new_book)
    return;

  if (*tail == NULL) {
    new_book->next = new_book;
    *tail = new_book;
    return;
  }
  new_book->next = (*tail)->next;  // 1984 -> DUNE
  (*tail)->next = new_book;         // (1984->) Dune -> 1984
  *tail = new_book;
}


book* find(book* tail, char* key) {
  if (NULL == tail)
    return NULL;

  book* current = tail->next;
  do {
    if (strcmp(current->title, key) == 0) {
      return current;
    }
    current = current->next;
  } while (current != tail->next);

  printf("Not found: %s\n", key);
  return NULL;
}

void delete(book** tail, char* key) {
  if (*tail == NULL)
    return;

  // caso: un solo nodo
  if ((*tail)->next == *tail) {
    if (strcmp((*tail)->title, key) == 0) {
      free(*tail);
      *tail = NULL;
    }
    return;
  }

  book* prev = *tail;
  book* current = (*tail)->next;
  do {
    if (strcmp(current->title, key) == 0) {
      prev->next = current->next;
      if (current == *tail)  // cancello la coda
        *tail = prev;
      free(current);
      return;
    }
    prev = current;
    current = current->next;
  } while (current != (*tail)->next);
}

void print(book* tail) {
  book* current = tail->next;
  if (NULL == current)
    return;

  do {
    printf("%s\n", current->title);
    current = current->next;
  } while (current != tail->next);
}

int main(void) {
  book* library = NULL;

  add(&library, "Dune");
  add(&library, "1984");
  add(&library, "LOTR");
  add(&library, "Fight Club");
  find(library, "1984");
  delete(&library, "Fight Club");
  print(library);
}

// Dune > 1984 > LOTR > FC > Dune
#include <stdio.h>
#include <string.h>

#define LIBRI 3
struct Libro
{
  char titolo[100];
  char autore[50];
  int anno;
  float prezzo;
};

void applicaSconto(struct Libro *l, float percentuale)
{
    l->prezzo = l->prezzo * (1 - percentuale / 100.0);
}

void stampaLibro(struct Libro *l)
{
  printf("Titolo: %s\n", l->titolo);
  printf("Autore: %s\n", l->autore);
  printf("Anno: %d\n", l->anno);
  printf("Prezzo: %.2f\n", l->prezzo);
  printf("\n");
}
int main(void)
{
  struct Libro libri[LIBRI];
  libri[0] = (struct Libro){"Il Signore degli Anelli", "J.R.R. Tolkien", 1954, 25.99};
  libri[1] = (struct Libro){"1984", "George Orwell", 1949, 12.50};
  libri[2] = (struct Libro){"Il Codice Da Vinci", "Dan Brown", 2003, 18.90};

  for (int i = 0; i < LIBRI; i++)
  {
    stampaLibro(&libri[i]);
    if (strcmp(libri[i].titolo, "1984") == 0)
      applicaSconto(&libri[i], 10);
  }

  printf("----------\n");
  for (int i = 0; i < LIBRI; i++)
  {
    stampaLibro(&libri[i]);
  }

  return 0;
}

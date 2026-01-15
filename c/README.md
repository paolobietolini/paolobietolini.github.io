# Learning C

This repository contains my notes, exercises, and code while learning C programming.
---

## Antirez Course - Impariamo il C

Course by Salvatore Sanfilippo (antirez).

### Fondamenti
- [Lezione 1: Introduzione](antirez/lezione01-introduzione)
- [Lezione 2: Variabili e operatori](antirez/lezione02-variabili-operatori)
  - [Appendice: La vita delle variabili locali](antirez/lezione02-appendice-variabili-locali)
- [Lezione 3: Variabili Globali](antirez/lezione03-variabili-globali)
- [Lezione 4: Tipi](antirez/lezione04-tipi)
- [Lezione 5: Stringhe](antirez/lezione05-stringhe)

### Controllo di Flusso e Ricorsione
- [Lezione 6: IF, GOTO e ricorsione](antirez/lezione06-if-goto-ricorsione)
- [Lezione 7: Ancora sulla ricorsione, while/for, switch](antirez/lezione07-ricorsione-while-for-switch)
- [Lezione 8: Implementiamo il Conway's Game of Life](antirez/lezione08-game-of-life/)

### Puntatori
- [Lezione 9: Introduzione ai puntatori](antirez/lezione09-introduzione-puntatori/)
- [Lezione 10: La matematica dei puntatori](antirez/lezione10-matematica-puntatori/)
- [Lezione 11: Chiarimenti sui puntatori](antirez/lezione11-chiarimenti-puntatori/)
- [Lezione 12: Un primo incontro con malloc()](antirez/lezione12-malloc/)
- [Lezione 13: Il trucco dei metadati nascosti](antirez/lezione13-metadati-nascosti/)

### Strutture Dati
- [Lezione 14: Le strutture del C](antirez/lezione14-strutture/)
- [Lezione 15: Le struct come mattone delle strutture dati](antirez/lezione15-struct-strutture-dati/)
- [Lezione 16: Stringhe con reference counting](antirez/lezione16-struct-stringhe-refcount/)
- [Lezione 17: Design delle stringhe, hexdump()](antirez/lezione17-stringhe-design-hexdump/)
- [Approfondimento: Reference counting](antirez/lezione-approfondimento-refcount/)

### Concetti Avanzati
- [Lezione 18: Tipi opachi, typedef, file stdlib](antirez/lezione18-tipi-opachi-typedef-file/)
- [Lezione 19: Le chiamate di sistema](antirez/lezione19-chiamate-sistema/)
- [Lezione 20: Buffering della libc e file mappati in memoria](antirez/lezione20-buffering-mmap/)
- [Lezione 21: Union e bitfield](antirez/lezione21-union-bitfield/)
- [Lezione 22: I puntatori a funzione](antirez/lezione22-puntatori-funzione/)
- [Lezione 28: Funzioni con numero variabile di argomenti](antirez/lezione28-argomenti-variabili/)

### Progetto: Toy Forth
- [Lezione 23: Interprete Toy Forth (parte 1)](antirez/lezione23-toy-forth-parte1/)
- [Lezione 24: Interprete Toy Forth (parte 2)](antirez/lezione24-toy-forth-parte2/)
- [Lezione 25: Interprete Toy Forth (parte 3)](antirez/lezione25-toy-forth-parte3/)
- [Lezione 26: Toy Forth - exec() (parte 4)](antirez/lezione26-toy-forth-exec-parte4/)
- [Lezione 27: Toy Forth - registrazione funzioni (parte 5)](antirez/lezione27-toy-forth-registrazione-parte5/)
- [Lezione 29: Toy Forth - primo programma](antirez/lezione29-toy-forth-primo-programma/)

### Puntate Speciali
- [Come riesumare gli algoritmi dalla memoria](antirez/lezione-speciale-algoritmi-memoria/)
- [Random variables](antirez/lezione-speciale-random-variables/)

---

## K&R Exercises

Exercises from "The C Programming Language" by Kernighan and Ritchie.

- [Chapter 1: A Tutorial Introduction](kr-exercises/chapter-01-tutorial-introduction/)
- [Chapter 2: Types, Operators and Expressions](kr-exercises/chapter-02-types-operators-expressions/)
- [Chapter 3: Control Flow](kr-exercises/chapter-03-control-flow/)
- [Chapter 4: Functions and Program Structure](kr-exercises/chapter-04-functions-program-structure/)
- [Chapter 5: Pointers and Arrays](kr-exercises/chapter-05-pointers-arrays/)
- [Chapter 6: Structures](kr-exercises/chapter-06-structures/)
- [Chapter 7: Input and Output](kr-exercises/chapter-07-input-output/)
- [Chapter 8: The UNIX System Interface](kr-exercises/chapter-08-unix-system-interface/)

---

## Compilation

```bash
gcc -o program program.c
./program
```

With warnings enabled (recommended):
```bash
gcc -Wall -Wextra -o program program.c
```

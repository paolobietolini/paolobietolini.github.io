Ecco una versione **riorganizzata, corretta e arricchita** dei tuoi appunti sui puntatori in C, con particolare attenzione alla parte sulle stringhe e agli esempi pratici. Ho strutturato tutto in modo da essere chiaro, progressivo e pronto per lo studio o la consultazione rapida.

---

# **Puntatori in C: Guida Completa**

## **1. Cos’è un puntatore?**
Un **puntatore** è una variabile che **non contiene un valore**, ma **l’indirizzo di memoria di un’altra variabile**.
- Ogni variabile occupa una zona di memoria; il tipo ne determina dimensione e interpretazione.
- Solo i puntatori contengono indirizzi di memoria.

**Esempio:**
```c
int x = 10;
int *p = &x;
```
- `x` → variabile normale
- `&x` → indirizzo di memoria di `x`
- `p` → puntatore a `int` che contiene l’indirizzo di `x`

---

## **2. Visualizzazione in Memoria**

| Indirizzo  | Contenuto       |
|------------|-----------------|
| 0x1000     | p = 0x2000      |
| ...        | ...             |
| 0x2000     | x = 10          |

- `p` **non contiene 10**, ma **0x2000** (l’indirizzo di `x`).

---

## **3. Operatori Fondamentali**

### **a) Operatore `&` (address-of)**
Restituisce **l’indirizzo** di una variabile.
```c
&x  // indirizzo di x
&p  // indirizzo di p
```

### **b) Operatore `*` (dereferenziazione)**
Restituisce **il valore puntato** dal puntatore.
```c
*p  // valore di x (10)
```
- `printf("%d", *p);` → stampa `10`

---

## **4. Modifica Tramite Puntatore**
Modificando `*p`, si modifica direttamente `x`:
```c
*p = 20;
```
- Ora `x` vale `20`.
- **Potere dei puntatori:** permettono di **modificare dati indirettamente**.

---

## **5. Tipi e Coerenza**
Il tipo del puntatore **deve corrispondere** al tipo della variabile puntata:
```c
int x;
int *p = &x;   // OK
float *f = &x; // SBAGLIATO
```
- Il tipo dice al compilatore:
  - Quanti byte leggere
  - Come interpretare quei byte

---

## **6. Errori Tipici**
- **Puntatore non inizializzato:**
  ```c
  int *p;
  *p = 10;  // ERRORE: p non punta a niente
  ```
- **Dereferenziazione di NULL:**
  ```c
  int *p = NULL;
  *p = 10;  // ERRORE: dereferenziazione di NULL
  ```
- **Sempre inizializzare i puntatori prima dell’uso!**

---

## **7. Puntatori e Funzioni**
I puntatori permettono di **modificare variabili esterne** a una funzione.
**Esempio:**
```c
int add_two(int *n) {
    *n = *n + 2;
    return *n;
}
int main() {
    int numero = 5;
    add_two(&numero);
    // Ora numero = 7
    return 0;
}
```
- La funzione riceve **l’indirizzo** di `numero` e ne modifica il valore.

---

## **8. Puntatori e Stringhe**
In C **non esiste un tipo “stringa”**: una stringa è un **array di char terminato da `\0`**.

### **a) Dichiarazione e Inizializzazione**
```c
char *s = "Hello";
```
- `s` punta al primo carattere (`'H'`).
- La stringa in memoria:
  ```
  H | e | l | l | o | \0
  ```

### **b) Aritmetica dei Puntatori**
- `*s` → `'H'`
- `s + 1` → punta a `'e'`
- Si può scorrere la stringa fino a `\0`.

### **c) Equivalenza**
- `s == &s[0]` (entrambi puntano a `'H'`).

---

## **9. Quando Usare i Puntatori?**
- **Modificare variabili indirettamente** (es. in funzioni).
- **Gestire array e stringhe** in modo efficiente.
- **Allocazione dinamica della memoria** (es. `malloc`, `calloc`).
- **Passare grandi strutture dati** senza copiarle¹.

---

## **10.Scorrere una Stringa**
```c
#include <stdio.h>

int main() {
    char *s = "Hello";
    while (*s != '\0') {
        printf("%c ", *s);
        s++;
    }
    // Stampa: H e l l o
    return 0;
}
```

> ¹ In C, quando passi una struttura a una funzione per valore, viene creata una copia della struttura, il che può essere inefficienti per strutture grandi. Per evitare questo, puoi passare un puntatore alla struttura.

---





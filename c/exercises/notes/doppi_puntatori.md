# Perché servono i doppi puntatori

## Il problema: modificare un puntatore da una funzione

```c
contact *phonebook = NULL;
add(&phonebook, "Mario", "111");  // vogliamo che phonebook punti a Mario
```

---

## SBAGLIATO: puntatore singolo

```c
void add(contact *head, ...) {
    contact *new = malloc(...);
    head = new;  // ❌ NON FUNZIONA!
}

add(phonebook, "Mario", "111");
```

### Cosa succede in memoria:

```
PRIMA della chiamata add():

    main()
    ┌─────────────────┐
    │ phonebook: NULL │  ← variabile in main
    └─────────────────┘


DURANTE add(phonebook, ...):

    main()                         add()
    ┌─────────────────┐           ┌─────────────┐
    │ phonebook: NULL │           │ head: NULL  │  ← COPIA del valore!
    └─────────────────┘           └─────────────┘
                                         │
                                         │ head = new;
                                         ▼
    ┌─────────────────┐           ┌─────────────┐      ┌───────┐
    │ phonebook: NULL │           │ head: ────────────▶│ Mario │
    └─────────────────┘           └─────────────┘      └───────┘
           │
           │ phonebook NON È CAMBIATO!
           ▼

DOPO add() ritorna:

    main()
    ┌─────────────────┐                               ┌───────┐
    │ phonebook: NULL │  ← ancora NULL!               │ Mario │ ← PERSO!
    └─────────────────┘                               └───────┘
                                                      (memory leak)
```

**Problema:** `head` è una COPIA di `phonebook`. Modificare la copia non cambia l'originale.

---

## CORRETTO: doppio puntatore

```c
void add(contact **head, ...) {
    contact *new = malloc(...);
    *head = new;  // ✅ FUNZIONA!
}

add(&phonebook, "Mario", "111");
```

### Cosa succede in memoria:

```
PRIMA della chiamata add():

    main()
    ┌─────────────────────┐
    │ phonebook: NULL     │  indirizzo: 0x1000
    └─────────────────────┘


DURANTE add(&phonebook, ...):

    main()                              add()
    ┌─────────────────────┐            ┌────────────────┐
    │ phonebook: NULL     │◀───────────│ head: 0x1000   │
    └─────────────────────┘            └────────────────┘
    indirizzo: 0x1000                   (indirizzo di phonebook!)
                │
                │  *head = new;  (scrivi all'indirizzo 0x1000)
                ▼
    ┌─────────────────────┐            ┌────────────────┐      ┌───────┐
    │ phonebook: ─────────────────────────────────────────────▶│ Mario │
    └─────────────────────┘            └────────────────┘      └───────┘


DOPO add() ritorna:

    main()
    ┌─────────────────────┐      ┌───────┐
    │ phonebook: ─────────────▶  │ Mario │  ← FUNZIONA!
    └─────────────────────┘      └───────┘
```

---

## Visualizzazione dei livelli

```
PUNTATORE SINGOLO (*):

    phonebook ──────▶ [Mario] ──────▶ [Luigi] ──────▶ NULL
        │
        └── contiene l'indirizzo di Mario


DOPPIO PUNTATORE (**):

    &phonebook ──────▶ phonebook ──────▶ [Mario] ──────▶ [Luigi]
        │                  │
        │                  └── contiene indirizzo di Mario
        │
        └── contiene indirizzo di phonebook


In codice:
    contact *phonebook;     // puntatore a contact
    contact **head;         // puntatore a puntatore a contact

    head = &phonebook;      // head punta a phonebook
    *head = new;            // modifica ciò che phonebook punta
```

---

## Analogia: la cassetta delle lettere

```
PUNTATORE SINGOLO (copia):

    Hai l'indirizzo "Via Roma 1" scritto su un foglio.
    Se cancelli il foglio e scrivi "Via Milano 2",
    la casa a Via Roma 1 non si sposta!
    Hai solo cambiato il tuo foglio.


DOPPIO PUNTATORE (riferimento):

    Hai l'indirizzo DELLA RUBRICA dove è scritto "Via Roma 1".
    Puoi aprire la rubrica e cambiare l'indirizzo scritto dentro.
    Ora la rubrica dice "Via Milano 2".
    Chiunque guardi la rubrica vedrà il nuovo indirizzo.
```

---

## Quando usare * vs **

| Situazione | Usa | Perché |
|------------|-----|--------|
| Leggere i dati | `*` | Non modifichi il puntatore |
| Modificare i dati puntati | `*` | `ptr->campo = x` funziona |
| Cambiare DOVE punta il puntatore | `**` | Devi modificare il puntatore stesso |

```c
// Leggo/modifico i DATI (basta *)
void print(contact *head) {
    printf("%s", head->name);  // leggo
    head->name[0] = 'X';       // modifico i dati (funziona con *)
}

// Cambio DOVE PUNTA il puntatore (serve **)
void add(contact **head) {
    *head = new;  // cambio dove punta phonebook
}

void delete_first(contact **head) {
    contact *old = *head;
    *head = (*head)->next;  // cambio dove punta phonebook
    free(old);
}
```

---

## Trucco mnemonico

```
*   = "il valore contenuto in"
&   = "l'indirizzo di"
**  = "il valore contenuto nel valore contenuto in" (doppia indirezione)

contact *p;      // p contiene un indirizzo → va a un contact
contact **pp;    // pp contiene un indirizzo → va a un puntatore → va a un contact

*p   = dereferenzia una volta  → contact
*pp  = dereferenzia una volta  → contact*
**pp = dereferenzia due volte  → contact
```

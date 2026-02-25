#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Struct Contact
typedef struct Contact {
    char name[50];
    char phone[20];
    struct Contact* next;
    struct Contact* prev;
} contact;

contact* find_middle(contact* head) {
    if (head == NULL) return NULL;

    contact* slow = head;
    contact* fast = head;
    while (fast != NULL && fast->next != NULL) {
        fast = fast->next->next;
        slow = slow->next;
    }

    return slow;
}
contact* create_contact(char* name, char* phone) {
    contact* new = (contact*)malloc(sizeof(contact));
    if (new == NULL) {
        fprintf(stderr, "Error while allocating memory\n");
        return NULL;
    }
    strncpy(new->name, name, sizeof(new->name) - 1);
    new->name[sizeof(new->name) - 1] = '\0';
    strncpy(new->phone, phone, sizeof(new->phone) - 1);
    new->phone[sizeof(new->phone) - 1] = '\0';
    new->next = NULL;
    new->prev = NULL;
    return new;
}

// Insert at an arbitrary index
void insert_at(contact** head, char* name, char* phone, int index) {
    int i = 0;
    contact* new = create_contact(name, phone);

    while (*head != NULL && i != index) {
        i++;
        head = &(*head)->next;
    }

    new->next = *head;
    if ((*head) != NULL) {
        new->prev = (*head)->prev;
        (*head)->prev = new;
    }
    *head = new;
    return;
}

// reverse()
void reverse(contact** head) {
    contact* current = *head;
    contact* new_head = NULL;

    while (current != NULL) {
        contact* next = current->next;

        current->next = current->prev;
        current->prev = next;

        new_head = current;
        current = next;
    }

    *head = new_head;
}

// add() - add to tail
void add(contact** head, char* name, char* phone) {
    contact* new = create_contact(name, phone);
    if (new == NULL) {
        fprintf(stderr, "Error while allocating memory\n");
        return;
    }

    if (*head == NULL) {
        *head = new;
        return;
    }

    contact* temp = *head;
    while (temp->next != NULL) {
        temp = temp->next;
    }
    new->prev = temp;
    temp->next = new;
    return;
}

void add_head(contact** head, char* name, char* phone) {
    contact* new = create_contact(name, phone);
    if (new == NULL) return;
    if (*head != NULL) (*head)->prev = new;
    new->next = *head;
    *head = new;
}

// print_phonebook()
void print_phonebook(contact* head) {
    while (head != NULL) {
        printf("| %-10s | %-22s |\n", head->name, head->phone);
        head = head->next;
    }
}

// find()
contact* find(contact* head, char* name) {
    if (head == NULL) {
        fprintf(stderr, "Contact %s, not found. Empty list.\n", name);
        return NULL;
    }

    while (head != NULL) {
        if (strcmp(head->name, name) == 0) {
            return head;
        }
        head = head->next;
    }

    printf("Contact %s not found.\n", name);
    return NULL;
}

// delete()
void delete(contact** head, char* name) {
    while (*head != NULL) {
        if (strcmp((*head)->name, name) == 0) {
            contact* to_free = *head;
            *head = (*head)->next;
            if ((*head) != NULL) {
                (*head)->prev = to_free->prev;
            }
            free(to_free);
            return;
        }
        head = &(*head)->next;
    }
}

int main(void) {
    contact* phonebook = NULL;
    // find(phonebook, "Bowser");

    add(&phonebook, "Mario", "111");
    add(&phonebook, "Luigi", "222");
    add_head(&phonebook, "Bowser", "434");
    // print_phonebook(phonebook);

    contact* altra_rubrica = NULL;
    add(&altra_rubrica, "Peach", "333");

    delete(&phonebook, "Bowser");
    insert_at(&phonebook, "Donkey Kong", "5555", 0);
    // printf("Rubrica 2:\n");
    // print_phonebook(altra_rubrica);
    add(&phonebook, "Toad", "88554");
    find(phonebook, "Toad");
    print_phonebook(phonebook);

    return 0;
}

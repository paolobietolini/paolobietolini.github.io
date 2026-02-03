#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Struct Contact
typedef struct Contact
{
    char name[50];
    char phone[20];
    struct Contact *next;
} contact;


// add()
void add(contact **head, char *name, char *phone)
{
    contact *new = (contact *)malloc(sizeof(contact));
    if (new == NULL)
    {
        fprintf(stderr, "Error while allocating memory\n");
        return;
    }
    int nameLen = sizeof(new->name);
    int phoneLen = sizeof(new->phone);
    strncpy(new->name, name, nameLen - 1);
    new->name[nameLen - 1] = '\0';
    strncpy(new->phone, phone, phoneLen - 1);
    new->phone[phoneLen - 1] = '\0';

    if (*head == NULL)
    {
        *head = new;
        return;
    }

    contact *temp = *head;
    while (temp->next != NULL)
    {
        temp = temp->next;
    }

    new->next = *head;
    *head = new;
    return;
}

void add_head(contact **head, char *name, char *phone)
{
    contact *new = (contact *)malloc(sizeof(contact));
    if (new == NULL)
    {
        fprintf(stderr, "Error while allocating memory\n");
        return;
    }
    int nameLen = sizeof(new->name);
    int phoneLen = sizeof(new->phone);
    strncpy(new->name, name, nameLen - 1);
    new->name[nameLen - 1] = '\0';
    strncpy(new->phone, phone, phoneLen - 1);
    new->phone[phoneLen - 1] = '\0';

    if (*head == NULL)
    {
        *head = new;
        return;
    }

    new->next = *head;
    *head = new;
    return;
}
// print_phonebook()
void print_phonebook(contact *head)
{
    while (head != NULL)
    {
        printf("| %-10s | %-22s |\n", head->name, head->phone);
        head = head->next;
    }
}

// find()
contact *find(contact *head, char *name) {
    if(head == NULL) {
        fprintf(stderr, "Contact %s, not found. Empty list.\n", name);
        return NULL;
    }

    while(head != NULL) {
        if(strcmp(head->name, name) == 0) {
            return head;
        }
        head = head->next;
    }

    printf("Contact %s not found.\n", name);
    return NULL;
}

// delete()
void delete(contact **head, char *name) {
    while (*head != NULL) {
        if (strcmp((*head)->name, name) == 0) {
            contact *to_free = *head;
            *head = (*head)->next;
            free(to_free);
            return;
        }
        head = &(*head)->next;
    }
}
int main(void)
{
    contact *phonebook = NULL;
    find(phonebook, "Bowser");

    add(&phonebook, "Mario", "111");
    add(&phonebook, "Luigi", "222");
    add_head(&phonebook, "Bowser", "434");
    print_phonebook(phonebook);

    // Bonus: puoi avere più liste!
    contact *altra_rubrica = NULL;
    add(&altra_rubrica, "Peach", "333");

    delete(&phonebook, "Bowser");

    printf("Rubrica 1:\n");
    print_phonebook(phonebook);
    printf("Rubrica 2:\n");
    print_phonebook(altra_rubrica);
    find(phonebook, "Toad");

    return 0;
}

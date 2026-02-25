/*
 * TEST FILE per syntax_checker.c
 * Copri questo file nella stessa cartella del tuo syntax_checker
 * 
 * Per testare: ./syntax_checker < test_cases.c
 * 
 * Include:
 * - Casi corretti (should return 0)
 * - Casi con errori (should return 1) 
 * - Edge cases comuni
 */

// =============================================================================
// SEZIONE 1: CODICE CORRETTO (dovrebbe passare senza errori)
// =============================================================================

#include <stdio.h>
#include <stdlib.h>

// Test 1: Nested brackets normali
int main(void) {
    int arr[10] = {1, 2, 3, 4, 5};
    
    if (arr[0] == 1) {
        for (int i = 0; i < 10; i++) {
            printf("arr[%d] = %d\n", i, arr[i]);
        }
    }
    
    return 0;
}

// Test 2: Stringhe con brackets inside (dovrebbero essere ignorate)
void test_strings(void) {
    printf("This ( has ) many [ different ] brackets { inside }");
    printf("Even \"quoted brackets [like these]\" should work");
    
    // Escape sequences
    printf("Say \"hello\" to the world\n");
    printf("Backslash: \\ and quote: \"\n");
}

// Test 3: Character literals
void test_chars(void) {
    char open_paren = '(';
    char close_bracket = ']';
    char escaped_quote = '\'';
    char backslash = '\\';
}

// Test 4: Commenti con brackets (dovrebbero essere ignorati)
void test_comments(void) {
    /* This ( comment has ] unmatched brackets } but it's OK */
    
    // This line comment has [ unmatched ) brackets too
    
    // Triple slash comment ///
    int x = 5; //// Quadruple slash
}

// Test 5: Block comments multilinea
void test_multiline_comments(void) {
    /*
     * This is a multiline comment
     * with ( various [ brackets } that
     * should be ignored completely
     */
    
    int valid_code = 42;
}

// Test 6: Nested structures complesse
void complex_nesting(void) {
    struct data {
        int matrix[3][3];
        char text[100];
    } info = {
        .matrix = {{1, 2, 3}, {4, 5, 6}, {7, 8, 9}},
        .text = "Complex structure with [nested] brackets"
    };
    
    if (info.matrix[0][0] == 1) {
        while (info.matrix[1][1] < 10) {
            for (int i = 0; i < 3; i++) {
                printf("%d ", info.matrix[i][i]);
            }
        }
    }
}

// =============================================================================
// SEZIONE 2: CODICE CON ERRORI (per test separati)
// Commenta/sccommenta per testare errori specifici
// =============================================================================

/*
// ERROR TEST 1: Missing closing brace
void error_test_1(void) {
    int arr[10] = {1, 2, 3;  // <- missing }
    return;
}

// ERROR TEST 2: Extra closing bracket  
void error_test_2(void) {
    int arr[10] = {1, 2, 3}];  // <- extra ]
}

// ERROR TEST 3: Mismatched brackets
void error_test_3(void) {
    if (arr[0) == 1) {  // <- [ closed by )
        return;
    }
}

// ERROR TEST 4: Unclosed function
void error_test_4(void) {
    printf("Missing closing brace");
    // <- function never closes

// ERROR TEST 5: Mixed mismatch
void error_test_5(void) {
    int data[10] = (1, 2, 3];  // <- ( closed by ]
}
*/

// =============================================================================
// SEZIONE 3: EDGE CASES INTERESSANTI  
// =============================================================================

// Test edge case: Commento seguito immediatamente da stringa
void edge_case_1(void) {
    /*comment*/printf("immediate string");
}

// Test edge case: Slash non seguiti da / o *
void edge_case_2(void) {
    int division = 10 / 5;  // Normal division, not comment
    char path[] = "/home/user/file.txt";  // Path con slash
}

// Test edge case: Caratteri speciali in stringhe
void edge_case_3(void) {
    printf("Special chars: !@#$%^&*()_+-=[]{}|;:,.<>?");
    printf("Escaped newline: \n and tab: \t");
}

// Test edge case: Commenti nested (C non li supporta ma testiamo)
void edge_case_4(void) {
    /* Outer comment /* inner comment */ printf("This should be commented"); */
    printf("This line should be visible");
}

// Test edge case: Empty brackets
void edge_case_5(void) {
    int empty_array[] = {};
    if (1) { /* empty block */ }
    function_call();  // () vuote
}

// =============================================================================
// ISTRUZIONI D'USO:
//
// 1. CODICE CORRETTO: Esegui con tutto il file
//    ./syntax_checker < test_cases.c
//    Dovrebbe ritornare 0 (no errors)
//
// 2. TEST ERRORI: Sccommenta UN error test alla volta
//    ./syntax_checker < test_cases.c  
//    Dovrebbe ritornare 1 e mostrare l'errore specifico
//
// 3. DEBUG: Se hai problemi, usa echo per testare frammenti:
//    echo 'printf("test [");' | ./syntax_checker
//
// 4. CHECK RETURN CODE:
//    ./syntax_checker < test_cases.c; echo "Exit code: $?"
// =============================================================================

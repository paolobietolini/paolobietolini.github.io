#include <stdio.h>

#define MAX_NUMBERS 100

int get_numbers(int numbers[]) {
  int n, i = 0;
  while (scanf("%d", &n) == 1 && i < MAX_NUMBERS) {
    numbers[i++] = n;
  }
  return i;
}

int main(void) {
  int numbers[MAX_NUMBERS];
  int count;
  int max, min, even_count, sum;
  double avg;

  count = get_numbers(numbers);

  if (count == 0)
    return -1;

  max = min = sum = numbers[0];
  even_count = (numbers[0] % 2 == 0);

  for (int i = 1; i < count; i++) {
    if (numbers[i] > max)
      max = numbers[i];
    if (numbers[i] < min)
      min = numbers[i];
    if (numbers[i] % 2 == 0)
      even_count++;
    sum += numbers[i];
  }

  avg = (double)sum / count;

  printf("Numbers read: %d\n", count);
  printf("Maximum value: %d\n", max);
  printf("Minimum value: %d\n", min);
  printf("Even numbers: %d\n", even_count);
  printf("Arithmetic mean: %.2f\n", avg);

  return 0;
}
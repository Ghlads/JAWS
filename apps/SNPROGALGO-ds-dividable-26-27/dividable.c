#include "dividable.h"
#include <stdio.h>

int min(const int a, const int b) { return a < b ? a : b; }

int max(const int a, const int b) { return a > b ? a : b; }

int test_prime_number(const int tested) {
  if (tested < 2) {
    return 0;
  }

  for (int division = 2; division < tested; division++) {
    if ((tested % division) == 0) {
      return 0;
    }
  }

  return 1;
}

void divprint(const Dividable *dividable) {
  printf("Dividable: [value: %d, sd: %d, bd: %d]\n", dividable->value,
         dividable->sd, dividable->bd);
}

void divinit(Dividable *dividable) {
  if (dividable == NULL) {
    return;
  }

  dividable->value = 6;
  dividable->sd = 2;
  dividable->bd = 3;
}

Dividable divmake(const int a, const int b) {
  Dividable result = {};
  result.value = a * b;
  result.sd = min(a, b);
  result.bd = max(a, b);
  return result;
}

Dividable divmultiply(const Dividable *divA, const Dividable *divB) {
  Dividable result = {};
  result.value = divA->value * divB->value;
  result.sd = min(divA->sd, divB->sd);
  result.bd = max(divA->bd, divB->bd);
  return result;
}

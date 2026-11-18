#include "dividable.h"
#include <stdio.h>

void print_is_prime(int number) {
  int is_prime = test_prime_number(number);
  printf("%d: is", number);
  if (!is_prime) {
    printf(" not ");
  }
  printf("prime\n");
}

int main() {
  Dividable div = {38115, 3, 11};
  divprint(&div);
  divinit(&div);
  divprint(&div);

  print_is_prime(div.value);
  print_is_prime(div.sd);
  print_is_prime(div.bd);

  Dividable other_div = divmake(13, 11);
  divprint(&other_div);
  Dividable mul_div = divmultiply(&div, &other_div);
  divprint(&mul_div);
}

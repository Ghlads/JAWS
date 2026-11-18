#ifndef __DIVIDABLE
#define __DIVIDABLE

typedef struct Dividable {
  int value;
  int sd; // smallest dividable
  int bd; // biggest dividable
} Dividable;

int test_prime_number(const int tested);
void divprint(const Dividable *dividable);
void divinit(Dividable *dividable);
Dividable divmake(const int a, const int b);
Dividable divmultiply(const Dividable *divA, const Dividable *divB);

#endif // __DIVIDABLE

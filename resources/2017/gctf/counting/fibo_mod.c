// Taken from https://medium.com/competitive/huge-fibonacci-number-modulo-m-6b4926a5c836
// $ clang -o fibo_mod fibo_mod.c -Wall -Wextra -Werror -pedantic -O3

#include <stdio.h>
#include <stdlib.h>

long long get_fibonacci_huge(long long n, long long m, long long p) {
    long long remainder = n % p;

    long long first = 0;
    long long second = 1;

    long long res = remainder;

    for (int i = 1; i < remainder; i++) {
        res = (first + second) % m;
        first = second;
        second = res;
    }

    return res % m;
}

int main(int argc, char ** argv) {
    if(argc != 4) { return 0; }
    long long n = strtoull(argv[1], NULL, 10);
    long long m = strtoull(argv[2], NULL, 10);
    long long p = strtoull(argv[3], NULL, 10);

    printf("<FLAG:%#llx>\n", get_fibonacci_huge(n, m, p));
    return 0;
}

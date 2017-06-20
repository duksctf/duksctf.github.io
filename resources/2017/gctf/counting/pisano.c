// Taken from https://stackoverflow.com/questions/37009744/calculate-huge-fibonacci-number-modulo-m-in-c
// $ clang -o pisano pisano.c  -Wall -Wextra -Werror -pedantic -O3

#include <stdio.h>
#include <stdlib.h>

long long pisano(long long m) {
    long long result = 2;
    for (long long fn2 = 1, fn1 = 2 % m, fn = 3 % m;
    fn1 != 1 || fn != 1;
        fn2 = fn1, fn1 = fn, fn = (fn1 + fn2) % m
        ) {
        result++;
    }
    return result;
}

int main(int argc, char ** argv) {
    if(argc != 2) { return 0; }
    long long m = strtoull(argv[1], NULL, 10);

    printf("<PISANO:%#llx>\n", pisano(m));
    return 0;
}

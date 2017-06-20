// Taken from: https://rosettacode.org/wiki/Hailstone_sequence#With_caching
// $ clang -o hailstone hailstone.c -Wall -Wextra -Werror -pedantic -O3

#include <stdio.h>
#include <stdlib.h>

#define N 100000000
#define CS N	/* cache size */

typedef unsigned long long ulong;
ulong cache[CS] = {0};

ulong hailstone(ulong n)
{
	int x;
	if (n == 1) return 1;
	if (n < CS && cache[n]) return cache[n];

	x = 1 + hailstone((n & 1) ? 3 * n + 1 : n / 2);
	if (n < CS) cache[n] = x;
	return x;
}

int main(int argc, char** argv)
{
    if(argc != 2) { return 0; }
    ulong x = strtoull(argv[1], NULL, 10);
    ulong sum = 0;

	for (ulong i = 1; i <= x; i++) {
        sum += hailstone(i) - 1;
	}

    printf("<MODULO:%#llx>\n", sum);
	return 0;
}

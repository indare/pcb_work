CC ?= cc
CFLAGS ?= -O2 -std=c11 -Wall -Wextra -I.
LDFLAGS ?= -lm

.PHONY: test clean

test: test_host
	./test_host

test_host: test_host.c fft_q15.c fft_q15.h
	$(CC) $(CFLAGS) -o $@ test_host.c fft_q15.c $(LDFLAGS)

clean:
	rm -f test_host

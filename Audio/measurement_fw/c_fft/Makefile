CC ?= cc
CFLAGS ?= -O2 -std=c11 -Wall -Wextra -I.
LDFLAGS ?= -lm

.PHONY: test sanitize clean

test: test_host
	./test_host

sanitize:
	$(CC) $(CFLAGS) -O1 -g -fsanitize=undefined -o test_host_san test_host.c fft_q15.c $(LDFLAGS)
	UBSAN_OPTIONS=halt_on_error=1 ./test_host_san

test_host: test_host.c fft_q15.c fft_q15.h
	$(CC) $(CFLAGS) -o $@ test_host.c fft_q15.c $(LDFLAGS)

clean:
	rm -f test_host test_host_san

# Define variable CC to be the compiler we want to use
CC = clang

# Define CFLAGS for the flags we will want to use with clang
CLANG = -g -Wall

TARGETS = clean penn-sh
DEPS = tokenizer.h

.PHONY: penn-sh alarm

# If no arguments are passed to make, it will attempt the listed target(s)
default: penn-sh

%.o: %.c $(DEPS)
	$(CC) -c -o $@ $< $(CFLAGS)

# This runs the 'clean' and other targets when 'make all' is run
all: $(TARGETS)

# $^ = names of all the dependent files, deduped and with spaces
# $@ = complete name of the target
penn-sh: tokenizer.o penn-sh.o
	$(CC) -o penn-sh penn-sh.o tokenizer.o

tokenizer.o: tokenizer.c
	$(CC) -c tokenizer.c

penn-sh.o: penn-sh.c
	$(CC) -c penn-sh.c

# $(RM) is the platform agnostic way to delete a file (here rm -f)
clean:
	$(RM) penn-sh *.o
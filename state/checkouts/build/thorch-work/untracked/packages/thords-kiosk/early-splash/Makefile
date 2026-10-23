CC ?= gcc
CFLAGS ?= -O2 -Wall -Wextra
LDLIBS := $(shell pkg-config --libs libdrm) -lm
CPPFLAGS := $(shell pkg-config --cflags libdrm)

build/early-splash-renderer: src/armada-splash.c src/stb_impl.c
	mkdir -p build
	$(CC) -O2 -w -c src/stb_impl.c -o build/stb_impl.o
	$(CC) $(CFLAGS) $(CPPFLAGS) -o $@ src/armada-splash.c build/stb_impl.o $(LDLIBS)
	strip $@

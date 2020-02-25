#FLAGS ?= -Wall -O0 -g -pedantic-errors -std=c99 
FLAGS ?= -Wall -O0 -g -pedantic-errors -std=gnu99 
COMPILLER:=$(shell sh -c 'type $(CC) >/dev/null 2>/dev/null && echo $(CC) || echo gcc')
BUILDDIR?=bin

all: main
 
main: main.c
	${COMPILLER} ${FLAGS} -rdynamic -o ${BUILDDIR}/mywsd main.c server.c users.c lists.c core.c parson.c bb.c libsha.c redis_thread.c -lhiredis -lev -L/usr/local/lib -I/usr/local/include -pthread

clean: 
	rm -f mywsd server.o

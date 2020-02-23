# Use Abacus's build options if it exists
-include $(ABACUS)/common.mk

CXX ?= g++
CXXFLAGS += -O3 -std=c++11 -Wall
CPPFLAGS += -Isrc

TARGETS := fast_cksum/fast_cksum.so bin/fast_cksum bin/fast_cksum_store

all: cli python

cli: bin/fast_cksum bin/fast_cksum_store

python: fast_cksum/fast_cksum.so

fast_cksum/fast_cksum.so: src/fast_cksum.cpp src/fast_cksum.h
	${CXX} ${CXXFLAGS} ${CPPFLAGS} -o $@ $< -shared -fPIC

# TODO: compiler-generated dependencies
bin/fast_cksum: cli/fast_cksum_cli.cpp
	mkdir -p bin
	${CXX} ${CXXFLAGS} ${CPPFLAGS} -o $@ $<

bin/fast_cksum_store: cli/fast_cksum_store.cpp
	mkdir -p bin
	${CXX} ${CXXFLAGS} ${CPPFLAGS} -o $@ $<

clean:
	$(RM) $(TARGETS)

.PHONY: python cli all clean

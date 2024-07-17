# Use Abacus's build options if it exists
#-include $(ABACUS)/common.mk

CXXFLAGS += -O3 -g -std=c++11 -Wall -Wextra -march=native
CPPFLAGS += -Isrc

TARGETS := fast_cksum/fast_cksum.so bin/fast_cksum bin/fast_cksum_store bin/fast_cksum_cat

all: cli python

cli: bin/fast_cksum bin/fast_cksum_store bin/fast_cksum_cat

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

bin/fast_cksum_cat: cli/fast_cksum_cat.cpp
	mkdir -p bin
	${CXX} ${CXXFLAGS} ${CPPFLAGS} -o $@ $<

clean:
	$(RM) $(TARGETS)

.PHONY: python cli all clean

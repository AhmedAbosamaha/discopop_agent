all: clean prog

prog: code.o
	$(CC) -o prog code.o $(CFLAGS) -lm

code.o:
	$(CC) -c -S -emit-llvm -o code.ll code.c $(CFLAGS)
	rm -rf .discopop
	$(CC) -c -o code.o code.c $(CFLAGS)

clean:
	rm -rf .discopop
	rm -rf src/.discopop
	find . -not -name code.c -not -name Makefile -not -path **/FileMapping.txt -delete

veryclean: clean
	rm -f FileMapping.txt

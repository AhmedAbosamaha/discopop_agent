#ifndef KERN_H
#define KERN_H
#define R 300
#define T 40
extern double a[R][T];
extern double b[R];
void kernel(int n);
void smooth(int n);
#endif

// Bad: Buffer overflow and use-after-free

#include <string.h>

int main() {
    char buffer[10];
    const char *source = "This is a very long string";
    
    // cpp-memory-001: strcpy buffer overflow
    strcpy(buffer, source);
    
    // cpp-memory-002: use-after-free
    int *ptr = new int(42);
    delete ptr;
    *ptr = 0;
    
    return 0;
}

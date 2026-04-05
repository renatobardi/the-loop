// Bad: Hardcoded cryptographic keys

#include <string>

int main() {
    // cpp-crypto-001: hardcoded key
    unsigned char key[] = {0x01, 0x02, 0x03, 0x04, 0x05};
    
    // cpp-crypto-002: weak random
    int weak_random = rand();
    
    return 0;
}

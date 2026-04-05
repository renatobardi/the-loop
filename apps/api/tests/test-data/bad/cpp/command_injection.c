// Bad: Command injection

#include <stdlib.h>

int main() {
    char cmd[256];
    const char *user_cmd = get_user_input();
    
    // cpp-injection-002: system() with user input
    system(user_cmd);
    
    return 0;
}

// Bad: SQL injection

#include <stdio.h>
#include <stdlib.h>
#include <sqlite3.h>

int main() {
    char query[256];
    const char *user_id = get_user_input();
    
    // cpp-injection-001: SQL injection via sprintf
    sprintf(query, "SELECT * FROM users WHERE id = %s", user_id);
    
    sqlite3 *db;
    sqlite3_prepare_v2(db, query, -1, NULL, NULL);
    
    return 0;
}

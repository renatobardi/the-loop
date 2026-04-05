using System;
using System.Data.SqlClient;

public class SqlInjectionCsharp {
    public void BadSqlConcatenation(string userId) {
        // BAD: SQL injection via string concatenation
        string query = "SELECT * FROM Users WHERE Id=" + userId;
        using (SqlCommand cmd = new SqlCommand(query)) {
            cmd.ExecuteReader();
        }
    }

    public void BadLinqInjection(DbContext context, string userInput) {
        // BAD: Dynamic SQL via FromSqlRaw
        var users = context.Users.FromSqlRaw("SELECT * FROM Users WHERE Name = " + userInput).ToList();
    }
}

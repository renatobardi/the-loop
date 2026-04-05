using System;
using System.Data.SqlClient;
using System.Security.Cryptography;

public class SecureCsharp {
    public void GoodParameterizedQuery(string userId) {
        // GOOD: Parameterized query prevents SQL injection
        string query = "SELECT * FROM Users WHERE Id = @userId";
        using (SqlCommand cmd = new SqlCommand(query)) {
            cmd.Parameters.AddWithValue("@userId", userId);
            cmd.ExecuteReader();
        }
    }

    public void GoodLinqParameterized(DbContext context, string userInput) {
        // GOOD: Using parameterized FromSqlInterpolated
        var users = context.Users.FromSqlInterpolated($"SELECT * FROM Users WHERE Name = {userInput}").ToList();
    }

    public void GoodSha256Hash(string data) {
        // GOOD: SHA-256 is cryptographically secure
        using (var hash = SHA256.Create()) {
            var hashBytes = hash.ComputeHash(System.Text.Encoding.UTF8.GetBytes(data));
        }
    }

    public void GoodTlsValidation() {
        // GOOD: TLS validation enabled (default)
        var handler = new System.Net.Http.HttpClientHandler();
        // ServerCertificateCustomValidationCallback defaults to validating certificates
    }
}

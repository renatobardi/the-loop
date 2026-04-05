using System.Security.Cryptography;

public class CryptoWeakCsharp {
    public void BadMd5Hash(string data) {
        // BAD: MD5 is cryptographically weak
        using (var hash = MD5.Create()) {
            var hashBytes = hash.ComputeHash(System.Text.Encoding.UTF8.GetBytes(data));
        }
    }

    public void BadHardcodedKey() {
        // BAD: Hardcoded encryption key
        string encryptionKey = "MySecretKey12345SecurePassword";
    }
}

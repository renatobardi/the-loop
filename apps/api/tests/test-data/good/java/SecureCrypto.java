import java.security.*;
import javax.crypto.Cipher;
import javax.crypto.KeyGenerator;
import javax.crypto.SecretKey;

public class SecureCrypto {
    public void goodHashWithSha256(String data) throws NoSuchAlgorithmException {
        // GOOD: SHA-256 is cryptographically secure
        MessageDigest digest = MessageDigest.getInstance("SHA-256");
        digest.update(data.getBytes());
        byte[] hash = digest.digest();
    }

    public String goodRandomToken() throws NoSuchAlgorithmException {
        // GOOD: Using SecureRandom for security-sensitive values
        SecureRandom secureRandom = new SecureRandom();
        byte[] tokenBytes = new byte[32];
        secureRandom.nextBytes(tokenBytes);
        return java.util.Base64.getEncoder().encodeToString(tokenBytes);
    }

    public void goodTlsConfiguration(String host, int port) throws Exception {
        // GOOD: JDBC connection with SSL/TLS enabled
        String url = "jdbc:mysql://" + host + ":" + port + "/mydb?sslMode=REQUIRED";
        java.sql.Connection conn = java.sql.DriverManager.getConnection(url, "user", "pass");
    }
}

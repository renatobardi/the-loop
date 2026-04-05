public class HardcodedCredential {
    // BAD: Hardcoded API key in code
    private static final String API_KEY = "sk_live_51234567890abcdefgh";

    private String dbPassword = "admin123password";

    public void connectToDb() {
        // BAD: Hardcoded password in connection string
        String connectionUrl = "jdbc:mysql://localhost:3306/mydb?user=admin&password=SecretPass123";
    }
}

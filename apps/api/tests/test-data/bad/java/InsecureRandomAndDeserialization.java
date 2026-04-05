import java.io.*;
import java.util.Random;

public class InsecureRandomAndDeserialization {
    public void badRandomForToken() {
        // BAD: java.util.Random is not cryptographically secure
        Random random = new Random();
        String token = "token_" + random.nextInt(Integer.MAX_VALUE);
    }

    public void badDeserialization(InputStream input) throws IOException, ClassNotFoundException {
        // BAD: Unsafe deserialization with ObjectInputStream
        ObjectInputStream ois = new ObjectInputStream(input);
        Object obj = ois.readObject();  // Vulnerable to gadget chain attacks
    }

    public void badTlsDisabled(String host, int port) throws Exception {
        // BAD: JDBC without SSL/TLS
        String url = "jdbc:mysql://" + host + ":" + port + "/mydb";
        java.sql.Connection conn = java.sql.DriverManager.getConnection(url, "user", "pass");
    }
}

import java.sql.*;

public class SqlInjectionJdbc {
    public void queryWithStringConcat(Statement stmt, String userId) throws SQLException {
        // BAD: SQL injection via string concatenation
        String query = "SELECT * FROM users WHERE id=" + userId;
        stmt.executeQuery(query);
    }

    public void executeUpdateWithConcat(Statement stmt, String tableName, String id) throws SQLException {
        // BAD: Vulnerable to injection
        String sql = "DELETE FROM " + tableName + " WHERE id=" + id;
        stmt.executeUpdate(sql);
    }
}

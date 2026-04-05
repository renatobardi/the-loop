import java.sql.*;

public class SecureJdbc {
    public void queryWithPreparedStatement(Connection conn, String userId) throws SQLException {
        // GOOD: Uses PreparedStatement to prevent SQL injection
        String query = "SELECT * FROM users WHERE id = ?";
        PreparedStatement pstmt = conn.prepareStatement(query);
        pstmt.setString(1, userId);
        ResultSet rs = pstmt.executeQuery();
    }

    public void updateWithParameterized(Connection conn, String tableName, String id, String value) throws SQLException {
        // GOOD: Parameters are properly escaped
        String sql = "UPDATE users SET name = ? WHERE id = ?";
        PreparedStatement pstmt = conn.prepareStatement(sql);
        pstmt.setString(1, value);
        pstmt.setString(2, id);
        pstmt.executeUpdate();
    }
}

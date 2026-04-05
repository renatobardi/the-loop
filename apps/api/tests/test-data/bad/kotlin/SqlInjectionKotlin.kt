// Bad: SQL injection

val userId = request.getParameter("id")

// kotlin-injection-001 & kotlin-injection-002
val query = "SELECT * FROM users WHERE id = $userId"
db.execSQL(query)

val sql = "DELETE FROM users WHERE id = " + userId
connection.prepareStatement(sql)

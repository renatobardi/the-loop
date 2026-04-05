// Good: Secure patterns

val stmt = connection.prepareStatement("SELECT * FROM users WHERE id = ?")
stmt.setInt(1, userId)

val secureKey = generateSecureKey()
val secureRandom = SecureRandom()

val items = database.getAllItems()

items.forEach { item ->
    logger.info("Processing ${item.id}")
}

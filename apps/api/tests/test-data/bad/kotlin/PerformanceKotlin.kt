// Bad: Performance issues

// kotlin-perf-001 & perf-002
for (id in ids) {
    db.query("SELECT * FROM items WHERE id = $id")
}

items.forEach { item ->
    val details = database.getDetails(item.id)
}

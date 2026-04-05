<?php
// Bad: SQL injection via string concatenation

$user_id = $_GET['id'];

// php-injection-001: mysqli_query with string concat
mysqli_query($conn, "SELECT * FROM users WHERE id = " . $user_id);

// php-injection-002: PDO query with string interpolation
$db->query("SELECT * FROM users WHERE id = $user_id");
$db->exec("DELETE FROM users WHERE id = " . $_POST['user_id']);

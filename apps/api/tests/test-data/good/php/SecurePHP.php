<?php
// Good: Secure patterns

// Use prepared statements
$stmt = $conn->prepare("SELECT * FROM users WHERE id = ?");
$stmt->bind_param("i", $user_id);
$stmt->execute();

// Use random_bytes for security
$token = bin2hex(random_bytes(16));

// Use hash with salt
$password_hash = password_hash($password, PASSWORD_BCRYPT);

// Validate CORS origin explicitly
$allowed = ['https://trusted.example.com'];
if (in_array($_SERVER['HTTP_ORIGIN'], $allowed)) {
    header("Access-Control-Allow-Origin: " . $_SERVER['HTTP_ORIGIN']);
}

// Use json_decode instead of unserialize
$data = json_decode($_GET['data'], true);

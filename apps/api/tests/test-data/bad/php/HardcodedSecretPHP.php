<?php
// Bad: Hardcoded secrets

// php-security-001: hardcoded API key
$api_key = "sk_live_123456789abcdef";
$password = "admin123";
$secret = "my_secret_key";

// php-security-002: CORS with wildcard
header("Access-Control-Allow-Origin: *");
$origin = $_SERVER['HTTP_ORIGIN'] . "*";

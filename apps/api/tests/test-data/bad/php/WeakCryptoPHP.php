<?php
// Bad: Weak cryptography

$data = "sensitive";

// php-crypto-001: MD5 and SHA1 are weak
$hash1 = md5($data);
$hash2 = sha1($data);

// php-crypto-002: weak random
$token = rand(1000, 9999);
$random = mt_rand();

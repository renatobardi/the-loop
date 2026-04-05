<?php
// Bad: Unsafe deserialization

// php-security-003: unserialize() with untrusted input
$data = $_GET['data'];
$object = unserialize($data);

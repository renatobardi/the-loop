<?php
// Bad: Command injection

$cmd = $_GET['cmd'];

// php-injection-003: system() with unsanitized input
system($cmd);
exec($cmd);
shell_exec($cmd);
passthru($cmd);

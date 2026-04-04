// BAD: js-injection-001 — SQL via string interpolation
// ruleid: js-injection-001
const userId = req.params.id;
db.query(`SELECT * FROM users WHERE id = ${userId}`);

// BAD: js-injection-001 — SQL via string concatenation
// ruleid: js-injection-001
db.query("SELECT * FROM users WHERE name = " + userName);

// BAD: js-injection-002 — eval with external input
// ruleid: js-injection-002
eval(req.body.code);

// BAD: js-injection-003 — innerHTML with user data
// ruleid: js-injection-003
const el = document.getElementById('output');
el.innerHTML = userInput;

// BAD: js-injection-004 — exec with template literal
// ruleid: js-injection-004
const { exec } = require('child_process');
exec(`ls ${userInput}`);

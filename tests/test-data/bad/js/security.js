const jwt = require('jsonwebtoken');
const cors = require('cors');
const express = require('express');
const app = express();

// BAD: js-security-001 — JWT with hardcoded secret
// ruleid: js-security-001
const token = jwt.sign({ userId: 123 }, 'mysecret');

// BAD: js-security-001 — JWT verify with hardcoded secret
// ruleid: js-security-001
jwt.verify(token, 'hardcoded-secret-key');

// BAD: js-security-002 — CORS wildcard
// ruleid: js-security-002
app.use(cors({ origin: '*' }));

// BAD: js-security-003 — TLS verification disabled
// ruleid: js-security-003
process.env.NODE_TLS_REJECT_UNAUTHORIZED = '0';

// BAD: js-security-004 — prototype pollution
// ruleid: js-security-004
const config = Object.assign({}, req.body);

const crypto = require('crypto');
const { execFile } = require('child_process');
const jwt = require('jsonwebtoken');
const cors = require('cors');
const express = require('express');
const app = express();

// GOOD: parametrized SQL query
db.query('SELECT * FROM users WHERE id = ?', [userId]);
db.execute('SELECT * FROM orders WHERE user_id = $1', [userId]);

// GOOD: safe JSON parsing, no eval
const data = JSON.parse(req.body.payload);

// GOOD: textContent instead of innerHTML
el.textContent = userInput;

// GOOD: execFile with argument array
execFile('ls', ['-la', safeDirectory], callback);

// GOOD: SHA-256 hash
const hash = crypto.createHash('sha256').update(data).digest('hex');

// GOOD: cryptographic random token
const token = crypto.randomBytes(32).toString('hex');

// GOOD: JWT secret from environment variable
const jwtToken = jwt.sign({ userId: 123 }, process.env.JWT_SECRET);

// GOOD: CORS with explicit origin
app.use(cors({ origin: 'https://app.example.com' }));

// GOOD: explicit field extraction (no prototype pollution)
const config = { name: req.body.name, role: req.body.role };

// GOOD: parallel async with Promise.all
async function processIds(ids) {
  const results = await Promise.all(ids.map(id => fetch('/api/items/' + id)));
  return results;
}

// GOOD: no sensitive data in logs
console.log('User ID:', userId);
console.log('Request processed successfully');

// GOOD: URL from environment
const API_URL = process.env.API_URL;

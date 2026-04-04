const crypto = require('crypto');

// BAD: js-crypto-001 — MD5 hash
// ruleid: js-crypto-001
const hashMd5 = crypto.createHash('md5').update(data).digest('hex');

// BAD: js-crypto-001 — SHA1 hash
// ruleid: js-crypto-001
const hashSha1 = crypto.createHash('sha1').update(data).digest('hex');

// BAD: js-crypto-002 — Math.random for token
// ruleid: js-crypto-002
const token = Math.random().toString(36).substring(2);

// BAD: js-crypto-002 — Math.random for secret
// ruleid: js-crypto-002
const secret = Math.random().toString(36);

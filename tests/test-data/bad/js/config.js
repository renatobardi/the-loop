// BAD: js-config-001 — console.log with sensitive data names
// ruleid: js-config-001
console.log('Password:', password);

// ruleid: js-config-001
console.log('User token:', token);

// ruleid: js-config-001
console.log('API secret:', secret);

// BAD: js-config-002 — hardcoded API URL
// ruleid: js-config-002
const API_URL = 'https://api.myapp.com/v1';

// ruleid: js-config-002
const BASE_URL = 'https://prod.backend.com';

// ruleid: js-config-002
const endpoint = 'https://api.service.io/graphql';

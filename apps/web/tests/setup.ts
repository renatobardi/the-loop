import { vi } from 'vitest';

// Set up environment variables for tests
process.env.PUBLIC_FIREBASE_API_KEY = 'test-api-key';
process.env.PUBLIC_FIREBASE_AUTH_DOMAIN = 'test.firebaseapp.com';
process.env.PUBLIC_FIREBASE_PROJECT_ID = 'test-project';
process.env.PUBLIC_FIREBASE_STORAGE_BUCKET = 'test.firebasestorage.app';
process.env.PUBLIC_FIREBASE_MESSAGING_SENDER_ID = 'test-sender-id';
process.env.PUBLIC_FIREBASE_APP_ID = 'test-app-id';

// Mock SvelteKit's $env/dynamic/public
vi.doMock('$env/dynamic/public', () => ({
	env: {
		PUBLIC_FIREBASE_API_KEY: 'test-api-key',
		PUBLIC_FIREBASE_AUTH_DOMAIN: 'test.firebaseapp.com',
		PUBLIC_FIREBASE_PROJECT_ID: 'test-project',
		PUBLIC_FIREBASE_STORAGE_BUCKET: 'test.firebasestorage.app',
		PUBLIC_FIREBASE_MESSAGING_SENDER_ID: 'test-sender-id',
		PUBLIC_FIREBASE_APP_ID: 'test-app-id',
	},
}));

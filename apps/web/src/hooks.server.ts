import type { Handle } from '@sveltejs/kit';

const HSTS_MAX_AGE = 63_072_000; // 2 years

const csp = [
	"default-src 'self'",
	"script-src 'self' 'unsafe-inline'",
	"style-src 'self' 'unsafe-inline'",
	"img-src 'self' data:",
	"font-src 'self' https://cdn.jsdelivr.net",
	"connect-src 'self' https://theloop-api-1090621437043.us-central1.run.app https://firestore.googleapis.com https://firebase.googleapis.com https://identitytoolkit.googleapis.com https://securetoken.googleapis.com",
	"frame-ancestors 'none'",
	"base-uri 'self'",
	"form-action 'self'",
	"upgrade-insecure-requests"
].join('; ');

export const handle: Handle = async ({ event, resolve }) => {
	const response = await resolve(event);

	response.headers.set(
		'Strict-Transport-Security',
		`max-age=${HSTS_MAX_AGE}; includeSubDomains; preload`
	);
	response.headers.set('X-Frame-Options', 'DENY');
	response.headers.set('X-Content-Type-Options', 'nosniff');
	response.headers.set('Referrer-Policy', 'strict-origin-when-cross-origin');
	response.headers.set(
		'Permissions-Policy',
		'camera=(), microphone=(), geolocation=(), payment=(), usb=()'
	);
	response.headers.set('Content-Security-Policy', csp);
	response.headers.delete('X-Powered-By');

	return response;
};

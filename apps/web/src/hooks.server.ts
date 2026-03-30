import type { Handle } from '@sveltejs/kit';
import { sequence } from '@sveltejs/kit/hooks';
import { i18n } from '$lib/i18n';

const HSTS_MAX_AGE = 63_072_000; // 2 years

const csp = [
	"default-src 'self'",
	"script-src 'self'",
	"style-src 'self' 'unsafe-inline'",
	"img-src 'self' data:",
	"font-src 'self' https://cdn.jsdelivr.net",
	"connect-src 'self' https://firestore.googleapis.com https://firebase.googleapis.com",
	"frame-ancestors 'none'",
	"base-uri 'self'",
	"form-action 'self'",
	"upgrade-insecure-requests"
].join('; ');

const securityHeaders: Handle = async ({ event, resolve }) => {
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

export const handle = sequence(i18n.handle(), securityHeaders);

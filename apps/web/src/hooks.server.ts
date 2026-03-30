import type { Handle } from '@sveltejs/kit';
import { redirect } from '@sveltejs/kit';

const SUPPORTED_LOCALES = ['en', 'pt', 'es'];
const DEFAULT_LOCALE = 'en';
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

export const handle: Handle = async ({ event, resolve }) => {
  const { pathname } = event.url;

  // Root redirect: / → /en/
  if (pathname === '/') {
    throw redirect(301, `/${DEFAULT_LOCALE}/`);
  }

  // Unsupported locale redirect: /fr/anything → /en/anything
  const segments = pathname.split('/').filter(Boolean);
  if (segments.length > 0) {
    const maybeLocale = segments[0];
    if (maybeLocale.length === 2 && !SUPPORTED_LOCALES.includes(maybeLocale)) {
      const rest = segments.slice(1).join('/');
      throw redirect(301, `/${DEFAULT_LOCALE}/${rest}`);
    }
  }

  const response = await resolve(event);

  // Security headers
  response.headers.set('Strict-Transport-Security', `max-age=${HSTS_MAX_AGE}; includeSubDomains; preload`);
  response.headers.set('X-Frame-Options', 'DENY');
  response.headers.set('X-Content-Type-Options', 'nosniff');
  response.headers.set('Referrer-Policy', 'strict-origin-when-cross-origin');
  response.headers.set('Permissions-Policy', 'camera=(), microphone=(), geolocation=(), payment=(), usb=()');
  response.headers.set('Content-Security-Policy', csp);
  response.headers.delete('X-Powered-By');

  return response;
};

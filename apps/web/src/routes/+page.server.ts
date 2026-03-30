import { fail } from '@sveltejs/kit';
import type { Actions } from './$types';
import { WaitlistSchema } from '$lib/server/schemas';
import { waitlistLimiter } from '$lib/server/rateLimiter';
import { addToWaitlist } from '$lib/server/waitlist';

export const actions: Actions = {
  waitlist: async (event) => {
    const ip = event.getClientAddress();

    // Rate limit check
    try {
      await waitlistLimiter.consume(ip);
    } catch {
      return fail(429, { error: 'rate_limited' });
    }

    // Parse form data
    const data = await event.request.formData();
    const raw = { email: data.get('email') };

    // Validate
    const result = WaitlistSchema.safeParse(raw);
    if (!result.success) {
      const errorMsg = result.error.issues[0]?.message ?? 'Invalid input';
      return fail(400, { error: errorMsg });
    }

    const { languageTag } = await import('$lib/paraglide/runtime.js');
    const locale = languageTag();

    // Write to Firestore
    try {
      const status = await addToWaitlist(result.data.email, locale);
      if (status === 'duplicate') {
        return fail(409, { error: 'already_registered' });
      }
      return { success: true };
    } catch {
      return fail(500, { error: 'server_error' });
    }
  }
};

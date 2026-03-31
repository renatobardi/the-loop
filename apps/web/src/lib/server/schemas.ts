import { z } from 'zod';

export const VALID_SOURCES = ['hero', 'cta-bottom', 'constitution'] as const;

export const WaitlistSchema = z.object({
  email: z
    .string({ error: 'Email is required' })
    .trim()
    .toLowerCase()
    .email({ message: 'Please enter a valid email address' })
    .max(254, { message: 'Email address is too long' }),
  source: z
    .string()
    .optional()
    .transform((val) =>
      val && (VALID_SOURCES as readonly string[]).includes(val) ? val : 'unknown'
    )
});

export type WaitlistInput = z.infer<typeof WaitlistSchema>;

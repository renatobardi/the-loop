import { z } from 'zod';

export const WaitlistSchema = z.object({
  email: z
    .string({ error: 'Email is required' })
    .trim()
    .toLowerCase()
    .email({ message: 'Please enter a valid email address' })
    .max(254, { message: 'Email address is too long' })
});

export type WaitlistInput = z.infer<typeof WaitlistSchema>;

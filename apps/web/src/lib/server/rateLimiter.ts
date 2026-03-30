import { RateLimiterMemory } from 'rate-limiter-flexible';

export const waitlistLimiter = new RateLimiterMemory({
  points: 5,
  duration: 60
});

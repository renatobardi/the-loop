import type { ParamMatcher } from '@sveltejs/kit';

const SUPPORTED_LOCALES = ['en', 'pt', 'es'];

export const match: ParamMatcher = (param) => {
  return SUPPORTED_LOCALES.includes(param);
};

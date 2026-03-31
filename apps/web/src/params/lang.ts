import type { ParamMatcher } from '@sveltejs/kit';

const LOCALES = new Set(['en', 'pt', 'es']);

export const match: ParamMatcher = (param) => LOCALES.has(param);

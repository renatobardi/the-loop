import { defineConfig } from 'vitest/config';
import { sveltekit } from '@sveltejs/kit/vite';

export default defineConfig({
	plugins: [sveltekit()],
	test: {
		setupFiles: ['./tests/setup.ts'],
		globals: true,
		environment: 'jsdom',
	},
});

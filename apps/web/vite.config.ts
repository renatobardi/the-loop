import tailwindcss from '@tailwindcss/vite';
import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vitest/config';

export default defineConfig({
	plugins: [tailwindcss(), sveltekit()],
	server: {
		proxy: {
			'/api': {
				target: 'http://localhost:8000',
				changeOrigin: true
			}
		}
	},
	test: {
		include: ['tests/**/*.test.ts'],
		environment: 'jsdom',
		alias: {
			$lib: '/src/lib',
			$app: '/.svelte-kit/types/$app'
		}
	}
});

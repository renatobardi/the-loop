import tailwindcss from '@tailwindcss/vite';
import { sveltekit } from '@sveltejs/kit/vite';
import { paraglide } from '@inlang/paraglide-sveltekit/vite';
import { defineConfig } from 'vitest/config';

export default defineConfig({
	plugins: [tailwindcss(), sveltekit(), paraglide({ project: './project.inlang', outdir: './src/lib/paraglide' })],
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
			'$lib': '/src/lib',
			'$app': '/.svelte-kit/types/$app'
		}
	}
});

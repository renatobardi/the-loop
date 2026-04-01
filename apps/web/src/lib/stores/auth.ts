import { writable, type Readable } from 'svelte/store';
import type { User } from 'firebase/auth';

export const user: Readable<User | null> = (() => {
	const { subscribe, set } = writable<User | null>(null);

	if (typeof window !== 'undefined') {
		// Only run in browser
		import('$lib/firebase').then(({ onAuthChange }) => {
			onAuthChange((newUser) => {
				set(newUser);
			});
		});
	}

	return { subscribe };
})();

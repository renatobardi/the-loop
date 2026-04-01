import { writable, type Readable } from 'svelte/store';
import type { User } from 'firebase/auth';
import { onAuthChange } from '$lib/firebase';

export const user: Readable<User | null> = (() => {
	const { subscribe, set } = writable<User | null>(null);

	if (typeof window !== 'undefined') {
		onAuthChange((newUser) => {
			set(newUser);
		});
	}

	return { subscribe };
})();

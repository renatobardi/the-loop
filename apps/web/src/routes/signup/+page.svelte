<script lang="ts">
	import { goto } from '$app/navigation';
	import { signupWithEmail } from '$lib/firebase';
	import { Button } from '$lib/ui';

	let email = $state('');
	let password = $state('');
	let confirmPassword = $state('');
	let error = $state('');
	let loading = $state(false);

	async function handleSignup() {
		error = '';

		// Validate
		if (!email || !password || !confirmPassword) {
			error = 'All fields are required';
			return;
		}

		if (password !== confirmPassword) {
			error = 'Passwords do not match';
			return;
		}

		if (password.length < 6) {
			error = 'Password must be at least 6 characters';
			return;
		}

		loading = true;

		try {
			await signupWithEmail(email, password);
			await goto('/incidents/');
		} catch (err) {
			const message = err instanceof Error ? err.message : 'Signup failed';
			error = message.includes('auth/email-already-in-use')
				? 'Email already in use'
				: message.includes('auth/invalid-email')
					? 'Invalid email'
					: message.includes('auth/weak-password')
						? 'Password is too weak'
						: message;
		} finally {
			loading = false;
		}
	}
</script>

<div class="flex min-h-screen items-center justify-center bg-bg px-4">
	<div class="w-full max-w-md space-y-6">
		<div class="text-center">
			<h1 class="text-3xl font-bold text-text">Create Account</h1>
			<p class="mt-2 text-text-muted">Sign up to start using The Loop</p>
		</div>

		<form
			onsubmit={(e) => {
				e.preventDefault();
				handleSignup();
			}}
			class="space-y-4"
		>
			<div class="space-y-2">
				<label for="email" class="block text-sm font-medium text-text">Email</label>
				<input
					type="email"
					id="email"
					bind:value={email}
					required
					disabled={loading}
					class="w-full rounded border border-gray-300 px-4 py-2 text-text placeholder-text-muted focus:border-accent focus:outline-none focus:ring-1 focus:ring-accent disabled:opacity-50"
					placeholder="you@example.com"
				/>
			</div>

			<div class="space-y-2">
				<label for="password" class="block text-sm font-medium text-text">Password</label>
				<input
					type="password"
					id="password"
					bind:value={password}
					required
					disabled={loading}
					class="w-full rounded border border-gray-300 px-4 py-2 text-text placeholder-text-muted focus:border-accent focus:outline-none focus:ring-1 focus:ring-accent disabled:opacity-50"
					placeholder="••••••••"
				/>
			</div>

			<div class="space-y-2">
				<label for="confirmPassword" class="block text-sm font-medium text-text">Confirm Password</label>
				<input
					type="password"
					id="confirmPassword"
					bind:value={confirmPassword}
					required
					disabled={loading}
					class="w-full rounded border border-gray-300 px-4 py-2 text-text placeholder-text-muted focus:border-accent focus:outline-none focus:ring-1 focus:ring-accent disabled:opacity-50"
					placeholder="••••••••"
				/>
			</div>

			{#if error}
				<div class="rounded bg-red-50 p-3 text-sm text-red-700">{error}</div>
			{/if}

			<Button
				type="submit"
				disabled={loading || !email || !password || !confirmPassword}
				class="w-full"
			>
				{loading ? 'Creating account...' : 'Sign Up'}
			</Button>
		</form>

		<p class="text-center text-sm text-text-muted">
			Already have an account?
			<a href="/login/" class="text-accent hover:underline">Sign in</a>
		</p>
	</div>
</div>

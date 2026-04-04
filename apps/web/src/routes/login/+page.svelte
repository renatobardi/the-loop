<script lang="ts">
	import { goto } from '$app/navigation';
	import { loginWithEmail } from '$lib/firebase';
	import { Button } from '$lib/ui';

	let email = $state('');
	let password = $state('');
	let error = $state('');
	let loading = $state(false);

	async function handleLogin() {
		error = '';
		loading = true;

		try {
			await loginWithEmail(email, password);
			await goto('/dashboard/');
		} catch (err) {
			const message = err instanceof Error ? err.message : 'Login failed';
			error = message.includes('auth/user-not-found')
				? 'User not found'
				: message.includes('auth/wrong-password')
					? 'Incorrect password'
					: message.includes('auth/invalid-email')
						? 'Invalid email'
						: message;
		} finally {
			loading = false;
		}
	}
</script>

<div class="flex min-h-screen items-center justify-center bg-bg px-4">
	<div class="w-full max-w-md space-y-6">
		<div class="text-center">
			<h1 class="text-3xl font-bold text-text">Login</h1>
			<p class="mt-2 text-text-muted">Sign in to access incidents</p>
		</div>

		<form
			onsubmit={(e) => {
				e.preventDefault();
				handleLogin();
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

			{#if error}
				<div class="rounded bg-red-50 p-3 text-sm text-red-700">{error}</div>
			{/if}

			<Button
				type="submit"
				disabled={loading || !email || !password}
				class="w-full"
			>
				{loading ? 'Signing in...' : 'Sign In'}
			</Button>
		</form>

		<p class="text-center text-sm text-text-muted">
			Don't have an account?
			<a href="/signup/" class="text-accent hover:underline">Sign up</a>
		</p>
	</div>
</div>

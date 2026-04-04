<script lang="ts">
	import { Container, Tabs, Input, Button, Badge } from '$lib/ui';
	import { user } from '$lib/stores/auth';
	import { profile, loadProfile } from '$lib/stores/profile';
	import { updateMe } from '$lib/services/users';
	import {
		sendEmailVerification,
		updatePassword,
		EmailAuthProvider,
		reauthenticateWithCredential
	} from 'firebase/auth';

	const TABS = [
		{ id: 'profile', label: 'Profile' },
		{ id: 'security', label: 'Security' },
		{ id: 'plan', label: 'Plan' }
	];

	let activeTab = $state('profile');

	// Profile tab
	let displayName = $state($profile?.display_name ?? '');
	let jobTitle = $state($profile?.job_title ?? '');
	let profileMessage = $state<{ type: 'success' | 'error'; text: string } | null>(null);
	let profileSaving = $state(false);

	$effect(() => {
		if ($profile) {
			displayName = $profile.display_name ?? '';
			jobTitle = $profile.job_title ?? '';
		}
	});

	async function handleSaveProfile() {
		profileMessage = null;
		profileSaving = true;
		try {
			const patch: Record<string, unknown> = {};
			if (displayName.trim() !== ($profile?.display_name ?? '')) {
				patch.display_name = displayName.trim() || undefined;
			}
			if (jobTitle !== ($profile?.job_title ?? '')) patch.job_title = jobTitle || null;
			await updateMe(patch);
			await loadProfile();
			profileMessage = { type: 'success', text: 'Profile updated successfully.' };
		} catch {
			profileMessage = { type: 'error', text: 'Failed to save. Please try again.' };
		} finally {
			profileSaving = false;
		}
	}

	// Security tab
	let verificationSent = $state(false);
	let currentPassword = $state('');
	let newPassword = $state('');
	let confirmPassword = $state('');
	let securityMessage = $state<{ type: 'success' | 'error'; text: string } | null>(null);
	let securitySaving = $state(false);

	async function handleSendVerification() {
		const authUser = $user;
		if (!authUser) return;
		try {
			await sendEmailVerification(authUser);
			verificationSent = true;
		} catch {
			securityMessage = { type: 'error', text: 'Failed to send verification email.' };
		}
	}

	async function handleChangePassword() {
		securityMessage = null;
		if (newPassword !== confirmPassword) {
			securityMessage = { type: 'error', text: 'Passwords do not match.' };
			return;
		}
		const authUser = $user;
		if (!authUser || !authUser.email) return;
		securitySaving = true;
		try {
			const credential = EmailAuthProvider.credential(authUser.email, currentPassword);
			await reauthenticateWithCredential(authUser, credential);
			await updatePassword(authUser, newPassword);
			securityMessage = { type: 'success', text: 'Password changed successfully.' };
			currentPassword = '';
			newPassword = '';
			confirmPassword = '';
		} catch (err) {
			const code = (err as { code?: string })?.code ?? '';
			if (code === 'auth/wrong-password') {
				securityMessage = { type: 'error', text: 'Current password is incorrect.' };
			} else if (code === 'auth/weak-password') {
				securityMessage = { type: 'error', text: 'New password is too weak (minimum 6 characters).' };
			} else if (code === 'auth/requires-recent-login') {
				securityMessage = { type: 'error', text: 'Please sign in again before changing your password.' };
			} else {
				securityMessage = { type: 'error', text: 'Failed to change password.' };
			}
		} finally {
			securitySaving = false;
		}
	}

	// Plan tab
	const memberSince = $derived.by(() => {
		const date = $profile?.created_at;
		if (!date) return '—';
		return new Intl.DateTimeFormat('en-US', { dateStyle: 'long' }).format(new Date(date));
	});
</script>

<Container>
	<div class="py-8">
		<div class="mb-6">
			<h1 class="text-2xl font-bold text-text">Settings</h1>
			<p class="mt-1 text-sm text-text-muted">Manage your account and preferences</p>
		</div>

		<Tabs tabs={TABS} bind:active={activeTab} />

		<div class="mt-6">
			{#if activeTab === 'profile'}
				<div class="max-w-md space-y-4">
					<div>
						<label for="display-name" class="mb-1 block text-sm font-medium text-text">
							Display name
						</label>
						<Input id="display-name" bind:value={displayName} placeholder="Your name" />
					</div>
					<div>
						<label for="job-title" class="mb-1 block text-sm font-medium text-text">
							Job title
						</label>
						<Input id="job-title" bind:value={jobTitle} placeholder="Ex: Software Engineer" />
					</div>
					<div>
						<p class="mb-1 text-sm font-medium text-text">Email</p>
						<p class="text-sm text-text-muted">{$user?.email ?? ''}</p>
					</div>
					{#if profileMessage}
						<p
							class="text-sm {profileMessage.type === 'success' ? 'text-success' : 'text-error'}"
							role="alert"
						>
							{profileMessage.text}
						</p>
					{/if}
					<Button onclick={handleSaveProfile} disabled={profileSaving}>
						{profileSaving ? 'Saving…' : 'Save'}
					</Button>
				</div>

			{:else if activeTab === 'security'}
				<div class="max-w-md space-y-6">
					<div>
						<p class="mb-2 text-sm font-medium text-text">Email verification</p>
						<div class="flex items-center gap-3">
							{#if $user?.emailVerified}
								<Badge variant="success">Verified ✓</Badge>
							{:else}
								<Badge variant="error">Not verified</Badge>
								<button
									onclick={handleSendVerification}
									disabled={verificationSent}
									class="text-sm text-accent hover:underline disabled:opacity-50"
								>
									{verificationSent ? 'Email sent' : 'Resend verification'}
								</button>
							{/if}
						</div>
					</div>

					<div class="space-y-3">
						<p class="text-sm font-medium text-text">Change password</p>
						<div>
							<label for="current-password" class="mb-1 block text-xs text-text-muted">
								Current password
							</label>
							<Input
								id="current-password"
								type="password"
								bind:value={currentPassword}
								placeholder="••••••••"
							/>
						</div>
						<div>
							<label for="new-password" class="mb-1 block text-xs text-text-muted">
								New password
							</label>
							<Input
								id="new-password"
								type="password"
								bind:value={newPassword}
								placeholder="••••••••"
							/>
						</div>
						<div>
							<label for="confirm-password" class="mb-1 block text-xs text-text-muted">
								Confirm new password
							</label>
							<Input
								id="confirm-password"
								type="password"
								bind:value={confirmPassword}
								placeholder="••••••••"
							/>
						</div>
						{#if securityMessage}
							<p
								class="text-sm {securityMessage.type === 'success' ? 'text-success' : 'text-error'}"
								role="alert"
								aria-describedby="security-message"
							>
								{securityMessage.text}
							</p>
						{/if}
						<Button onclick={handleChangePassword} disabled={securitySaving}>
							{securitySaving ? 'Saving…' : 'Change password'}
						</Button>
					</div>
				</div>

			{:else if activeTab === 'plan'}
				<div class="max-w-md space-y-4">
					<div>
						<p class="mb-2 text-sm font-medium text-text">Current plan</p>
						<Badge>{$profile?.plan ?? 'beta'}</Badge>
					</div>
					<div>
						<p class="mb-1 text-sm font-medium text-text">Member since</p>
						<p class="text-sm text-text-muted">{memberSince}</p>
					</div>
					<a
						href="mailto:loop@oute.pro"
						class="inline-block rounded-lg px-6 py-3 font-semibold transition-colors bg-bg-surface border border-border text-text hover:border-border-hover"
					>
						Contact our team
					</a>
				</div>
			{/if}
		</div>
	</div>
</Container>

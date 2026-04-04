<script lang="ts">
	import { Container, Tabs, Input, Button, Badge } from '$lib/ui';
	import { user } from '$lib/stores/auth';
	import { profile, loadProfile } from '$lib/stores/profile';
	import { updateMe } from '$lib/services/users';
	import {
		listApiKeys,
		createApiKey,
		revokeApiKey,
		getWhitelist,
		addToWhitelist,
		removeFromWhitelist
	} from '$lib/services/api_keys';
	import { generateWorkflowYaml } from '$lib/utils/workflow-generator';
	import type { ApiKey, CreateApiKeyResponse } from '$lib/types/api_keys';
	import {
		sendEmailVerification,
		updatePassword,
		EmailAuthProvider,
		reauthenticateWithCredential
	} from 'firebase/auth';

	const TABS = [
		{ id: 'profile', label: 'Profile' },
		{ id: 'security', label: 'Security' },
		{ id: 'plan', label: 'Plan' },
		{ id: 'api-keys', label: 'API Keys' },
		{ id: 'onboarding', label: 'Onboarding' }
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

	// API Keys tab
	let apiKeys = $state<ApiKey[]>([]);
	let apiKeysLoading = $state(false);
	let apiKeysError = $state<string | null>(null);
	let newKeyName = $state('');
	let creatingKey = $state(false);
	let createKeyError = $state<string | null>(null);
	let newlyCreatedKey = $state<CreateApiKeyResponse | null>(null);
	let revokeConfirmId = $state<string | null>(null);
	let whitelistMap = $state<Record<string, string[]>>({});
	let whitelistInput = $state<Record<string, string>>({});
	let expandedWhitelist = $state<Record<string, boolean>>({});

	$effect(() => {
		if (activeTab === 'api-keys' && apiKeys.length === 0 && !apiKeysLoading) {
			loadApiKeys();
		}
	});

	async function loadApiKeys() {
		apiKeysLoading = true;
		apiKeysError = null;
		try {
			apiKeys = await listApiKeys();
		} catch (err: unknown) {
			apiKeysError = err instanceof Error ? err.message : 'Failed to load API keys';
		} finally {
			apiKeysLoading = false;
		}
	}

	async function handleCreateKey() {
		createKeyError = null;
		if (!newKeyName.trim()) {
			createKeyError = 'Key name is required.';
			return;
		}
		creatingKey = true;
		try {
			const created = await createApiKey(newKeyName.trim());
			newlyCreatedKey = created;
			newKeyName = '';
			apiKeys = await listApiKeys();
		} catch (err: unknown) {
			createKeyError = err instanceof Error ? err.message : 'Failed to create key';
		} finally {
			creatingKey = false;
		}
	}

	async function handleRevokeKey(id: string) {
		if (revokeConfirmId !== id) {
			revokeConfirmId = id;
			return;
		}
		revokeConfirmId = null;
		try {
			await revokeApiKey(id);
			apiKeys = await listApiKeys();
		} catch {
			apiKeysError = 'Failed to revoke key.';
		}
	}

	async function handleLoadWhitelist(keyId: string) {
		try {
			const data = await getWhitelist(keyId);
			whitelistMap = { ...whitelistMap, [keyId]: data.rule_ids };
		} catch {
			// ignore
		}
	}

	async function handleAddWhitelist(keyId: string) {
		const ruleId = (whitelistInput[keyId] ?? '').trim();
		if (!ruleId) return;
		try {
			await addToWhitelist(keyId, ruleId);
			whitelistInput = { ...whitelistInput, [keyId]: '' };
			await handleLoadWhitelist(keyId);
		} catch {
			// ignore
		}
	}

	async function handleRemoveWhitelist(keyId: string, ruleId: string) {
		try {
			await removeFromWhitelist(keyId, ruleId);
			await handleLoadWhitelist(keyId);
		} catch {
			// ignore
		}
	}

	function toggleWhitelist(keyId: string) {
		expandedWhitelist = { ...expandedWhitelist, [keyId]: !expandedWhitelist[keyId] };
		if (expandedWhitelist[keyId] && !whitelistMap[keyId]) {
			handleLoadWhitelist(keyId);
		}
	}

	function copyToClipboard(text: string) {
		navigator.clipboard.writeText(text).catch(() => {});
	}

	// Onboarding tab
	let selectedKeyId = $state('');
	const selectedKey = $derived(apiKeys.find((k) => k.id === selectedKeyId));
	const workflowYaml = $derived(
		selectedKey ? generateWorkflowYaml(selectedKey.prefix + '…') : ''
	);
	let copied = $state(false);

	$effect(() => {
		if (activeTab === 'onboarding' && apiKeys.length === 0 && !apiKeysLoading) {
			loadApiKeys();
		}
	});

	function handleCopyYaml() {
		copyToClipboard(workflowYaml);
		copied = true;
		setTimeout(() => (copied = false), 2000);
	}
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

			{:else if activeTab === 'api-keys'}
				<div class="max-w-lg space-y-6">
					<!-- Create new key -->
					<div>
						<p class="mb-2 text-sm font-medium text-text">New API Key</p>
						<div class="flex gap-2">
							<Input bind:value={newKeyName} placeholder="Key name (e.g. ci-production)" />
							<Button onclick={handleCreateKey} disabled={creatingKey}>
								{creatingKey ? 'Creating…' : 'Create'}
							</Button>
						</div>
						{#if createKeyError}
							<p class="text-sm text-error mt-1" role="alert">{createKeyError}</p>
						{/if}
					</div>

					<!-- One-time token display -->
					{#if newlyCreatedKey}
						<div class="rounded-lg border border-warning/30 bg-warning/5 p-4 space-y-2">
							<p class="text-sm font-semibold text-warning">Save this token now — it won't be shown again</p>
							<code class="block break-all font-mono text-xs text-text bg-bg-elevated p-2 rounded">
								{newlyCreatedKey.token}
							</code>
							<div class="flex gap-2">
								<button
									onclick={() => copyToClipboard(newlyCreatedKey!.token)}
									class="text-xs text-accent hover:underline"
								>
									Copy to clipboard
								</button>
								<button
									onclick={() => (newlyCreatedKey = null)}
									class="text-xs text-text-muted hover:underline"
								>
									Dismiss
								</button>
							</div>
						</div>
					{/if}

					<!-- Keys list -->
					{#if apiKeysLoading}
						<p class="text-sm text-text-muted">Loading keys…</p>
					{:else if apiKeysError}
						<p class="text-sm text-error" role="alert">{apiKeysError}</p>
					{:else if apiKeys.length === 0}
						<p class="text-sm text-text-muted">No API keys yet.</p>
					{:else}
						<div class="space-y-3">
							{#each apiKeys as key}
								<div class="rounded-lg border border-border bg-bg-surface p-4">
									<div class="flex items-start justify-between gap-2">
										<div>
											<p class="text-sm font-semibold text-text">{key.name}</p>
											<p class="font-mono text-xs text-text-muted mt-0.5">{key.prefix}…</p>
											<p class="text-xs text-text-muted mt-0.5">
												Created {new Intl.DateTimeFormat('en-US', { dateStyle: 'medium' }).format(new Date(key.created_at))}
												{#if key.last_used_at}
													· Last used {new Intl.DateTimeFormat('en-US', { dateStyle: 'medium' }).format(new Date(key.last_used_at))}
												{/if}
											</p>
											{#if key.revoked_at}
												<Badge variant="error">Revoked</Badge>
											{/if}
										</div>
										{#if !key.revoked_at}
											<button
												onclick={() => handleRevokeKey(key.id)}
												class="shrink-0 text-xs text-error hover:underline"
											>
												{revokeConfirmId === key.id ? 'Confirm revoke?' : 'Revoke'}
											</button>
										{/if}
									</div>

									<!-- Whitelist toggle -->
									{#if !key.revoked_at}
										<div class="mt-3 border-t border-border pt-3">
											<button
												onclick={() => toggleWhitelist(key.id)}
												class="text-xs text-text-muted hover:text-text"
											>
												{expandedWhitelist[key.id] ? '▾' : '▸'} Rule whitelist
											</button>
											{#if expandedWhitelist[key.id]}
												<div class="mt-2 space-y-1">
													{#if whitelistMap[key.id]?.length}
														{#each whitelistMap[key.id] as ruleId}
															<div class="flex items-center justify-between">
																<span class="font-mono text-xs text-text">{ruleId}</span>
																<button
																	onclick={() => handleRemoveWhitelist(key.id, ruleId)}
																	class="text-xs text-error hover:underline"
																>
																	Remove
																</button>
															</div>
														{/each}
													{:else}
														<p class="text-xs text-text-muted">No rules whitelisted.</p>
													{/if}
													<div class="flex gap-2 mt-2">
														<input
															type="text"
															bind:value={whitelistInput[key.id]}
															placeholder="rule-id"
															class="flex-1 rounded border border-border bg-bg-elevated px-2 py-1 text-xs text-text placeholder:text-text-muted focus:border-accent focus:outline-none"
														/>
														<button
															onclick={() => handleAddWhitelist(key.id)}
															class="rounded bg-bg-elevated border border-border px-2 py-1 text-xs text-text hover:border-border-hover"
														>
															Add
														</button>
													</div>
												</div>
											{/if}
										</div>
									{/if}
								</div>
							{/each}
						</div>
					{/if}
				</div>

			{:else if activeTab === 'onboarding'}
				<div class="max-w-2xl space-y-6">
					<div>
						<h2 class="text-lg font-semibold text-text">Set up The Loop Incident Guard</h2>
						<p class="text-sm text-text-muted mt-1">
							Add the GitHub Actions workflow to your repository to start scanning pull requests.
						</p>
					</div>

					<!-- Step 1: Select key -->
					<div>
						<p class="text-sm font-medium text-text mb-2">Step 1 — Select an API key</p>
						{#if apiKeys.filter((k) => !k.revoked_at).length === 0}
							<p class="text-sm text-text-muted">
								No active API keys. Create one in the <button
									onclick={() => (activeTab = 'api-keys')}
									class="text-accent hover:underline">API Keys tab</button
								>.
							</p>
						{:else}
							<select
								bind:value={selectedKeyId}
								class="rounded-md border border-border bg-bg-elevated px-3 py-2 text-sm text-text focus:border-accent focus:outline-none"
							>
								<option value="">— Select a key —</option>
								{#each apiKeys.filter((k) => !k.revoked_at) as key}
									<option value={key.id}>{key.name} ({key.prefix}…)</option>
								{/each}
							</select>
						{/if}
					</div>

					<!-- Step 2: Add secret -->
					{#if selectedKey}
						<div class="rounded-lg border border-border bg-bg-surface p-4 space-y-2">
							<p class="text-sm font-medium text-text">Step 2 — Add repository secret</p>
							<p class="text-sm text-text-muted">
								Go to your repository → Settings → Secrets → Actions → New repository secret
							</p>
							<div class="flex items-center gap-3 mt-1">
								<div>
									<p class="text-xs text-text-muted">Name</p>
									<code class="font-mono text-sm text-text">THELOOP_API_TOKEN</code>
								</div>
								<div>
									<p class="text-xs text-text-muted">Value</p>
									<p class="text-sm text-text-muted italic">Your full API token (from creation)</p>
								</div>
							</div>
						</div>

						<!-- Step 3: Workflow YAML -->
						<div>
							<div class="flex items-center justify-between mb-2">
								<p class="text-sm font-medium text-text">
									Step 3 — Add workflow file
									<span class="font-mono text-xs text-text-muted ml-1">
										.github/workflows/theloop-guard.yml
									</span>
								</p>
								<button
									onclick={handleCopyYaml}
									class="text-xs text-accent hover:underline"
								>
									{copied ? 'Copied!' : 'Copy to clipboard'}
								</button>
							</div>
							<pre class="overflow-x-auto rounded-lg border border-border bg-bg-elevated p-4 text-xs font-mono text-text leading-relaxed">{workflowYaml}</pre>
						</div>
					{/if}
				</div>
			{/if}
		</div>
	</div>
</Container>

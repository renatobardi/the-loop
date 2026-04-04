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
			if (displayName.trim()) patch.display_name = displayName.trim();
			if (jobTitle !== ($profile?.job_title ?? '')) patch.job_title = jobTitle || null;
			await updateMe(patch);
			await loadProfile();
			profileMessage = { type: 'success', text: 'Perfil atualizado com sucesso.' };
		} catch {
			profileMessage = { type: 'error', text: 'Erro ao salvar. Tente novamente.' };
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
			securityMessage = { type: 'error', text: 'Erro ao enviar verificação.' };
		}
	}

	async function handleChangePassword() {
		securityMessage = null;
		if (newPassword !== confirmPassword) {
			securityMessage = { type: 'error', text: 'As senhas não coincidem.' };
			return;
		}
		const authUser = $user;
		if (!authUser || !authUser.email) return;
		securitySaving = true;
		try {
			const credential = EmailAuthProvider.credential(authUser.email, currentPassword);
			await reauthenticateWithCredential(authUser, credential);
			await updatePassword(authUser, newPassword);
			securityMessage = { type: 'success', text: 'Senha alterada com sucesso.' };
			currentPassword = '';
			newPassword = '';
			confirmPassword = '';
		} catch (err) {
			const code = (err as { code?: string })?.code ?? '';
			if (code === 'auth/wrong-password') {
				securityMessage = { type: 'error', text: 'Senha atual incorreta.' };
			} else if (code === 'auth/weak-password') {
				securityMessage = { type: 'error', text: 'Nova senha muito fraca (mínimo 6 caracteres).' };
			} else if (code === 'auth/requires-recent-login') {
				securityMessage = { type: 'error', text: 'Faça login novamente antes de alterar a senha.' };
			} else {
				securityMessage = { type: 'error', text: 'Erro ao alterar senha.' };
			}
		} finally {
			securitySaving = false;
		}
	}

	// Plan tab
	const memberSince = $derived.by(() => {
		const date = $profile?.created_at;
		if (!date) return '—';
		return new Intl.DateTimeFormat('pt-BR', { dateStyle: 'long' }).format(new Date(date));
	});
</script>

<Container>
	<div class="py-8">
		<div class="mb-6">
			<h1 class="text-2xl font-bold text-text">Configurações</h1>
			<p class="mt-1 text-sm text-text-muted">Gerencie sua conta e preferências</p>
		</div>

		<Tabs tabs={TABS} bind:active={activeTab} />

		<div class="mt-6">
			{#if activeTab === 'profile'}
				<div class="max-w-md space-y-4">
					<div>
						<label for="display-name" class="mb-1 block text-sm font-medium text-text">
							Nome de exibição
						</label>
						<Input id="display-name" bind:value={displayName} placeholder="Seu nome" />
					</div>
					<div>
						<label for="job-title" class="mb-1 block text-sm font-medium text-text">
							Cargo
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
						{profileSaving ? 'Salvando…' : 'Salvar'}
					</Button>
				</div>

			{:else if activeTab === 'security'}
				<div class="max-w-md space-y-6">
					<div>
						<p class="mb-2 text-sm font-medium text-text">Verificação de email</p>
						<div class="flex items-center gap-3">
							{#if $user?.emailVerified}
								<Badge variant="success">Verificado ✓</Badge>
							{:else}
								<Badge variant="error">Não verificado</Badge>
								<button
									onclick={handleSendVerification}
									disabled={verificationSent}
									class="text-sm text-accent hover:underline disabled:opacity-50"
								>
									{verificationSent ? 'Email enviado' : 'Reenviar verificação'}
								</button>
							{/if}
						</div>
					</div>

					<div class="space-y-3">
						<p class="text-sm font-medium text-text">Alterar senha</p>
						<div>
							<label for="current-password" class="mb-1 block text-xs text-text-muted">
								Senha atual
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
								Nova senha
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
								Confirmar nova senha
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
							{securitySaving ? 'Salvando…' : 'Alterar senha'}
						</Button>
					</div>
				</div>

			{:else if activeTab === 'plan'}
				<div class="max-w-md space-y-4">
					<div>
						<p class="mb-2 text-sm font-medium text-text">Plano atual</p>
						<Badge>{$profile?.plan ?? 'beta'}</Badge>
					</div>
					<div>
						<p class="mb-1 text-sm font-medium text-text">Membro desde</p>
						<p class="text-sm text-text-muted">{memberSince}</p>
					</div>
					<a
						href="mailto:loop@oute.pro"
						class="inline-block rounded-lg px-6 py-3 font-semibold transition-colors bg-bg-surface border border-border text-text hover:border-border-hover"
					>
						Falar com a equipe
					</a>
				</div>
			{/if}
		</div>
	</div>
</Container>

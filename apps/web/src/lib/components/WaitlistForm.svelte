<script lang="ts">
  import { enhance } from '$app/forms';
  import { Input, Button } from '$lib/ui';

  let {
    action = '?/waitlist',
  }: {
    action?: string;
  } = $props();

  let status: 'idle' | 'submitting' | 'success' | 'error' | 'duplicate' | 'rate_limited' = $state('idle');
  let errorMessage = $state('');
</script>

<form
  method="POST"
  {action}
  use:enhance={() => {
    status = 'submitting';

    return async ({ result }) => {
      if (result.type === 'success') {
        status = 'success';
      } else if (result.type === 'failure') {
        const error = (result.data as Record<string, string> | undefined)?.error;
        if (error === 'rate_limited') {
          status = 'rate_limited';
        } else if (error === 'already_registered') {
          status = 'duplicate';
        } else {
          status = 'error';
          errorMessage = error ?? 'Something went wrong. Please try again.';
        }
      } else {
        status = 'error';
        errorMessage = 'Something went wrong. Please try again.';
      }
    };
  }}
>
  {#if status === 'success'}
    <p class="text-accent text-sm font-medium">
      You're on the list! We'll notify you when The Loop launches.
    </p>
  {:else}
    <div class="flex flex-col sm:flex-row gap-3">
      <div class="flex-1">
        <Input
          type="email"
          name="email"
          placeholder="your@email.com"
          required
          disabled={status === 'submitting'}
        />
      </div>
      <Button type="submit" variant="primary" disabled={status === 'submitting'}>
        {#if status === 'submitting'}
          Joining...
        {:else}
          Join the waitlist
        {/if}
      </Button>
    </div>

    {#if status === 'duplicate'}
      <p class="mt-2 text-sm text-text-muted">You're already on the list!</p>
    {:else if status === 'rate_limited'}
      <p class="mt-2 text-sm text-error">Too many attempts. Please try again in a minute.</p>
    {:else if status === 'error'}
      <p class="mt-2 text-sm text-error">{errorMessage}</p>
    {/if}
  {/if}
</form>

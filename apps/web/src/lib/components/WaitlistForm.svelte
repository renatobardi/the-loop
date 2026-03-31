<script lang="ts">
  import { enhance } from '$app/forms';
  import { Input, Button } from '$lib/ui';
  import { form_success, form_duplicate, form_rate_limited, form_server_error, form_submitting, form_submit, hero_email_placeholder, form_email_label } from '$lib/paraglide/messages.js';

  let {
    action = '?/waitlist',
    source = 'unknown',
  }: {
    action?: string;
    source?: string;
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
          errorMessage = error ?? form_server_error();
        }
      } else {
        status = 'error';
        errorMessage = form_server_error();
      }
    };
  }}
>
  {#if status === 'success'}
    <p class="text-accent text-sm font-medium">
      {form_success()}
    </p>
  {:else}
    <input type="hidden" name="source" value={source} />
    <div class="flex flex-col sm:flex-row gap-3">
      <div class="flex-1">
        <Input
          type="email"
          name="email"
          label={form_email_label()}
          placeholder={hero_email_placeholder()}
          required
          disabled={status === 'submitting'}
        />
      </div>
      <Button type="submit" variant="primary" disabled={status === 'submitting'}>
        {#if status === 'submitting'}
          {form_submitting()}
        {:else}
          {form_submit()}
        {/if}
      </Button>
    </div>

    {#if status === 'duplicate'}
      <p class="mt-2 text-sm text-text-muted">{form_duplicate()}</p>
    {:else if status === 'rate_limited'}
      <p class="mt-2 text-sm text-error">{form_rate_limited()}</p>
    {:else if status === 'error'}
      <p class="mt-2 text-sm text-error">{errorMessage}</p>
    {/if}
  {/if}
</form>

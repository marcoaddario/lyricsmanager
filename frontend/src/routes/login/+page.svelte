<script lang="ts">
  import { goto } from '$app/navigation';
  import { user, toasts } from '$lib/stores';
  import { api } from '$lib/services/api';

  let identifier = '';
  let password = '';
  let loading = false;
  let error = '';

  async function handleLogin() {
    if (!identifier || !password) { error = 'Please fill in all fields'; return; }
    loading = true; error = '';
    try {
      await api.auth.login(identifier, password);
      const me = await api.auth.me();
      user.set(me);
      goto('/');
    } catch (e: any) {
      // Handle different error formats
      if (typeof e.message === 'string') {
        error = e.message;
      } else if (e.message && typeof e.message === 'object') {
        error = e.message.detail || e.message.message || 'Login failed';
      } else {
        error = 'Login failed';
      }
    } finally {
      loading = false;
    }
  }
</script>

<svelte:head><title>Sign in — Lyrics Manager</title></svelte:head>

<div class="login-page">
  <div class="login-card">
    <div class="login-logo">🎵</div>
    <h1>Lyrics Manager</h1>
    <p style="color:var(--text2);margin-bottom:2rem;font-size:0.9rem">Sign in to your account</p>

    {#if error}
      <div class="error-msg">{error}</div>
    {/if}

    <div class="field">
      <label for="identifier">Email or Username</label>
      <input id="identifier" class="input" type="text" bind:value={identifier}
        placeholder="you@example.com or username" autocomplete="username"
        on:keydown={e => e.key === 'Enter' && handleLogin()} />
    </div>
    <div class="field">
      <label for="password">Password</label>
      <input id="password" class="input" type="password" bind:value={password}
        placeholder="••••••••" autocomplete="current-password"
        on:keydown={e => e.key === 'Enter' && handleLogin()} />
    </div>

    <button class="btn btn-primary" style="width:100%;justify-content:center;margin-top:0.5rem"
      disabled={loading} on:click={handleLogin}>
      {loading ? 'Signing in…' : 'Sign in'}
    </button>
  </div>
</div>

<style>
  .login-page {
    min-height: 100dvh; display: flex;
    align-items: center; justify-content: center;
    background: var(--bg); padding: 1rem;
  }
  .login-card {
    background: var(--bg2); border: 1px solid var(--border);
    border-radius: 16px; padding: 2.5rem 2rem;
    width: 100%; max-width: 380px;
    text-align: center;
  }
  .login-logo { font-size: 3rem; margin-bottom: 0.5rem; }
  .error-msg {
    background: rgba(248,113,113,0.1); color: var(--error);
    border: 1px solid rgba(248,113,113,0.3); border-radius: 8px;
    padding: 0.65rem 0.9rem; margin-bottom: 1rem;
    font-size: 0.875rem; text-align: left;
  }
  .field { text-align: left; }
</style>

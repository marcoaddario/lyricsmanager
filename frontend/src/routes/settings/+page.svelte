<script lang="ts">
  import { onMount } from 'svelte';
  import { user, theme } from '$lib/stores';
  import { api } from '$lib/services/api';
  import { offlineStore } from '$lib/services/offline';
  import { toasts } from '$lib/stores';

  let pwForm = { current_password: '', new_password: '', confirm: '' };
  let pwSaving = false;
  let pwError = '';

  let storageEst = { usageMB: 0, quotaMB: 0 };
  let cachedSetlists: any[] = [];

  onMount(async () => {
    storageEst = await offlineStore.getStorageEstimate();
    cachedSetlists = await offlineStore.listSetlists();
  });

  async function changePassword() {
    pwError = '';
    if (pwForm.new_password !== pwForm.confirm) { pwError = 'Passwords do not match'; return; }
    if (pwForm.new_password.length < 8) { pwError = 'Password must be at least 8 characters'; return; }
    pwSaving = true;
    try {
      await api.users.changePassword($user.id, {
        current_password: pwForm.current_password,
        new_password: pwForm.new_password
      });
      pwForm = { current_password: '', new_password: '', confirm: '' };
      toasts.add('Password updated', 'success');
    } catch (e: any) { pwError = e.message; }
    finally { pwSaving = false; }
  }

  async function removeOffline(id: number) {
    await offlineStore.deleteSetlist(id);
    cachedSetlists = cachedSetlists.filter(s => s.id !== id);
    storageEst = await offlineStore.getStorageEstimate();
    toasts.add('Removed from device', 'info');
  }

  async function setTheme(t: string) {
    theme.set(t as any);
    try { await api.users.update($user.id, { color_theme: t }); } catch {}
  }
</script>

<svelte:head><title>Settings — Lyrics Manager</title></svelte:head>

<h1 style="margin-bottom:1.5rem">Settings</h1>

<div class="settings-grid">

  <!-- Theme -->
  <div class="card">
    <h3 style="margin-bottom:1rem">🎨 Colour theme</h3>
    <div class="theme-grid">
      {#each ['dark','light','midnight','forest','amber'] as t}
        <button class="theme-btn" class:active={$theme === t}
          data-theme={t} on:click={() => setTheme(t)}>
          <span class="theme-swatch" data-swatch={t}></span>
          <span class="theme-label">{t.charAt(0).toUpperCase() + t.slice(1)}</span>
        </button>
      {/each}
    </div>
  </div>

  <!-- Password -->
  <div class="card">
    <h3 style="margin-bottom:1rem">🔒 Change password</h3>
    {#if pwError}
      <div class="err-box">{pwError}</div>
    {/if}
    <div class="field">
      <label>Current password</label>
      <input class="input" type="password" bind:value={pwForm.current_password} autocomplete="current-password" />
    </div>
    <div class="field">
      <label>New password</label>
      <input class="input" type="password" bind:value={pwForm.new_password} autocomplete="new-password" />
    </div>
    <div class="field">
      <label>Confirm new password</label>
      <input class="input" type="password" bind:value={pwForm.confirm} autocomplete="new-password" />
    </div>
    <button class="btn btn-primary" disabled={pwSaving || !pwForm.current_password || !pwForm.new_password}
      on:click={changePassword}>
      {pwSaving ? 'Saving…' : 'Update password'}
    </button>
  </div>

  <!-- Offline storage -->
  <div class="card" style="grid-column: 1 / -1">
    <h3 style="margin-bottom:1rem">📱 Offline storage</h3>
    <div class="storage-bar-wrap">
      <div class="storage-info">
        <span>{storageEst.usageMB} MB used</span>
        <span style="color:var(--text3)">{storageEst.quotaMB} MB quota</span>
      </div>
      {#if storageEst.quotaMB > 0}
        <div class="storage-bar">
          <div class="storage-fill" style="width:{Math.min(100, storageEst.usageMB / storageEst.quotaMB * 100)}%"></div>
        </div>
      {/if}
    </div>
    <h3 style="margin:1.25rem 0 0.75rem;font-size:0.9rem">Downloaded set lists</h3>
    {#if cachedSetlists.length === 0}
      <p style="color:var(--text3);font-size:0.85rem">No set lists cached. Open a set list and tap "Save offline".</p>
    {:else}
      <div style="display:flex;flex-direction:column;gap:6px">
        {#each cachedSetlists as sl}
          <div class="cached-row">
            <span>{sl.name}</span>
            <span style="color:var(--text3);font-size:0.78rem">
              {new Date(sl.downloadedAt).toLocaleDateString()}
            </span>
            <button class="btn btn-ghost btn-sm" style="color:var(--error);margin-left:auto"
              on:click={() => removeOffline(sl.id)}>Remove</button>
          </div>
        {/each}
      </div>
    {/if}
  </div>

</div>

<style>
  .settings-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
    gap: 1.25rem;
    align-items: start;
  }

  .theme-grid { display: grid; grid-template-columns: repeat(5,1fr); gap: 8px; }
  .theme-btn {
    display: flex; flex-direction: column; align-items: center; gap: 6px;
    padding: 0.6rem; border-radius: 10px;
    background: var(--bg3); border: 2px solid transparent;
    cursor: pointer; transition: all 0.15s;
  }
  .theme-btn.active { border-color: var(--accent); }
  .theme-btn:hover { border-color: var(--border2); }
  .theme-swatch {
    width: 28px; height: 28px; border-radius: 6px; display: block;
  }
  [data-swatch="dark"] { background: #0f0f0f; border: 1px solid #2e2e2e; }
  [data-swatch="light"] { background: #f7f7f5; border: 1px solid #d8d7d2; }
  [data-swatch="midnight"] { background: #070a14; border: 1px solid #1e2b42; }
  [data-swatch="forest"] { background: #080f08; border: 1px solid #1e301e; }
  [data-swatch="amber"] { background: #100c05; border: 1px solid #352a10; }
  .theme-label { font-size: 0.65rem; color: var(--text2); font-weight: 500; }

  .err-box {
    background: rgba(248,113,113,0.1); color: var(--error);
    border: 1px solid rgba(248,113,113,0.3); border-radius: 8px;
    padding: 0.6rem 0.85rem; margin-bottom: 1rem; font-size: 0.85rem;
  }

  .storage-bar-wrap { margin-bottom: 0.5rem; }
  .storage-info { display: flex; justify-content: space-between; font-size: 0.82rem; margin-bottom: 6px; }
  .storage-bar { background: var(--bg3); border-radius: 4px; height: 6px; overflow: hidden; }
  .storage-fill { height: 100%; background: var(--accent); border-radius: 4px; transition: width 0.3s; }

  .cached-row {
    display: flex; align-items: center; gap: 10px;
    background: var(--bg3); border: 1px solid var(--border);
    border-radius: 8px; padding: 0.5rem 0.75rem; font-size: 0.875rem;
  }
</style>

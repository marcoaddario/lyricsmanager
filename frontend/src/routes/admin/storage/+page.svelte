<script lang="ts">
  import { onMount } from 'svelte';
  import { api } from '$lib/services/api';
  import { toasts } from '$lib/stores';

  let info: any = null;
  let loading = true;

  onMount(async () => {
    try { info = await api.admin.storage(); } catch (e: any) { toasts.add(e.message, 'error'); }
    loading = false;
  });

  $: usedPct = info ? Math.min(100, (info.used_mb / info.max_mb) * 100) : 0;
  $: barColor = usedPct > 85 ? 'var(--error)' : usedPct > 60 ? 'var(--warning)' : 'var(--accent)';
</script>

<svelte:head><title>Storage — Admin</title></svelte:head>

<div style="margin-bottom:1.5rem">
  <div style="color:var(--text3);font-size:0.75rem;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:4px">Admin</div>
  <h1>Storage</h1>
</div>

{#if loading}
  <p style="color:var(--text2)">Loading…</p>
{:else if info}
  <div class="stats-row">
    <div class="stat-card">
      <div class="stat-num" style="color:var(--accent)">{info.user_count}</div>
      <div class="stat-label">Users</div>
    </div>
    <div class="stat-card">
      <div class="stat-num" style="color:var(--accent)">{info.library_count}</div>
      <div class="stat-label">Libraries</div>
    </div>
    <div class="stat-card">
      <div class="stat-num" style="color:var(--accent)">{info.song_count}</div>
      <div class="stat-label">Songs</div>
    </div>
    <div class="stat-card">
      <div class="stat-num" style="color:{barColor}">{info.used_mb} MB</div>
      <div class="stat-label">Lyrics storage used</div>
    </div>
  </div>

  <div class="card" style="margin-top:1.5rem">
    <h3 style="margin-bottom:1rem">Storage usage</h3>
    <div style="display:flex;justify-content:space-between;font-size:0.85rem;margin-bottom:8px">
      <span style="color:var(--text2)">{info.used_mb} MB used of {info.max_mb} MB</span>
      <span style="color:var(--text3)">{usedPct.toFixed(1)}%</span>
    </div>
    <div style="background:var(--bg3);border-radius:6px;height:12px;overflow:hidden">
      <div style="height:100%;width:{usedPct}%;background:{barColor};border-radius:6px;transition:width 0.4s"></div>
    </div>
    {#if usedPct > 85}
      <div style="color:var(--error);font-size:0.82rem;margin-top:10px">
        ⚠ Storage is nearly full. Consider increasing MAX_STORAGE_MB or removing unused libraries.
      </div>
    {/if}
  </div>

  <div class="card" style="margin-top:1.25rem">
    <h3 style="margin-bottom:0.75rem">Configuration</h3>
    <p style="color:var(--text2);font-size:0.875rem">
      To change the storage limit, set the <code class="mono" style="background:var(--bg3);padding:2px 6px;border-radius:4px">MAX_STORAGE_MB</code>
      environment variable in your <code class="mono" style="background:var(--bg3);padding:2px 6px;border-radius:4px">.env</code> file and restart the stack.
    </p>
  </div>
{/if}

<style>
  .stats-row { display: grid; grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: 1rem; }
  .stat-card {
    background: var(--bg2); border: 1px solid var(--border);
    border-radius: 10px; padding: 1.25rem;
  }
  .stat-num { font-size: 2rem; font-weight: 700; }
  .stat-label { font-size: 0.8rem; color: var(--text2); margin-top: 4px; }
</style>

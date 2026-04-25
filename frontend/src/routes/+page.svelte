<script lang="ts">
  import { onMount } from 'svelte';
  import { user } from '$lib/stores';
  import { api } from '$lib/services/api';
  import { offlineStore } from '$lib/services/offline';

  let libraries: any[] = [];
  let setlists: any[] = [];
  let offlineSetlists: any[] = [];
  let loading = true;

  onMount(async () => {
    try {
      [libraries, setlists] = await Promise.all([api.libraries.list(), api.setlists.list()]);
    } catch {}
    offlineSetlists = await offlineStore.listSetlists();
    loading = false;
  });
</script>

<svelte:head><title>Dashboard — Lyrics Manager</title></svelte:head>

<div class="page-header">
  <div>
    <h1>Welcome, {$user?.display_name || $user?.username} 👋</h1>
    <p style="color:var(--text2);margin-top:4px">Manage your lyrics and set lists</p>
  </div>
</div>

{#if loading}
  <p style="color:var(--text2)">Loading…</p>
{:else}
  <div class="stats-row">
    <div class="stat-card">
      <div class="stat-num">{libraries.length}</div>
      <div class="stat-label">Libraries</div>
    </div>
    <div class="stat-card">
      <div class="stat-num">{setlists.length}</div>
      <div class="stat-label">Set Lists</div>
    </div>
    <div class="stat-card">
      <div class="stat-num">{offlineSetlists.length}</div>
      <div class="stat-label">Cached offline</div>
    </div>
  </div>

  <div class="section">
    <div class="section-header">
      <h2>Recent set lists</h2>
      <a href="/setlists" class="btn btn-ghost btn-sm">View all</a>
    </div>
    {#if setlists.length === 0}
      <div class="empty-state">
        <div style="font-size:2rem">📋</div>
        <p>No set lists yet. <a href="/setlists">Create one</a></p>
      </div>
    {:else}
      <div class="grid-2">
        {#each setlists.slice(0, 4) as sl}
          <a href="/setlists/{sl.id}" class="card card-hover">
            <div style="display:flex;justify-content:space-between;align-items:flex-start">
              <strong>{sl.name}</strong>
              <span class="badge badge-accent">{sl.song_count} songs</span>
            </div>
            {#if sl.event_date}
              <div style="color:var(--text2);font-size:0.8rem;margin-top:6px">
                📅 {new Date(sl.event_date).toLocaleDateString()}
              </div>
            {/if}
          </a>
        {/each}
      </div>
    {/if}
  </div>

  <div class="section">
    <div class="section-header">
      <h2>Libraries</h2>
      <a href="/libraries" class="btn btn-ghost btn-sm">View all</a>
    </div>
    <div class="grid-2">
      {#each libraries as lib}
        <a href="/libraries/{lib.id}" class="card card-hover">
          <div style="display:flex;justify-content:space-between;align-items:flex-start">
            <strong>{lib.name}</strong>
            {#if lib.is_global}<span class="badge badge-success">global</span>{/if}
          </div>
          <div style="color:var(--text2);font-size:0.8rem;margin-top:4px">{lib.song_count} songs</div>
        </a>
      {/each}
    </div>
  </div>
{/if}

<style>
  .page-header { margin-bottom: 2rem; }
  .stats-row { display: flex; gap: 1rem; margin-bottom: 2rem; flex-wrap: wrap; }
  .stat-card {
    flex: 1; min-width: 120px;
    background: var(--bg2); border: 1px solid var(--border);
    border-radius: 10px; padding: 1.25rem;
  }
  .stat-num { font-size: 2rem; font-weight: 700; color: var(--accent); }
  .stat-label { font-size: 0.8rem; color: var(--text2); margin-top: 2px; }
  .section { margin-bottom: 2rem; }
  .section-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 1rem; }
  .grid-2 { display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 0.75rem; }
  .empty-state {
    text-align: center; padding: 3rem; color: var(--text2);
    background: var(--bg2); border: 1px dashed var(--border);
    border-radius: 10px;
  }
</style>

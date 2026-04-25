<script lang="ts">
  import { onMount } from 'svelte';
  import { api } from '$lib/services/api';
  import { toasts } from '$lib/stores';

  let libraries: any[] = [];
  let loading = true;
  let showCreate = false;
  let form = { name: '', description: '', is_global: false };
  let saving = false;

  onMount(async () => {
    try { libraries = await api.libraries.list(); } catch (e: any) { toasts.add(e.message, 'error'); }
    loading = false;
  });

  async function create() {
    saving = true;
    try {
      const lib = await api.libraries.create(form);
      libraries = [...libraries, lib];
      showCreate = false;
      form = { name: '', description: '', is_global: false };
      toasts.add('Library created', 'success');
    } catch (e: any) { toasts.add(e.message, 'error'); }
    finally { saving = false; }
  }

  async function deleteLib(id: number) {
    if (!confirm('Delete this library and all its songs?')) return;
    try {
      await api.libraries.delete(id);
      libraries = libraries.filter(l => l.id !== id);
      toasts.add('Library deleted', 'success');
    } catch (e: any) { toasts.add(e.message, 'error'); }
  }
</script>

<svelte:head><title>Libraries — Lyrics Manager</title></svelte:head>

<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:1.5rem">
  <h1>Libraries</h1>
  <button class="btn btn-primary" on:click={() => showCreate = !showCreate}>+ New library</button>
</div>

{#if showCreate}
  <div class="card" style="margin-bottom:1.5rem">
    <h3 style="margin-bottom:1rem">New library</h3>
    <div class="field">
      <label>Name *</label>
      <input class="input" bind:value={form.name} placeholder="My songs, Worship repertoire…" />
    </div>
    <div class="field">
      <label>Description</label>
      <input class="input" bind:value={form.description} placeholder="Optional" />
    </div>
    <div style="display:flex;gap:8px;margin-bottom:1rem;align-items:center">
      <input type="checkbox" id="is_global" bind:checked={form.is_global} />
      <label for="is_global" style="color:var(--text2);font-size:0.875rem">Global (shared with all users) — admin only</label>
    </div>
    <div style="display:flex;gap:8px">
      <button class="btn btn-primary" disabled={saving || !form.name} on:click={create}>
        {saving ? 'Creating…' : 'Create'}
      </button>
      <button class="btn btn-ghost" on:click={() => showCreate = false}>Cancel</button>
    </div>
  </div>
{/if}

{#if loading}
  <p style="color:var(--text2)">Loading…</p>
{:else if libraries.length === 0}
  <div class="empty-state">
    <div style="font-size:3rem">📚</div>
    <p>No libraries yet. Create your first one!</p>
  </div>
{:else}
  <div class="lib-grid">
    {#each libraries as lib}
      <div class="card card-hover lib-card">
        <div style="display:flex;align-items:flex-start;justify-content:space-between;margin-bottom:6px">
          <a href="/libraries/{lib.id}" style="font-weight:600;font-size:1rem;color:var(--text)">{lib.name}</a>
          <div style="display:flex;gap:4px">
            {#if lib.is_global}<span class="badge badge-success">global</span>{/if}
            {#if !lib.owner_id}<span class="badge badge-accent">system</span>{/if}
          </div>
        </div>
        {#if lib.description}
          <p style="color:var(--text2);font-size:0.82rem;margin-bottom:8px">{lib.description}</p>
        {/if}
        <div style="display:flex;align-items:center;justify-content:space-between;margin-top:auto">
          <span style="color:var(--text3);font-size:0.8rem">{lib.song_count} songs</span>
          <div style="display:flex;gap:6px">
            <a href="/libraries/{lib.id}" class="btn btn-ghost btn-sm">Open</a>
            <button class="btn btn-ghost btn-sm" style="color:var(--error)"
              on:click={() => deleteLib(lib.id)}>Delete</button>
          </div>
        </div>
      </div>
    {/each}
  </div>
{/if}

<style>
  .lib-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px,1fr)); gap: 1rem; }
  .lib-card { display: flex; flex-direction: column; min-height: 120px; }
  .empty-state {
    text-align: center; padding: 4rem 2rem; color: var(--text2);
    background: var(--bg2); border: 1px dashed var(--border); border-radius: 12px;
  }
</style>

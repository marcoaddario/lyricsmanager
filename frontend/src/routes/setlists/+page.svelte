<script lang="ts">
  import { onMount } from 'svelte';
  import { api } from '$lib/services/api';
  import { offlineStore } from '$lib/services/offline';
  import { toasts } from '$lib/stores';

  let setlists: any[] = [];
  let downloaded = new Set<number>();
  let loading = true;
  let showCreate = false;
  let form = { name: '', description: '', event_date: '' };
  let saving = false;

  onMount(async () => {
    try { setlists = await api.setlists.list(); } catch {}
    const cached = await offlineStore.listSetlists();
    downloaded = new Set(cached.map((c: any) => c.id));
    loading = false;
  });

  async function createSetlist() {
    saving = true;
    try {
      const sl = await api.setlists.create({
        name: form.name,
        description: form.description || undefined,
        event_date: form.event_date || undefined
      });
      setlists = [sl, ...setlists];
      showCreate = false;
      form = { name: '', description: '', event_date: '' };
      toasts.add('Set list created', 'success');
    } catch (e: any) {
      toasts.add(e.message, 'error');
    } finally { saving = false; }
  }

  async function deleteSetlist(id: number) {
    if (!confirm('Delete this set list?')) return;
    try {
      await api.setlists.delete(id);
      setlists = setlists.filter(s => s.id !== id);
      toasts.add('Deleted', 'success');
    } catch (e: any) { toasts.add(e.message, 'error'); }
  }

  async function downloadSetlist(id: number) {
    try {
      const data = await api.setlists.download(id);
      await offlineStore.saveSetlist(data);
      downloaded = new Set([...downloaded, id]);
      toasts.add('Downloaded for offline use ✓', 'success');
    } catch (e: any) { toasts.add(e.message, 'error'); }
  }

  async function removeOffline(id: number) {
    await offlineStore.deleteSetlist(id);
    downloaded = new Set([...downloaded].filter(x => x !== id));
    toasts.add('Removed from device', 'info');
  }
</script>

<svelte:head><title>Set Lists — Lyrics Manager</title></svelte:head>

<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:1.5rem">
  <h1>Set Lists</h1>
  <button class="btn btn-primary" on:click={() => showCreate = !showCreate}>+ New set list</button>
</div>

{#if showCreate}
  <div class="card" style="margin-bottom:1.5rem">
    <h3 style="margin-bottom:1rem">New set list</h3>
    <div class="field">
      <label>Name *</label>
      <input class="input" bind:value={form.name} placeholder="Sunday service, Festival night…" />
    </div>
    <div class="field">
      <label>Description</label>
      <input class="input" bind:value={form.description} placeholder="Optional notes" />
    </div>
    <div class="field">
      <label>Event date</label>
      <input class="input" type="date" bind:value={form.event_date} />
    </div>
    <div style="display:flex;gap:8px">
      <button class="btn btn-primary" disabled={saving || !form.name} on:click={createSetlist}>
        {saving ? 'Saving…' : 'Create'}
      </button>
      <button class="btn btn-ghost" on:click={() => showCreate = false}>Cancel</button>
    </div>
  </div>
{/if}

{#if loading}
  <p style="color:var(--text2)">Loading…</p>
{:else if setlists.length === 0}
  <div class="empty-state">
    <div style="font-size:3rem">📋</div>
    <p>No set lists yet. Create your first one!</p>
  </div>
{:else}
  <div class="setlist-grid">
    {#each setlists as sl}
      <div class="card card-hover setlist-card">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:8px">
          <a href="/setlists/{sl.id}" style="font-weight:600;color:var(--text)">{sl.name}</a>
          <span class="badge badge-accent">{sl.song_count} songs</span>
        </div>
        {#if sl.description}
          <p style="color:var(--text2);font-size:0.82rem;margin-bottom:8px">{sl.description}</p>
        {/if}
        {#if sl.event_date}
          <p style="color:var(--text3);font-size:0.78rem;margin-bottom:10px">
            📅 {new Date(sl.event_date).toLocaleDateString(undefined, {weekday:'short',year:'numeric',month:'short',day:'numeric'})}
          </p>
        {/if}
        <div style="display:flex;gap:6px;flex-wrap:wrap">
          <a href="/setlists/{sl.id}" class="btn btn-ghost btn-sm">Edit</a>
          <a href="/perform/{sl.id}" class="btn btn-primary btn-sm">🎤 Perform</a>
          {#if downloaded.has(sl.id)}
            <button class="btn btn-ghost btn-sm" style="color:var(--success)"
              on:click={() => removeOffline(sl.id)}>✓ Offline</button>
          {:else}
            <button class="btn btn-ghost btn-sm" on:click={() => downloadSetlist(sl.id)}>⬇ Download</button>
          {/if}
          <button class="btn btn-ghost btn-sm" style="color:var(--error);margin-left:auto"
            on:click={() => deleteSetlist(sl.id)}>Delete</button>
        </div>
      </div>
    {/each}
  </div>
{/if}

<style>
  .setlist-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 1rem; }
  .setlist-card { display: flex; flex-direction: column; }
  .empty-state {
    text-align: center; padding: 4rem 2rem; color: var(--text2);
    background: var(--bg2); border: 1px dashed var(--border); border-radius: 12px;
  }
</style>

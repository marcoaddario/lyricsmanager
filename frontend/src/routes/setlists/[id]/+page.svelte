<script lang="ts">
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import { api } from '$lib/services/api';
  import { offlineStore } from '$lib/services/offline';
  import { toasts } from '$lib/stores';

  const id = Number($page.params.id);

  let setlist: any = null;
  let libraries: any[] = [];
  let allSongs: any[] = [];
  let selectedLibrary: number | null = null;
  let songSearch = '';
  let loading = true;
  let saving = false;
  let isDownloaded = false;

  // Metadata editing
  let editingMetadata = false;
  let metadataForm = { name: '', description: '', event_date: '' };

  // Editable items list (positions are indices+1)
  let items: any[] = [];

  onMount(async () => {
    [setlist, libraries] = await Promise.all([api.setlists.get(id), api.libraries.list()]);
    items = [...setlist.items];
    metadataForm = {
      name: setlist.name,
      description: setlist.description || '',
      event_date: setlist.event_date ? new Date(setlist.event_date).toISOString().split('T')[0] : ''
    };
    if (libraries.length > 0) { selectedLibrary = libraries[0].id; await loadSongs(); }
    isDownloaded = await offlineStore.isSetlistDownloaded(id);
    loading = false;
  });

  async function loadSongs() {
    if (!selectedLibrary) return;
    try { allSongs = await api.songs.list(selectedLibrary, songSearch || undefined); } catch {}
  }

  $: if (selectedLibrary) loadSongs();
  $: if (songSearch !== undefined) loadSongs();

  function addSong(song: any) {
    if (items.find(i => i.song_id === song.id)) { toasts.add('Song already in set list', 'info'); return; }
    items = [...items, { song_id: song.id, position: items.length + 1, song }];
  }

  function removeItem(idx: number) {
    items = items.filter((_, i) => i !== idx);
  }

  function moveUp(idx: number) {
    if (idx === 0) return;
    const arr = [...items];
    [arr[idx - 1], arr[idx]] = [arr[idx], arr[idx - 1]];
    items = arr;
  }

  function moveDown(idx: number) {
    if (idx === items.length - 1) return;
    const arr = [...items];
    [arr[idx], arr[idx + 1]] = [arr[idx + 1], arr[idx]];
    items = arr;
  }

  async function save() {
    saving = true;
    try {
      const payload = items.map((item, i) => ({
        song_id: item.song_id, position: i + 1,
        transpose_key: item.transpose_key || undefined,
        notes: item.notes || undefined
      }));
      setlist = await api.setlists.replaceItems(id, payload);
      items = [...setlist.items];
      toasts.add('Saved ✓', 'success');
    } catch (e: any) { toasts.add(e.message, 'error'); }
    finally { saving = false; }
  }

  async function updateMetadata() {
    saving = true;
    try {
      const payload = {
        name: metadataForm.name,
        description: metadataForm.description || undefined,
        event_date: metadataForm.event_date || undefined
      };
      setlist = await api.setlists.update(id, payload);
      editingMetadata = false;
      toasts.add('Metadata updated ✓', 'success');
    } catch (e: any) { toasts.add(e.message, 'error'); }
    finally { saving = false; }
  }

  async function downloadOffline() {
    try {
      const data = await api.setlists.download(id);
      await offlineStore.saveSetlist(data);
      isDownloaded = true;
      toasts.add('Downloaded for offline use ✓', 'success');
    } catch (e: any) { toasts.add(e.message, 'error'); }
  }
</script>

<svelte:head><title>{setlist?.name || 'Set List'} — Lyrics Manager</title></svelte:head>

{#if loading}
  <p style="color:var(--text2)">Loading…</p>
{:else}
  <div style="display:flex;align-items:center;gap:12px;margin-bottom:1.5rem;flex-wrap:wrap">
    <a href="/setlists" style="color:var(--text2);font-size:0.85rem">← Back</a>
    {#if editingMetadata}
      <div style="flex:1">
        <div class="field" style="margin-bottom:0.5rem">
          <input class="input" bind:value={metadataForm.name} placeholder="Setlist name" />
        </div>
        <div class="field" style="margin-bottom:0.5rem">
          <input class="input" bind:value={metadataForm.description} placeholder="Description (optional)" />
        </div>
        <div class="field" style="margin-bottom:0">
          <input class="input" type="date" bind:value={metadataForm.event_date} />
        </div>
      </div>
      <button class="btn btn-ghost" on:click={() => { editingMetadata = false; metadataForm = { name: setlist.name, description: setlist.description || '', event_date: setlist.event_date ? new Date(setlist.event_date).toISOString().split('T')[0] : '' }; }}>Cancel</button>
      <button class="btn btn-primary" disabled={saving} on:click={updateMetadata}>
        {saving ? 'Saving…' : 'Save'}
      </button>
    {:else}
      <h1 style="flex:1">{setlist.name}</h1>
      <button class="btn btn-ghost" on:click={() => editingMetadata = true}>✏ Edit metadata</button>
    {/if}
    <a href="/perform/{id}" class="btn btn-primary">🎤 Perform</a>
    {#if isDownloaded}
      <span class="badge badge-success">✓ Offline cached</span>
    {:else}
      <button class="btn btn-ghost" on:click={downloadOffline}>⬇ Save offline</button>
    {/if}
    <button class="btn btn-primary" disabled={saving} on:click={save}>
      {saving ? 'Saving…' : 'Save order'}
    </button>
  </div>

  <div class="editor-layout">
    <!-- Current set list -->
    <div class="panel">
      <h3 style="margin-bottom:1rem">Set list ({items.length} songs)</h3>
      {#if items.length === 0}
        <div style="color:var(--text3);text-align:center;padding:2rem">Add songs from the library →</div>
      {:else}
        <div class="setlist-items">
          {#each items as item, idx}
            <div class="set-item">
              <span class="position mono">{idx + 1}</span>
              <div class="set-item-info">
                <span class="set-item-title">{item.song?.title || item.song_id}</span>
                {#if item.song?.artist}<span class="set-item-artist">{item.song.artist}</span>{/if}
              </div>
              <div class="set-item-actions">
                <button class="btn btn-ghost btn-sm" on:click={() => moveUp(idx)} disabled={idx === 0}>↑</button>
                <button class="btn btn-ghost btn-sm" on:click={() => moveDown(idx)} disabled={idx === items.length-1}>↓</button>
                <button class="btn btn-ghost btn-sm" style="color:var(--error)" on:click={() => removeItem(idx)}>✕</button>
              </div>
            </div>
          {/each}
        </div>
      {/if}
    </div>

    <!-- Library picker -->
    <div class="panel">
      <h3 style="margin-bottom:1rem">Add from library</h3>
      <div class="field">
        <label>Library</label>
        <select class="input" bind:value={selectedLibrary}>
          {#each libraries as lib}
            <option value={lib.id}>{lib.name}</option>
          {/each}
        </select>
      </div>
      <div class="field">
        <label>Search</label>
        <input class="input" bind:value={songSearch} placeholder="Title or artist…" />
      </div>
      <div class="song-list">
        {#each allSongs as song}
          <button class="song-row" on:click={() => addSong(song)}
            class:already-added={items.some(i => i.song_id === song.id)}>
            <div>
              <span class="song-title">{song.title}</span>
              {#if song.artist}<span class="song-artist"> — {song.artist}</span>{/if}
            </div>
            {#if song.key}<span class="badge badge-accent" style="font-size:0.65rem">{song.key}</span>{/if}
            <span style="color:var(--accent);margin-left:auto">+</span>
          </button>
        {/each}
      </div>
    </div>
  </div>
{/if}

<style>
  .editor-layout {
    display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem;
  }
  @media (max-width: 700px) { .editor-layout { grid-template-columns: 1fr; } }
  .panel { background: var(--bg2); border: 1px solid var(--border); border-radius: 10px; padding: 1.25rem; }

  .setlist-items { display: flex; flex-direction: column; gap: 6px; }
  .set-item {
    display: flex; align-items: center; gap: 10px;
    background: var(--bg3); border: 1px solid var(--border); border-radius: 8px;
    padding: 0.5rem 0.75rem;
  }
  .position { color: var(--text3); font-size: 0.8rem; min-width: 20px; }
  .set-item-info { flex: 1; min-width: 0; }
  .set-item-title { font-weight: 500; font-size: 0.875rem; display: block; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  .set-item-artist { color: var(--text2); font-size: 0.78rem; }
  .set-item-actions { display: flex; gap: 4px; flex-shrink: 0; }

  .song-list { display: flex; flex-direction: column; gap: 4px; max-height: 400px; overflow-y: auto; }
  .song-row {
    display: flex; align-items: center; gap: 8px;
    background: var(--bg3); border: 1px solid transparent; border-radius: 8px;
    padding: 0.5rem 0.75rem; text-align: left; width: 100%;
    transition: border-color 0.12s, background 0.12s;
  }
  .song-row:hover { border-color: var(--border2); background: var(--bg4); }
  .song-row.already-added { opacity: 0.4; }
  .song-title { font-size: 0.875rem; font-weight: 500; color: var(--text); }
  .song-artist { font-size: 0.78rem; color: var(--text2); }
</style>

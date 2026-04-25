<script lang="ts">
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import { api } from '$lib/services/api';
  import { toasts } from '$lib/stores';

  const libId = Number($page.params.id);

  let library: any = null;
  let songs: any[] = [];
  let loading = true;
  let search = '';
  let searchTimer: any;

  let editingSong: any = null;   // null = hidden, {} = new, {id:...} = edit
  let songForm = { title: '', artist: '', lyrics: '', key: '', tempo: '', notes: '' };
  let saving = false;

  onMount(async () => {
    [library, songs] = await Promise.all([
      api.libraries.get(libId),
      api.songs.list(libId)
    ]);
    loading = false;
  });

  function onSearchInput() {
    clearTimeout(searchTimer);
    searchTimer = setTimeout(async () => {
      songs = await api.songs.list(libId, search || undefined);
    }, 300);
  }

  function openNew() {
    editingSong = {};
    songForm = { title: '', artist: '', lyrics: '', key: '', tempo: '', notes: '' };
  }

  function openEdit(song: any) {
    editingSong = song;
    songForm = {
      title: song.title, artist: song.artist || '',
      lyrics: song.lyrics || '', key: song.key || '',
      tempo: song.tempo?.toString() || '', notes: song.notes || ''
    };
  }

  function closeEditor() { editingSong = null; }

  async function saveSong() {
    saving = true;
    const payload = {
      title: songForm.title,
      artist: songForm.artist || undefined,
      lyrics: songForm.lyrics,
      key: songForm.key || undefined,
      tempo: songForm.tempo ? Number(songForm.tempo) : undefined,
      notes: songForm.notes || undefined,
    };
    try {
      if (editingSong?.id) {
        const updated = await api.songs.update(libId, editingSong.id, payload);
        songs = songs.map(s => s.id === updated.id ? updated : s);
        toasts.add('Song saved', 'success');
      } else {
        const created = await api.songs.create(libId, payload);
        songs = [created, ...songs];
        toasts.add('Song added', 'success');
      }
      closeEditor();
    } catch (e: any) { toasts.add(e.message, 'error'); }
    finally { saving = false; }
  }

  async function deleteSong(id: number) {
    if (!confirm('Delete this song?')) return;
    try {
      await api.songs.delete(libId, id);
      songs = songs.filter(s => s.id !== id);
      if (editingSong?.id === id) closeEditor();
      toasts.add('Song deleted', 'success');
    } catch (e: any) { toasts.add(e.message, 'error'); }
  }
</script>

<svelte:head><title>{library?.name || 'Library'} — Lyrics Manager</title></svelte:head>

{#if loading}
  <p style="color:var(--text2)">Loading…</p>
{:else}
  <div style="display:flex;align-items:center;gap:12px;margin-bottom:1.5rem;flex-wrap:wrap">
    <a href="/libraries" style="color:var(--text2);font-size:0.85rem">← Libraries</a>
    <h1 style="flex:1">
      {library.name}
      {#if library.is_global}<span class="badge badge-success" style="margin-left:8px">global</span>{/if}
    </h1>
    <button class="btn btn-primary" on:click={openNew}>+ Add song</button>
  </div>

  <div class="layout">
    <!-- Song list panel -->
    <div class="panel">
      <input class="input" style="margin-bottom:1rem" bind:value={search}
        on:input={onSearchInput} placeholder="Search songs…" />

      {#if songs.length === 0}
        <div style="text-align:center;padding:2rem;color:var(--text3)">No songs found</div>
      {:else}
        <div class="song-list">
          {#each songs as song}
            <div class="song-row" class:active={editingSong?.id === song.id}>
              <div class="song-info" role="button" tabindex="0"
                on:click={() => openEdit(song)} on:keydown={e => e.key==='Enter' && openEdit(song)}>
                <span class="song-title">{song.title}</span>
                {#if song.artist}<span class="song-artist">{song.artist}</span>{/if}
              </div>
              <div class="song-meta">
                {#if song.key}<span class="badge badge-accent">{song.key}</span>{/if}
                <button class="btn btn-ghost btn-sm" on:click={() => openEdit(song)}>Edit</button>
                <button class="btn btn-ghost btn-sm" style="color:var(--error)"
                  on:click={() => deleteSong(song.id)}>✕</button>
              </div>
            </div>
          {/each}
        </div>
      {/if}
    </div>

    <!-- Song editor panel -->
    {#if editingSong !== null}
      <div class="panel editor-panel">
        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:1.25rem">
          <h3>{editingSong?.id ? 'Edit song' : 'New song'}</h3>
          <button class="btn btn-ghost btn-sm" on:click={closeEditor}>✕</button>
        </div>

        <div class="field">
          <label>Title *</label>
          <input class="input" bind:value={songForm.title} placeholder="Song title" />
        </div>
        <div class="field">
          <label>Artist</label>
          <input class="input" bind:value={songForm.artist} placeholder="Artist / Band" />
        </div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:0.75rem">
          <div class="field">
            <label>Key</label>
            <input class="input" bind:value={songForm.key} placeholder="C, Am, G#…" />
          </div>
          <div class="field">
            <label>Tempo (BPM)</label>
            <input class="input" type="number" bind:value={songForm.tempo} placeholder="120" />
          </div>
        </div>
        <div class="field">
          <label>Lyrics</label>
          <textarea class="input" bind:value={songForm.lyrics} rows="14"
            placeholder="Paste or type lyrics here…&#10;&#10;[Verse 1]&#10;…"></textarea>
        </div>
        <div class="field">
          <label>Notes</label>
          <input class="input" bind:value={songForm.notes} placeholder="Performance notes, cues…" />
        </div>

        <div style="display:flex;gap:8px;margin-top:0.5rem">
          <button class="btn btn-primary" disabled={saving || !songForm.title} on:click={saveSong}>
            {saving ? 'Saving…' : editingSong?.id ? 'Save changes' : 'Add song'}
          </button>
          <button class="btn btn-ghost" on:click={closeEditor}>Cancel</button>
          {#if editingSong?.id}
            <button class="btn btn-ghost" style="color:var(--error);margin-left:auto"
              on:click={() => deleteSong(editingSong.id)}>Delete song</button>
          {/if}
        </div>
      </div>
    {/if}
  </div>
{/if}

<style>
  .layout {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.5rem;
    align-items: start;
  }
  @media (max-width: 700px) { .layout { grid-template-columns: 1fr; } }

  .panel {
    background: var(--bg2); border: 1px solid var(--border);
    border-radius: 10px; padding: 1.25rem;
  }
  .editor-panel { position: sticky; top: 1rem; }

  .song-list { display: flex; flex-direction: column; gap: 4px; max-height: 65vh; overflow-y: auto; }
  .song-row {
    display: flex; align-items: center; gap: 8px;
    padding: 0.55rem 0.75rem; border-radius: 8px;
    border: 1px solid transparent;
    transition: background 0.12s, border-color 0.12s;
  }
  .song-row:hover { background: var(--bg3); border-color: var(--border); }
  .song-row.active { background: var(--accent-glow); border-color: var(--accent); }
  .song-info { flex: 1; cursor: pointer; min-width: 0; }
  .song-title { font-size: 0.875rem; font-weight: 500; display: block; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  .song-artist { font-size: 0.78rem; color: var(--text2); }
  .song-meta { display: flex; gap: 6px; align-items: center; flex-shrink: 0; }
</style>

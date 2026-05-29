<script lang="ts">
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import { api } from '$lib/services/api';
  import { offlineStore } from '$lib/services/offline';
  import { toasts, user } from '$lib/stores';

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

  // Drag and drop
  let draggedIndex: number | null = null;

  // Editable items list (positions are indices+1)
  let items: any[] = [];

  // Computed
  let isOwner = false;
  let canEdit = false;
  let isViewOnly = false;
  let ownerLabel = '';
  $: {
    isOwner = setlist && setlist.permission === null;
    canEdit = isOwner || setlist?.permission === 'edit';
    isViewOnly = setlist?.permission === 'view';
    ownerLabel = setlist?.owner_name || '';
  }

  // Sharing state
  let shares: any[] = [];
  let showSharing = false;
  let userSearchQuery = '';
  let userSearchResults: any[] = [];
  let searchingUsers = false;
  let selectedUser: any | null = null;
  let sharePermission = 'view';
  let sharingSaving = false;
  let searchTimeout: number | null = null;

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
    if (isOwner) {
      loadShares();
    }
    loading = false;
  });

  async function loadShares() {
    try {
      shares = await api.setlists.listShares(id);
    } catch {}
  }

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

  function onDragStart(event: DragEvent, idx: number) {
    if ((event.target as HTMLElement).tagName === 'BUTTON') return;
    draggedIndex = idx;
    event.dataTransfer!.effectAllowed = 'move';
  }

  function onDragOver(event: DragEvent) {
    event.preventDefault();
    event.dataTransfer!.dropEffect = 'move';
  }

  function onDrop(event: DragEvent, dropIndex: number) {
    event.preventDefault();
    if (draggedIndex === null || draggedIndex === dropIndex) return;

    const newItems = [...items];
    const [draggedItem] = newItems.splice(draggedIndex, 1);
    newItems.splice(dropIndex, 0, draggedItem);
    items = newItems;
    draggedIndex = null;
  }

  function onDragEnd() {
    draggedIndex = null;
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

  // ── Sharing functions ──────────────────────────────────────────────

  function onUserSearchInput(query: string) {
    userSearchQuery = query;
    selectedUser = null;
    if (searchTimeout) clearTimeout(searchTimeout);
    if (query.length < 2) {
      userSearchResults = [];
      return;
    }
    searchTimeout = window.setTimeout(async () => {
      searchingUsers = true;
      try {
        const results = await api.users.search(query);
        userSearchResults = results.filter((u: any) => u.id !== $user?.id);
      } catch {
        userSearchResults = [];
      } finally {
        searchingUsers = false;
      }
    }, 300);
  }

  function selectUser(u: any) {
    selectedUser = u;
    userSearchQuery = u.display_name || u.username;
    userSearchResults = [];
  }

  async function addShare() {
    if (!selectedUser) return;
    sharingSaving = true;
    try {
      await api.setlists.addShare(id, {
        shared_with_user_id: selectedUser.id,
        permission: sharePermission
      });
      toasts.add('Shared ✓', 'success');
      selectedUser = null;
      userSearchQuery = '';
      sharePermission = 'view';
      await loadShares();
    } catch (e: any) {
      toasts.add(e.message, 'error');
    } finally {
      sharingSaving = false;
    }
  }

  async function changePermission(shareId: number, newPermission: string) {
    try {
      await api.setlists.updateShare(id, shareId, { permission: newPermission });
      toasts.add('Permission updated ✓', 'success');
      await loadShares();
    } catch (e: any) {
      toasts.add(e.message, 'error');
    }
  }

  async function removeShare(shareId: number) {
    try {
      await api.setlists.removeShare(id, shareId);
      toasts.add('Share removed', 'info');
      await loadShares();
    } catch (e: any) {
      toasts.add(e.message, 'error');
    }
  }
</script>

<svelte:head><title>{setlist?.name || 'Set List'} — Lyrics Manager</title></svelte:head>

{#if loading}
  <p style="color:var(--text2)">Loading…</p>
{:else}
  <!-- Shared banner -->
  {#if !isOwner}
    <div class="shared-banner">
      <span>🔗 Shared with you by <strong>{ownerLabel}</strong></span>
      {#if setlist.permission === 'edit'}
        <span class="badge badge-warning" style="margin-left:8px">Edit access</span>
      {:else}
        <span class="badge badge-info" style="margin-left:8px">View only</span>
      {/if}
    </div>
  {/if}

  <div style="display:flex;align-items:center;gap:12px;margin-bottom:1.5rem;flex-wrap:wrap">
    <a href="/setlists" style="color:var(--text2);font-size:0.85rem">← Back</a>
    {#if editingMetadata && canEdit}
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
      {#if canEdit}
        <button class="btn btn-ghost" on:click={() => editingMetadata = true}>✏ Edit metadata</button>
      {/if}
    {/if}
    <a href="/perform/{id}" class="btn btn-primary">🎤 Perform</a>
    {#if isDownloaded}
      <span class="badge badge-success">✓ Offline cached</span>
    {:else}
      <button class="btn btn-ghost" on:click={downloadOffline}>⬇ Save offline</button>
    {/if}
    {#if canEdit}
      <button class="btn btn-primary" disabled={saving} on:click={save}>
        {saving ? 'Saving…' : 'Save order'}
      </button>
    {/if}
  </div>

  <div class="editor-layout">
    <!-- Current set list -->
    <div class="panel">
      <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:1rem">
        <h3>Set list ({items.length} songs)</h3>
        {#if isOwner}
          <button class="btn btn-ghost btn-sm" on:click={() => showSharing = !showSharing}>
            {showSharing ? 'Close sharing' : '🔗 Share'}
          </button>
        {/if}
      </div>

      <!-- Sharing panel (owner only) -->
      {#if showSharing && isOwner}
        <div class="sharing-panel">
          <h4 style="margin-bottom:0.75rem;font-size:0.9rem;color:var(--text2)">Share with users</h4>

          <!-- Add share form -->
          <div class="share-form">
            <div class="share-search">
              <input
                class="input"
                placeholder="Search users by name or email…"
                value={userSearchQuery}
                on:input={(e) => onUserSearchInput(e.currentTarget.value)}
                on:blur={() => setTimeout(() => userSearchResults = [], 200)}
              />
              {#if userSearchResults.length > 0}
                <div class="search-results">
                  {#each userSearchResults as u}
                    <button class="search-result-item" on:click={() => selectUser(u)} type="button">
                      <strong>{u.display_name || u.username}</strong>
                      <span style="color:var(--text3);font-size:0.78rem">{u.email}</span>
                    </button>
                  {/each}
                </div>
              {/if}
              {#if searchingUsers}
                <div class="searching-hint">Searching…</div>
              {/if}
            </div>
            <select class="input share-perm-select" bind:value={sharePermission}>
              <option value="view">View only</option>
              <option value="edit">Can edit</option>
            </select>
            <button class="btn btn-primary btn-sm" disabled={!selectedUser || sharingSaving} on:click={addShare}>
              {sharingSaving ? '…' : 'Share'}
            </button>
          </div>

          <!-- Current shares -->
          {#if shares.length > 0}
            <div class="shares-list">
              {#each shares as share}
                <div class="share-item">
                  <div class="share-user">
                    <span class="share-user-name">{share.shared_with_user.display_name || share.shared_with_user.username}</span>
                    <span class="share-user-email">{share.shared_with_user.email}</span>
                  </div>
                  <div class="share-actions">
                    <select
                      class="input share-perm-toggle"
                      value={share.permission}
                      on:change={(e) => changePermission(share.id, e.currentTarget.value)}
                    >
                      <option value="view">👁 View</option>
                      <option value="edit">✏ Edit</option>
                    </select>
                    <button class="btn btn-ghost btn-sm" style="color:var(--error)" on:click={() => removeShare(share.id)}>
                      ✕
                    </button>
                  </div>
                </div>
              {/each}
            </div>
          {:else}
            <p style="color:var(--text3);font-size:0.82rem;margin-top:0.5rem">Not shared with anyone yet.</p>
          {/if}
        </div>
      {/if}

      {#if items.length === 0}
        <div style="color:var(--text3);text-align:center;padding:2rem">{canEdit ? 'Add songs from the library →' : 'No songs in this setlist.'}</div>
      {:else}
        <div class="setlist-items">
          {#each items as item, idx}
            <div class="set-item"
                 draggable={canEdit ? "true" : "false"}
                 on:dragstart={(e) => canEdit && onDragStart(e, idx)}
                 on:dragover={canEdit ? onDragOver : undefined}
                 on:drop={(e) => canEdit && onDrop(e, idx)}
                 on:dragend={canEdit ? onDragEnd : undefined}
                 class:dragging={draggedIndex === idx}>
              <span class="position mono">{idx + 1}</span>
              <div class="set-item-info">
                <span class="set-item-title">{item.song?.title || item.song_id}</span>
                {#if item.song?.artist}<span class="set-item-artist">{item.song.artist}</span>{/if}
              </div>
              {#if canEdit}
                <div class="set-item-actions">
                  <button class="btn btn-ghost btn-sm" on:click={() => moveUp(idx)} disabled={idx === 0}>↑</button>
                  <button class="btn btn-ghost btn-sm" on:click={() => moveDown(idx)} disabled={idx === items.length-1}>↓</button>
                  <button class="btn btn-ghost btn-sm" style="color:var(--error)" on:click={() => removeItem(idx)}>✕</button>
                </div>
              {/if}
            </div>
          {/each}
        </div>
      {/if}
    </div>

    <!-- Library picker (only if can edit) -->
    {#if canEdit}
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
    {/if}
  </div>
{/if}

<style>
  .editor-layout {
    display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem;
  }
  @media (max-width: 700px) { .editor-layout { grid-template-columns: 1fr; } }
  .panel { background: var(--bg2); border: 1px solid var(--border); border-radius: 10px; padding: 1.25rem; }

  .shared-banner {
    display: flex; align-items: center; gap: 4px;
    background: var(--bg4); border: 1px solid var(--border2);
    border-radius: 8px; padding: 0.6rem 1rem;
    margin-bottom: 1rem; font-size: 0.85rem;
  }

  /* Sharing panel */
  .sharing-panel {
    background: var(--bg3); border: 1px solid var(--border);
    border-radius: 8px; padding: 0.85rem;
    margin-bottom: 1rem;
  }
  .share-form {
    display: flex; gap: 8px; align-items: flex-start;
    flex-wrap: wrap;
  }
  .share-search {
    flex: 1; min-width: 180px; position: relative;
  }
  .share-perm-select {
    width: 130px; flex-shrink: 0;
  }
  .search-results {
    position: absolute; top: 100%; left: 0; right: 0;
    background: var(--bg2); border: 1px solid var(--border2);
    border-radius: 6px; z-index: 10;
    max-height: 200px; overflow-y: auto;
    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
  }
  .search-result-item {
    display: flex; flex-direction: column; gap: 2px;
    width: 100%; text-align: left;
    padding: 0.5rem 0.75rem;
    background: none; border: none; cursor: pointer;
    font-size: 0.82rem;
  }
  .search-result-item:hover { background: var(--bg4); }
  .searching-hint {
    font-size: 0.75rem; color: var(--text3);
    padding: 4px 0;
  }
  .shares-list {
    display: flex; flex-direction: column; gap: 6px;
    margin-top: 0.75rem;
  }
  .share-item {
    display: flex; align-items: center; justify-content: space-between;
    gap: 8px; padding: 0.5rem 0.65rem;
    background: var(--bg2); border: 1px solid var(--border);
    border-radius: 6px;
  }
  .share-user {
    display: flex; flex-direction: column; gap: 1px;
    min-width: 0;
  }
  .share-user-name { font-weight: 500; font-size: 0.82rem; }
  .share-user-email { font-size: 0.75rem; color: var(--text3); }
  .share-actions {
    display: flex; align-items: center; gap: 6px;
    flex-shrink: 0;
  }
  .share-perm-toggle {
    width: 100px; font-size: 0.75rem;
  }

  .setlist-items { display: flex; flex-direction: column; gap: 6px; }
  .set-item {
    display: flex; align-items: center; gap: 10px;
    background: var(--bg3); border: 1px solid var(--border); border-radius: 8px;
    padding: 0.5rem 0.75rem;
    cursor: grab;
  }
  .set-item.dragging {
    opacity: 0.5;
    transform: rotate(2deg);
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

  .badge-warning {
    background: #f59e0b20; color: #f59e0b;
    border: 1px solid #f59e0b40;
    padding: 2px 8px; border-radius: 6px; font-size: 0.72rem; font-weight: 500;
  }
  .badge-info {
    background: #3b82f620; color: #60a5fa;
    border: 1px solid #3b82f640;
    padding: 2px 8px; border-radius: 6px; font-size: 0.72rem; font-weight: 500;
  }
</style>

<script lang="ts">
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import { isOnline } from '$lib/stores';
  import { api } from '$lib/services/api';
  import { offlineStore } from '$lib/services/offline';

  const id = Number($page.params.id);

  let setlist: any = null;
  let currentIdx = 0;
  let loading = true;
  let error = '';
  let fontSize = 1.2; // rem

  onMount(async () => {
    // Try online first, then offline cache
    try {
      if ($isOnline) {
        setlist = await api.setlists.get(id);
      } else {
        throw new Error('offline');
      }
    } catch {
      const cached = await offlineStore.getSetlist(id);
      if (cached) {
        setlist = cached;
      } else {
        error = 'Set list not found. Download it for offline use first.';
      }
    }
    loading = false;
  });

  $: current = setlist?.items?.[currentIdx];
  $: total = setlist?.items?.length || 0;

  function next() { if (currentIdx < total - 1) currentIdx++; }
  function prev() { if (currentIdx > 0) currentIdx--; }

  function handleKey(e: KeyboardEvent) {
    if (e.key === 'ArrowRight' || e.key === 'ArrowDown' || e.key === ' ') { e.preventDefault(); next(); }
    if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') { e.preventDefault(); prev(); }
    if (e.key === '+' || e.key === '=') fontSize = Math.min(fontSize + 0.15, 3);
    if (e.key === '-') fontSize = Math.max(fontSize - 0.15, 0.7);
    if (e.key === 'Escape') history.back();
  }
</script>

<svelte:head><title>{setlist?.name || 'Perform'} — Lyrics Manager</title></svelte:head>
<svelte:window on:keydown={handleKey} />

{#if loading}
  <div class="center">Loading…</div>
{:else if error}
  <div class="center error">{error} <a href="/setlists">← Back</a></div>
{:else}
  <div class="perform-shell">
    <!-- Top bar -->
    <header class="perf-header">
      <a href="/setlists/{id}" class="back-btn">✕</a>
      <span class="setlist-name">{setlist.name}</span>
      <div style="display:flex;gap:6px;align-items:center">
        <button class="ctrl-btn" on:click={() => fontSize = Math.max(fontSize - 0.15, 0.7)}>A−</button>
        <button class="ctrl-btn" on:click={() => fontSize = Math.min(fontSize + 0.15, 3)}>A+</button>
      </div>
    </header>

    <!-- Song info bar -->
    <div class="song-info-bar">
      <div>
        <span class="song-num">{currentIdx + 1} / {total}</span>
        <strong class="song-title-perf">{current?.song?.title}</strong>
        {#if current?.song?.artist}<span class="song-artist-perf">{current.song.artist}</span>{/if}
      </div>
      {#if current?.song?.key}
        <span class="badge badge-accent" style="font-size:0.75rem">Key: {current.transpose_key || current.song.key}</span>
      {/if}
    </div>

    <!-- Lyrics -->
    <div class="lyrics-area" style="font-size: {fontSize}rem">
      <pre class="lyrics-text">{current?.song?.lyrics || '(No lyrics)'}</pre>
    </div>

    <!-- Nav bar -->
    <footer class="perf-footer">
      <!-- Song selector pills -->
      <div class="song-pills">
        {#each setlist.items as item, idx}
          <button class="pill" class:active={idx === currentIdx} on:click={() => currentIdx = idx}>
            {idx + 1}
          </button>
        {/each}
      </div>
      <div class="nav-btns">
        <button class="nav-btn" disabled={currentIdx === 0} on:click={prev}>← Prev</button>
        <button class="nav-btn" disabled={currentIdx === total - 1} on:click={next}>Next →</button>
      </div>
    </footer>
  </div>
{/if}

<style>
  :global(body) { overflow: hidden; }

  .perform-shell {
    position: fixed; inset: 0;
    display: flex; flex-direction: column;
    background: var(--lyrics-bg); color: var(--lyrics-text);
  }

  .perf-header {
    display: flex; align-items: center; gap: 12px;
    padding: 0.6rem 1rem;
    background: var(--bg2); border-bottom: 1px solid var(--border);
    flex-shrink: 0;
  }
  .back-btn {
    color: var(--text2); font-size: 1.1rem; font-weight: 600;
    background: none; border: none; cursor: pointer; padding: 4px 8px;
    border-radius: 6px;
  }
  .back-btn:hover { background: var(--bg3); }
  .setlist-name { flex: 1; font-weight: 600; font-size: 0.9rem; color: var(--text2); }
  .ctrl-btn {
    background: var(--bg3); border: 1px solid var(--border); border-radius: 6px;
    padding: 4px 10px; font-size: 0.8rem; font-weight: 700; color: var(--text);
    cursor: pointer;
  }

  .song-info-bar {
    display: flex; align-items: center; justify-content: space-between;
    padding: 0.75rem 1.25rem;
    background: rgba(0,0,0,0.3); border-bottom: 1px solid var(--border);
    flex-shrink: 0;
  }
  .song-num { color: var(--text3); font-size: 0.8rem; margin-right: 10px; font-family: 'DM Mono', monospace; }
  .song-title-perf { font-size: 1.05rem; }
  .song-artist-perf { color: var(--text2); font-size: 0.85rem; margin-left: 8px; }

  .lyrics-area {
    flex: 1; overflow-y: auto; padding: 1.5rem 1.75rem;
  }
  .lyrics-text {
    font-family: 'DM Mono', monospace;
    white-space: pre-wrap; line-height: 1.9;
    color: var(--lyrics-text);
    font-size: inherit;
  }

  .perf-footer {
    flex-shrink: 0; padding: 0.75rem 1rem;
    background: var(--bg2); border-top: 1px solid var(--border);
    display: flex; align-items: center; justify-content: space-between; gap: 12px;
  }
  .song-pills { display: flex; gap: 6px; flex-wrap: nowrap; overflow-x: auto; flex: 1; }
  .pill {
    min-width: 32px; height: 32px; border-radius: 6px;
    background: var(--bg3); border: 1px solid var(--border);
    color: var(--text2); font-size: 0.78rem; font-weight: 600; cursor: pointer;
    flex-shrink: 0;
  }
  .pill.active { background: var(--accent); border-color: var(--accent); color: #fff; }
  .nav-btns { display: flex; gap: 8px; flex-shrink: 0; }
  .nav-btn {
    padding: 0.5rem 1.1rem; border-radius: 8px;
    background: var(--bg3); border: 1px solid var(--border);
    color: var(--text); font-weight: 500; font-size: 0.875rem; cursor: pointer;
  }
  .nav-btn:hover:not(:disabled) { background: var(--bg4); }
  .nav-btn:disabled { opacity: 0.35; cursor: not-allowed; }

  .center {
    display: flex; align-items: center; justify-content: center;
    height: 100dvh; color: var(--text2); gap: 12px;
  }
  .error { color: var(--error); }
</style>

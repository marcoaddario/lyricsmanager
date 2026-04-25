<script lang="ts">
  import { onMount } from 'svelte';
  import { api } from '$lib/services/api';
  import { toasts } from '$lib/stores';

  let libraries: any[] = [];
  let loading = true;

  onMount(async () => {
    try { libraries = await api.libraries.list(); } catch (e: any) { toasts.add(e.message, 'error'); }
    loading = false;
  });

  async function deleteLib(id: number, name: string) {
    if (!confirm(`Delete library "${name}" and all its songs?`)) return;
    try {
      await api.libraries.delete(id);
      libraries = libraries.filter(l => l.id !== id);
      toasts.add('Library deleted', 'success');
    } catch (e: any) { toasts.add(e.message, 'error'); }
  }
</script>

<svelte:head><title>All Libraries — Admin</title></svelte:head>

<div style="margin-bottom:1.5rem">
  <div style="color:var(--text3);font-size:0.75rem;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:4px">Admin</div>
  <h1>All Libraries</h1>
</div>

{#if loading}
  <p style="color:var(--text2)">Loading…</p>
{:else}
  <div class="card" style="padding:0;overflow:hidden">
    <table class="lib-table">
      <thead>
        <tr>
          <th>Library</th>
          <th>Type</th>
          <th>Songs</th>
          <th>Owner</th>
          <th>Created</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        {#each libraries as lib}
          <tr>
            <td>
              <a href="/libraries/{lib.id}" style="font-weight:500;color:var(--text)">{lib.name}</a>
              {#if lib.description}
                <div style="color:var(--text3);font-size:0.75rem;margin-top:2px">{lib.description}</div>
              {/if}
            </td>
            <td>
              {#if lib.is_global}
                <span class="badge badge-success">global</span>
              {:else}
                <span class="badge" style="background:var(--bg3);color:var(--text2)">personal</span>
              {/if}
            </td>
            <td style="color:var(--text2)">{lib.song_count}</td>
            <td style="color:var(--text3);font-size:0.82rem">
              {lib.owner_id ? `#${lib.owner_id}` : '—'}
            </td>
            <td style="color:var(--text3);font-size:0.8rem">{new Date(lib.created_at).toLocaleDateString()}</td>
            <td>
              <div style="display:flex;gap:6px">
                <a href="/libraries/{lib.id}" class="btn btn-ghost btn-sm">Open</a>
                <button class="btn btn-ghost btn-sm" style="color:var(--error)"
                  on:click={() => deleteLib(lib.id, lib.name)}>Delete</button>
              </div>
            </td>
          </tr>
        {/each}
      </tbody>
    </table>
  </div>
{/if}

<style>
  .lib-table { width: 100%; border-collapse: collapse; font-size: 0.875rem; }
  .lib-table th {
    text-align: left; padding: 0.75rem 1rem;
    background: var(--bg3); color: var(--text3);
    font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.06em;
    border-bottom: 1px solid var(--border);
  }
  .lib-table td {
    padding: 0.75rem 1rem; border-bottom: 1px solid var(--border); vertical-align: middle;
  }
  .lib-table tbody tr:last-child td { border-bottom: none; }
  .lib-table tbody tr:hover td { background: var(--bg3); }
</style>

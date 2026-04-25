<script lang="ts">
  import '../app.css';
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
  import { user, theme, isAdmin, isOnline, toasts } from '$lib/stores';
  import { api } from '$lib/services/api';
  import Sidebar from '$lib/components/Sidebar.svelte';
  import Toast from '$lib/components/Toast.svelte';

  const PUBLIC_ROUTES = ['/login'];
  let sidebarOpen = false;
  let loading = true;

  onMount(async () => {
    theme.init();
    try {
      const me = await api.auth.me();
      user.set(me);
    } catch {
      user.set(null);
    }
    loading = false;
  });

  $: if (!loading) {
    const isPublic = PUBLIC_ROUTES.some(r => $page.url.pathname.startsWith(r));
    if (!$user && !isPublic) goto('/login');
    if ($user && $page.url.pathname === '/login') goto('/');
  }
</script>

{#if !$isOnline}
  <div class="offline-banner">⚠ No internet connection — using cached data</div>
{/if}

<Toast />

{#if loading}
  <div style="display:flex;align-items:center;justify-content:center;height:100dvh;color:var(--text2)">Loading…</div>
{:else if $user}
  <div class="app-shell">
    <!-- Topbar (mobile) -->
    <header style="
      grid-column: 1/-1; grid-row:1;
      display:flex; align-items:center; gap:12px;
      padding: 0 1rem;
      background: var(--bg2); border-bottom: 1px solid var(--border);
    ">
      <button class="btn btn-ghost btn-sm" style="display:none" class:show-mobile={true}
        on:click={() => sidebarOpen = !sidebarOpen} aria-label="Menu">☰</button>
      <span style="font-weight:600;font-size:1rem;letter-spacing:-0.01em">🎵 Lyrics Manager</span>
      <span style="flex:1"/>
      <span class="badge badge-accent" style="font-size:0.65rem">{$user.display_name || $user.username}</span>
      {#if $isAdmin}<span class="badge badge-success" style="font-size:0.65rem">admin</span>{/if}
    </header>

    <Sidebar bind:open={sidebarOpen} />

    <main style="grid-column:2;grid-row:2;overflow-y:auto;padding:1.5rem;background:var(--bg)">
      <slot />
    </main>
  </div>
{:else}
  <slot />
{/if}

<style>
  @media (max-width: 768px) {
    :global(.app-shell > main) { grid-column: 1 !important; }
    header button { display: flex !important; }
  }
</style>

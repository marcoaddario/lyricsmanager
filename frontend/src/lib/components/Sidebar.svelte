<script lang="ts">
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
  import { user, isAdmin, theme } from '$lib/stores';
  import { api } from '$lib/services/api';

  export let open = false;

  function logout() {
    api.auth.logout();
    user.set(null);
    goto('/login');
  }

  $: path = $page.url.pathname;

  const navItems = [
    { href: '/', icon: '🏠', label: 'Dashboard' },
    { href: '/setlists', icon: '📋', label: 'Set Lists' },
    { href: '/libraries', icon: '📚', label: 'Libraries' },
   
    { href: '/settings', icon: '⚙️', label: 'Settings' },
  ];

  const adminItems = [
    { href: '/admin/users', icon: '👥', label: 'Users' },
    { href: '/admin/libraries', icon: '🗄️', label: 'All Libraries' },
    { href: '/admin/storage', icon: '💾', label: 'Storage' },
  ];
</script>

<nav class="sidebar" class:open
  style="
    grid-column:1; grid-row:2;
    display:flex; flex-direction:column;
    background:var(--bg2); border-right:1px solid var(--border);
    padding: 1rem 0;
    overflow-y:auto;
  "
>
  {#if open}
    <button class="btn btn-ghost btn-sm" style="margin:0 1rem 1rem;align-self:flex-end"
      on:click={() => open = false}>✕</button>
  {/if}

  <section style="padding: 0 0.75rem">
    {#each navItems as item}
      <a href={item.href} class="nav-link" class:active={path === item.href}
        on:click={() => open = false}>
        <span style="font-size:1rem">{item.icon}</span>
        <span>{item.label}</span>
      </a>
    {/each}
  </section>

  {#if $isAdmin}
    <div style="margin:1.25rem 0.75rem 0.5rem;font-size:0.7rem;font-weight:600;text-transform:uppercase;letter-spacing:0.08em;color:var(--text3)">
      Admin
    </div>
    <section style="padding: 0 0.75rem">
      {#each adminItems as item}
        <a href={item.href} class="nav-link" class:active={path.startsWith(item.href)}
          on:click={() => open = false}>
          <span style="font-size:1rem">{item.icon}</span>
          <span>{item.label}</span>
        </a>
      {/each}
    </section>
  {/if}

  <div style="flex:1"/>

  <!-- Theme picker -->
  <div style="padding:0 0.75rem 0.75rem">
    <div style="font-size:0.7rem;font-weight:600;text-transform:uppercase;letter-spacing:0.08em;color:var(--text3);margin-bottom:0.5rem">
      Theme
    </div>
    <div style="display:flex;gap:6px;flex-wrap:wrap">
      {#each theme.themes as t}
        <button
          class="theme-dot"
          class:active={$theme === t}
          title={t}
          on:click={() => theme.set(t)}>
          {t.slice(0,1).toUpperCase()}
        </button>
      {/each}
    </div>
  </div>

  <div style="padding:0 0.75rem 1rem;border-top:1px solid var(--border);padding-top:0.75rem;margin-top:0.25rem">
    <button class="btn btn-ghost" style="width:100%;justify-content:flex-start" on:click={logout}>
      🚪 Sign out
    </button>
  </div>
</nav>

<style>
  .nav-link {
    display: flex; align-items: center; gap: 10px;
    padding: 0.5rem 0.75rem; border-radius: 8px;
    color: var(--text2); font-size: 0.875rem; font-weight: 500;
    transition: background 0.12s, color 0.12s;
    margin-bottom: 2px;
  }
  .nav-link:hover { background: var(--bg3); color: var(--text); }
  .nav-link.active { background: var(--accent-glow); color: var(--accent); }

  .theme-dot {
    width: 28px; height: 28px; border-radius: 6px;
    font-size: 0.7rem; font-weight: 700;
    border: 2px solid transparent;
    background: var(--bg4); color: var(--text2);
    transition: all 0.15s;
  }
  .theme-dot.active { border-color: var(--accent); color: var(--accent); }
  .theme-dot:hover { border-color: var(--border2); }
</style>
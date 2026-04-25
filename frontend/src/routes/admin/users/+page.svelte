<script lang="ts">
  import { onMount } from 'svelte';
  import { api } from '$lib/services/api';
  import { toasts } from '$lib/stores';

  let users: any[] = [];
  let loading = true;
  let showCreate = false;
  let form = { email: '', username: '', password: '', display_name: '', is_admin: false };
  let saving = false;

  let editingUser: any = null; // null = not editing, user object = editing
  let editForm = { email: '', username: '', display_name: '', is_admin: false };

  onMount(async () => {
    try { users = await api.users.list(); } catch (e: any) { toasts.add(e.message, 'error'); }
    loading = false;
  });

  async function createUser() {
    saving = true;
    try {
      const u = await api.users.create(form);
      users = [u, ...users];
      showCreate = false;
      form = { email: '', username: '', password: '', display_name: '', is_admin: false };
      toasts.add('User created', 'success');
    } catch (e: any) { toasts.add(e.message, 'error'); }
    finally { saving = false; }
  }

  async function toggleActive(u: any) {
    try {
      const updated = await api.users.update(u.id, { is_active: !u.is_active });
      users = users.map(x => x.id === updated.id ? updated : x);
    } catch (e: any) { toasts.add(e.message, 'error'); }
  }

  async function toggleAdmin(u: any) {
    try {
      const updated = await api.users.update(u.id, { is_admin: !u.is_admin });
      users = users.map(x => x.id === updated.id ? updated : x);
    } catch (e: any) { toasts.add(e.message, 'error'); }
  }

  async function deleteUser(id: number) {
    if (!confirm('Delete this user and all their data?')) return;
    try {
      await api.users.delete(id);
      users = users.filter(u => u.id !== id);
      toasts.add('User deleted', 'success');
    } catch (e: any) { toasts.add(e.message, 'error'); }
  }

  function openEdit(user: any) {
    editingUser = user;
    editForm = {
      email: user.email,
      username: user.username,
      display_name: user.display_name || '',
      is_admin: user.is_admin
    };
  }

  function closeEdit() {
    editingUser = null;
  }

  async function saveEdit() {
    saving = true;
    try {
      const updated = await api.users.update(editingUser.id, {
        email: editForm.email,
        username: editForm.username,
        display_name: editForm.display_name || undefined,
        is_admin: editForm.is_admin
      });
      users = users.map(u => u.id === updated.id ? updated : u);
      editingUser = null;
      toasts.add('User updated', 'success');
    } catch (e: any) { toasts.add(e.message, 'error'); }
    finally { saving = false; }
  }
</script>

<svelte:head><title>Users — Admin</title></svelte:head>

<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:1.5rem">
  <div>
    <div style="color:var(--text3);font-size:0.75rem;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:4px">Admin</div>
    <h1>Users</h1>
  </div>
  <button class="btn btn-primary" on:click={() => showCreate = !showCreate}>+ New user</button>
</div>

{#if showCreate}
  <div class="card" style="margin-bottom:1.5rem">
    <h3 style="margin-bottom:1rem">Create user</h3>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:0.75rem">
      <div class="field">
        <label>Email *</label>
        <input class="input" type="email" bind:value={form.email} />
      </div>
      <div class="field">
        <label>Username *</label>
        <input class="input" bind:value={form.username} />
      </div>
      <div class="field">
        <label>Password *</label>
        <input class="input" type="password" bind:value={form.password} />
      </div>
      <div class="field">
        <label>Display name</label>
        <input class="input" bind:value={form.display_name} />
      </div>
    </div>
    <div style="display:flex;gap:8px;align-items:center;margin-bottom:1rem">
      <input type="checkbox" id="is_admin" bind:checked={form.is_admin} />
      <label for="is_admin" style="font-size:0.875rem;color:var(--text2)">Admin user</label>
    </div>
    <div style="display:flex;gap:8px">
      <button class="btn btn-primary" disabled={saving || !form.email || !form.username || !form.password}
        on:click={createUser}>{saving ? 'Creating…' : 'Create user'}</button>
      <button class="btn btn-ghost" on:click={() => showCreate = false}>Cancel</button>
    </div>
  </div>
{/if}

{#if loading}
  <p style="color:var(--text2)">Loading…</p>
{:else}
  <div class="card" style="padding:0;overflow:hidden">
    <table class="user-table">
      <thead>
        <tr>
          <th>User</th>
          <th>Email</th>
          <th>Role</th>
          <th>Status</th>
          <th>Joined</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        {#each users as u}
          {#if editingUser?.id === u.id}
            <tr>
              <td colspan="6" style="padding:1rem">
                <div style="display:grid;grid-template-columns:1fr 1fr;gap:0.75rem;margin-bottom:1rem">
                  <div class="field">
                    <label>Email *</label>
                    <input class="input" type="email" bind:value={editForm.email} />
                  </div>
                  <div class="field">
                    <label>Username *</label>
                    <input class="input" bind:value={editForm.username} />
                  </div>
                  <div class="field">
                    <label>Display name</label>
                    <input class="input" bind:value={editForm.display_name} />
                  </div>
                  <div></div>
                </div>
                <div style="display:flex;gap:8px;align-items:center;margin-bottom:1rem">
                  <input type="checkbox" id="edit_is_admin_{u.id}" bind:checked={editForm.is_admin} />
                  <label for="edit_is_admin_{u.id}" style="font-size:0.875rem;color:var(--text2)">Admin user</label>
                </div>
                <div style="display:flex;gap:8px">
                  <button class="btn btn-primary" disabled={saving || !editForm.email || !editForm.username}
                    on:click={saveEdit}>{saving ? 'Saving…' : 'Save changes'}</button>
                  <button class="btn btn-ghost" on:click={closeEdit}>Cancel</button>
                </div>
              </td>
            </tr>
          {:else}
            <tr class:inactive={!u.is_active}>
              <td>
                <div style="font-weight:500">{u.display_name || u.username}</div>
                <div style="color:var(--text3);font-size:0.75rem">@{u.username}</div>
              </td>
              <td style="color:var(--text2);font-size:0.85rem">{u.email}</td>
              <td>
                {#if u.is_admin}
                  <span class="badge badge-success">admin</span>
                {:else}
                  <span class="badge" style="background:var(--bg3);color:var(--text2)">user</span>
                {/if}
              </td>
              <td>
                {#if u.is_active}
                  <span class="badge badge-success">active</span>
                {:else}
                  <span class="badge badge-error">inactive</span>
                {/if}
              </td>
              <td style="color:var(--text3);font-size:0.8rem">{new Date(u.created_at).toLocaleDateString()}</td>
              <td>
                <div style="display:flex;gap:4px;flex-wrap:wrap">
                  <button class="btn btn-ghost btn-sm" on:click={() => openEdit(u)}>Edit</button>
                  <button class="btn btn-ghost btn-sm" on:click={() => toggleAdmin(u)}>
                    {u.is_admin ? 'Revoke admin' : 'Make admin'}
                  </button>
                  <button class="btn btn-ghost btn-sm" on:click={() => toggleActive(u)}>
                    {u.is_active ? 'Disable' : 'Enable'}
                  </button>
                  <button class="btn btn-ghost btn-sm" style="color:var(--error)"
                    on:click={() => deleteUser(u.id)}>Delete</button>
                </div>
              </td>
            </tr>
          {/if}
        {/each}
      </tbody>
    </table>
  </div>
{/if}

<style>
  .user-table { width: 100%; border-collapse: collapse; font-size: 0.875rem; }
  .user-table th {
    text-align: left; padding: 0.75rem 1rem;
    background: var(--bg3); color: var(--text3);
    font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.06em;
    border-bottom: 1px solid var(--border);
  }
  .user-table td {
    padding: 0.75rem 1rem;
    border-bottom: 1px solid var(--border);
    vertical-align: middle;
  }
  .user-table tbody tr:last-child td { border-bottom: none; }
  .user-table tbody tr:hover td { background: var(--bg3); }
  .inactive td { opacity: 0.55; }
</style>

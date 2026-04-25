<script lang="ts">
  import { toasts } from '$lib/stores';
</script>

<div class="toast-container">
  {#each $toasts as t (t.id)}
    <div class="toast toast-{t.type}" role="alert">
      {t.message}
    </div>
  {/each}
</div>

<style>
  .toast-container {
    position: fixed; bottom: 1.5rem; right: 1.5rem;
    display: flex; flex-direction: column; gap: 8px;
    z-index: 500; pointer-events: none;
  }
  .toast {
    padding: 0.65rem 1.1rem; border-radius: 10px;
    font-size: 0.875rem; font-weight: 500;
    max-width: 300px; animation: slide-in 0.2s ease;
    pointer-events: all;
  }
  .toast-success { background: var(--success); color: #000; }
  .toast-error { background: var(--error); color: #fff; }
  .toast-info { background: var(--bg4); color: var(--text); border: 1px solid var(--border2); }

  @keyframes slide-in {
    from { transform: translateX(120%); opacity: 0; }
    to { transform: translateX(0); opacity: 1; }
  }
</style>

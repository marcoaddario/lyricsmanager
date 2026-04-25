import { writable, derived } from 'svelte/store';
import { browser } from '$app/environment';

// ── Auth store ────────────────────────────────────────────────────────────────
function createAuthStore() {
  const { subscribe, set, update } = writable<any>(null);
  return {
    subscribe,
    set,
    update,
    logout() {
      if (browser) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
      }
      set(null);
    }
  };
}
export const user = createAuthStore();
export const isAdmin = derived(user, ($u) => $u?.is_admin === true);

// ── Theme store ───────────────────────────────────────────────────────────────
const THEMES = ['dark', 'light', 'midnight', 'forest', 'amber'] as const;
export type Theme = typeof THEMES[number];

function createThemeStore() {
  const initial: Theme = browser
    ? ((localStorage.getItem('theme') as Theme) || 'dark')
    : 'dark';

  const { subscribe, set } = writable<Theme>(initial);

  function applyTheme(t: Theme) {
    if (browser) {
      localStorage.setItem('theme', t);
      document.documentElement.setAttribute('data-theme', t);
    }
    set(t);
  }

  return {
    subscribe,
    set: applyTheme,
    init() {
      if (browser) {
        const saved = (localStorage.getItem('theme') as Theme) || 'dark';
        document.documentElement.setAttribute('data-theme', saved);
        set(saved);
      }
    },
    themes: THEMES
  };
}
export const theme = createThemeStore();

// ── Online / offline status ───────────────────────────────────────────────────
function createNetworkStore() {
  const { subscribe, set } = writable(browser ? navigator.onLine : true);
  if (browser) {
    window.addEventListener('online', () => set(true));
    window.addEventListener('offline', () => set(false));
  }
  return { subscribe };
}
export const isOnline = createNetworkStore();

// ── Toast notifications ───────────────────────────────────────────────────────
interface Toast { id: string; type: 'success' | 'error' | 'info'; message: string }

function createToastStore() {
  const { subscribe, update } = writable<Toast[]>([]);

  function add(message: string, type: Toast['type'] = 'info') {
    const id = Math.random().toString(36).slice(2);
    update(ts => [...ts, { id, type, message }]);
    setTimeout(() => update(ts => ts.filter(t => t.id !== id)), 3500);
  }

  return {
    subscribe,
    add,
    success: (msg: string) => add(msg, 'success'),
    error: (msg: string) => add(msg, 'error')
  };
}
export const toasts = createToastStore();
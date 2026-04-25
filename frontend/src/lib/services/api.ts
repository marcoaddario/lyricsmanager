import { browser } from '$app/environment';
import { goto } from '$app/navigation';

const BASE = typeof window !== 'undefined'
  ? (import.meta.env.PUBLIC_API_URL || '/api')
  : '/api';

function getTokens() {
  if (!browser) return { access: null, refresh: null };
  return {
    access: localStorage.getItem('access_token'),
    refresh: localStorage.getItem('refresh_token')
  };
}

function setTokens(access: string, refresh: string) {
  localStorage.setItem('access_token', access);
  localStorage.setItem('refresh_token', refresh);
}

export function clearTokens() {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
}

async function refreshTokens(): Promise<boolean> {
  const { refresh } = getTokens();
  if (!refresh) return false;
  try {
    const res = await fetch(`${BASE}/auth/refresh`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: refresh })
    });
    if (!res.ok) return false;
    const data = await res.json();
    setTokens(data.access_token, data.refresh_token);
    return true;
  } catch {
    return false;
  }
}

async function request(path: string, init: RequestInit = {}, retry = true): Promise<any> {
  const { access } = getTokens();
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(init.headers as Record<string, string>)
  };
  if (access) headers['Authorization'] = `Bearer ${access}`;

  const res = await fetch(`${BASE}${path}`, { ...init, headers });

  if (res.status === 401 && retry) {
    const ok = await refreshTokens();
    if (ok) return request(path, init, false);
    clearTokens();
    goto('/login');
    throw new Error('Session expired');
  }

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Request failed' }));
    throw new Error(err.detail || 'Request failed');
  }

  if (res.status === 204) return null;
  return res.json();
}

// ── Auth ──────────────────────────────────────────────────────────────────────
export const api = {
  auth: {
    login: async (identifier: string, password: string) => {
      const data = await request('/auth/login', {
        method: 'POST', body: JSON.stringify({ identifier, password })
      });
      setTokens(data.access_token, data.refresh_token);
      return data;
    },
    me: () => request('/auth/me'),
    logout: () => clearTokens()
  },

  // ── Users ─────────────────────────────────────────────────────────────────
  users: {
    list: () => request('/users/'),
    create: (body: any) => request('/users/', { method: 'POST', body: JSON.stringify(body) }),
    get: (id: number) => request(`/users/${id}`),
    update: (id: number, body: any) => request(`/users/${id}`, { method: 'PATCH', body: JSON.stringify(body) }),
    delete: (id: number) => request(`/users/${id}`, { method: 'DELETE' }),
    changePassword: (id: number, body: any) => request(`/users/${id}/change-password`, { method: 'POST', body: JSON.stringify(body) })
  },

  // ── Libraries ─────────────────────────────────────────────────────────────
  libraries: {
    list: () => request('/libraries/'),
    create: (body: any) => request('/libraries/', { method: 'POST', body: JSON.stringify(body) }),
    get: (id: number) => request(`/libraries/${id}`),
    update: (id: number, body: any) => request(`/libraries/${id}`, { method: 'PATCH', body: JSON.stringify(body) }),
    delete: (id: number) => request(`/libraries/${id}`, { method: 'DELETE' })
  },

  // ── Songs ─────────────────────────────────────────────────────────────────
  songs: {
    list: (libraryId: number, q?: string) =>
      request(`/libraries/${libraryId}/songs/${q ? `?q=${encodeURIComponent(q)}` : ''}`),
    create: (libraryId: number, body: any) =>
      request(`/libraries/${libraryId}/songs/`, { method: 'POST', body: JSON.stringify(body) }),
    get: (libraryId: number, songId: number) =>
      request(`/libraries/${libraryId}/songs/${songId}`),
    update: (libraryId: number, songId: number, body: any) =>
      request(`/libraries/${libraryId}/songs/${songId}`, { method: 'PATCH', body: JSON.stringify(body) }),
    delete: (libraryId: number, songId: number) =>
      request(`/libraries/${libraryId}/songs/${songId}`, { method: 'DELETE' })
  },

  // ── Setlists ──────────────────────────────────────────────────────────────
  setlists: {
    list: () => request('/setlists/'),
    create: (body: any) => request('/setlists/', { method: 'POST', body: JSON.stringify(body) }),
    get: (id: number) => request(`/setlists/${id}`),
    update: (id: number, body: any) => request(`/setlists/${id}`, { method: 'PATCH', body: JSON.stringify(body) }),
    delete: (id: number) => request(`/setlists/${id}`, { method: 'DELETE' }),
    replaceItems: (id: number, items: any[]) =>
      request(`/setlists/${id}/items`, { method: 'PUT', body: JSON.stringify(items) }),
    download: (id: number) => request(`/setlists/${id}/download`)
  },

  // ── Admin ─────────────────────────────────────────────────────────────────
  admin: {
    storage: () => request('/admin/storage')
  }
};

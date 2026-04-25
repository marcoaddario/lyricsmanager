import { openDB, type IDBPDatabase } from 'idb';

const DB_NAME = 'lyricsmanager';
const DB_VERSION = 1;

interface SetlistRecord {
  id: number;
  name: string;
  downloadedAt: number;
  data: any;
}

let _db: IDBPDatabase | null = null;

async function getDb(): Promise<IDBPDatabase> {
  if (_db) return _db;
  _db = await openDB(DB_NAME, DB_VERSION, {
    upgrade(db) {
      if (!db.objectStoreNames.contains('setlists')) {
        const store = db.createObjectStore('setlists', { keyPath: 'id' });
        store.createIndex('downloadedAt', 'downloadedAt');
      }
      if (!db.objectStoreNames.contains('songs')) {
        db.createObjectStore('songs', { keyPath: 'id' });
      }
      if (!db.objectStoreNames.contains('prefs')) {
        db.createObjectStore('prefs');
      }
    }
  });
  return _db;
}

export const offlineStore = {
  async saveSetlist(setlist: any): Promise<void> {
    const db = await getDb();
    const record: SetlistRecord = {
      id: setlist.id,
      name: setlist.name,
      downloadedAt: Date.now(),
      data: setlist
    };
    await db.put('setlists', record);
    // Also cache individual songs for quick lookup
    for (const item of setlist.items || []) {
      await db.put('songs', item.song);
    }
  },

  async getSetlist(id: number): Promise<any | null> {
    const db = await getDb();
    const record = await db.get('setlists', id) as SetlistRecord | undefined;
    return record?.data ?? null;
  },

  async listSetlists(): Promise<SetlistRecord[]> {
    const db = await getDb();
    return db.getAll('setlists');
  },

  async deleteSetlist(id: number): Promise<void> {
    const db = await getDb();
    await db.delete('setlists', id);
  },

  async getSong(id: number): Promise<any | null> {
    const db = await getDb();
    return db.get('songs', id) ?? null;
  },

  async setPref(key: string, value: any): Promise<void> {
    const db = await getDb();
    await db.put('prefs', value, key);
  },

  async getPref(key: string): Promise<any> {
    const db = await getDb();
    return db.get('prefs', key);
  },

  async isSetlistDownloaded(id: number): Promise<boolean> {
    const db = await getDb();
    const record = await db.get('setlists', id);
    return !!record;
  },

  async getStorageEstimate(): Promise<{ usageMB: number; quotaMB: number }> {
    if (!navigator.storage?.estimate) return { usageMB: 0, quotaMB: 0 };
    const { usage = 0, quota = 0 } = await navigator.storage.estimate();
    return { usageMB: Math.round(usage / 1024 / 1024), quotaMB: Math.round(quota / 1024 / 1024) };
  }
};

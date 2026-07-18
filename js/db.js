// IndexedDB 简易封装：catches（钓获日志）、gear（装备）

const DB_NAME = 'lure-companion';
const DB_VERSION = 1;
let dbPromise = null;

function openDB() {
  if (dbPromise) return dbPromise;
  dbPromise = new Promise((resolve, reject) => {
    const req = indexedDB.open(DB_NAME, DB_VERSION);
    req.onupgradeneeded = () => {
      const db = req.result;
      if (!db.objectStoreNames.contains('catches')) {
        db.createObjectStore('catches', { keyPath: 'id' });
      }
      if (!db.objectStoreNames.contains('gear')) {
        db.createObjectStore('gear', { keyPath: 'id' });
      }
    };
    req.onsuccess = () => resolve(req.result);
    req.onerror = () => reject(req.error);
  });
  return dbPromise;
}

function tx(storeName, mode, fn) {
  return openDB().then(
    (db) =>
      new Promise((resolve, reject) => {
        const t = db.transaction(storeName, mode);
        const store = t.objectStore(storeName);
        const result = fn(store);
        t.oncomplete = () => resolve(result.result !== undefined ? result.result : result);
        t.onerror = () => reject(t.error);
      })
  );
}

export function getAll(storeName) {
  return tx(storeName, 'readonly', (store) => store.getAll()).then((r) => r || []);
}

export function put(storeName, value) {
  return tx(storeName, 'readwrite', (store) => store.put(value));
}

export function remove(storeName, id) {
  return tx(storeName, 'readwrite', (store) => store.delete(id));
}

export function uid() {
  return Date.now().toString(36) + Math.random().toString(36).slice(2, 8);
}

// 导出 / 导入备份
export async function exportBackup() {
  const [catches, gear] = await Promise.all([getAll('catches'), getAll('gear')]);
  return { app: 'lure-companion', version: 1, exportedAt: new Date().toISOString(), catches, gear };
}

export async function importBackup(data) {
  if (!data || data.app !== 'lure-companion') throw new Error('不是有效的备份文件');
  for (const c of data.catches || []) await put('catches', c);
  for (const g of data.gear || []) await put('gear', g);
  return { catches: (data.catches || []).length, gear: (data.gear || []).length };
}

// 图片压缩为 dataURL（最长边 900px，JPEG 0.8）
export function compressImage(file) {
  return new Promise((resolve, reject) => {
    const img = new Image();
    const url = URL.createObjectURL(file);
    img.onload = () => {
      URL.revokeObjectURL(url);
      const max = 900;
      let { width, height } = img;
      if (width > max || height > max) {
        const scale = max / Math.max(width, height);
        width = Math.round(width * scale);
        height = Math.round(height * scale);
      }
      const canvas = document.createElement('canvas');
      canvas.width = width;
      canvas.height = height;
      canvas.getContext('2d').drawImage(img, 0, 0, width, height);
      resolve(canvas.toDataURL('image/jpeg', 0.8));
    };
    img.onerror = () => {
      URL.revokeObjectURL(url);
      reject(new Error('图片读取失败'));
    };
    img.src = url;
  });
}

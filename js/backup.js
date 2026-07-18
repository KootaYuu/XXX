// 备份导出 / 导入 + 备份提醒
import { exportBackup, importBackup } from './db.js';
import { toast, fmtDate } from './ui.js';

const KEY = 'lure.lastBackupAt';

export async function exportToFile() {
  const data = await exportBackup();
  const blob = new Blob([JSON.stringify(data)], { type: 'application/json' });
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = `路亚宝典备份-${fmtDate(new Date().toISOString())}.json`;
  a.click();
  URL.revokeObjectURL(a.href);
  localStorage.setItem(KEY, new Date().toISOString());
  toast('已导出备份文件');
}

export async function importFromFile(file) {
  const data = JSON.parse(await file.text());
  const n = await importBackup(data);
  toast(`已导入 ${n.catches} 条日志、${n.gear} 件装备`);
}

export function lastBackupAt() {
  return localStorage.getItem(KEY);
}

export function lastBackupText() {
  const t = lastBackupAt();
  return t ? fmtDate(t) : '从未备份';
}

// 有 5 条以上记录且超过 30 天未备份时提醒
export function needBackupNudge(catchCount) {
  if (catchCount < 5) return false;
  const t = lastBackupAt();
  if (!t) return true;
  return Date.now() - Date.parse(t) > 30 * 24 * 3600 * 1000;
}

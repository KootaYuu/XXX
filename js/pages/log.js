// 钓获日志页
import { SPECIES, SPECIES_MAP, LURES, LURE_MAP } from '../data.js';
import { getAll, put, remove, uid, compressImage, exportBackup, importBackup } from '../db.js';
import { esc, toast, openSheet, confirmDialog, fmtDate } from '../ui.js';

export async function renderLog(el) {
  const catches = (await getAll('catches')).sort((a, b) => (b.date || '').localeCompare(a.date || ''));

  el.innerHTML = `
    <header class="page-head">
      <h1>📓 钓获日志</h1>
      <p class="sub">共 ${catches.length} 条记录 · 解锁 ${new Set(catches.map((c) => c.speciesId)).size} 种鱼</p>
    </header>
    <div class="btn-row">
      <button id="add-catch" class="btn primary">＋ 记一条</button>
      <button id="export-data" class="btn">导出备份</button>
      <button id="import-data" class="btn">导入</button>
      <input type="file" id="import-file" accept="application/json" hidden>
    </div>
    <section id="catch-list">
      ${catches.length === 0 ? '<p class="empty">还没有记录，中鱼了就来记一条吧 🎣</p>' : catches.map(catchCard).join('')}
    </section>
  `;

  el.querySelector('#add-catch').addEventListener('click', () => openForm(null, () => renderLog(el)));

  el.querySelector('#export-data').addEventListener('click', async () => {
    const data = await exportBackup();
    const blob = new Blob([JSON.stringify(data)], { type: 'application/json' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = `路亚宝典备份-${fmtDate(new Date().toISOString())}.json`;
    a.click();
    URL.revokeObjectURL(a.href);
    toast('已导出备份文件');
  });

  const fileInput = el.querySelector('#import-file');
  el.querySelector('#import-data').addEventListener('click', () => fileInput.click());
  fileInput.addEventListener('change', async () => {
    const file = fileInput.files[0];
    if (!file) return;
    try {
      const data = JSON.parse(await file.text());
      const n = await importBackup(data);
      toast(`已导入 ${n.catches} 条日志、${n.gear} 件装备`);
      renderLog(el);
    } catch (err) {
      toast('导入失败：' + err.message);
    }
  });

  el.querySelector('#catch-list').addEventListener('click', async (e) => {
    const card = e.target.closest('.catch-card');
    if (!card) return;
    const record = catches.find((c) => c.id === card.dataset.id);
    if (!record) return;
    if (e.target.closest('.del-btn')) {
      if (await confirmDialog('删除这条记录？')) {
        await remove('catches', record.id);
        toast('已删除');
        renderLog(el);
      }
    } else {
      openForm(record, () => renderLog(el));
    }
  });
}

function catchCard(c) {
  const sp = SPECIES_MAP[c.speciesId];
  const lure = LURE_MAP[c.lureId];
  const size = [c.weight ? `${c.weight} 斤` : '', c.length ? `${c.length} cm` : ''].filter(Boolean).join(' / ');
  return `
    <div class="card catch-card" data-id="${c.id}">
      <div class="catch-row">
        ${c.photo ? `<img class="catch-photo" src="${c.photo}" alt="渔获照片">` : `<div class="catch-photo placeholder">${sp ? sp.emoji : '🐟'}</div>`}
        <div class="catch-info">
          <div class="catch-title">${sp ? sp.emoji + ' ' + esc(sp.name) : esc(c.speciesName || '未知鱼种')}${size ? `<span class="catch-size">${esc(size)}</span>` : ''}</div>
          <div class="catch-meta">${esc(fmtDate(c.date))}${c.spot ? ' · ' + esc(c.spot) : ''}</div>
          <div class="catch-meta">${lure ? lure.emoji + ' ' + esc(lure.name) : ''}${c.weather ? ' · ' + esc(c.weather) : ''}</div>
          ${c.notes ? `<div class="catch-notes">${esc(c.notes)}</div>` : ''}
        </div>
        <button class="del-btn" aria-label="删除">✕</button>
      </div>
    </div>`;
}

function openForm(record, onSaved) {
  const isEdit = !!record;
  const c = record || {
    id: uid(),
    date: new Date().toISOString().slice(0, 10),
    speciesId: '', lureId: '', spot: '', weather: '', weight: '', length: '', notes: '', photo: '',
  };

  openSheet(
    `
    <h2>${isEdit ? '编辑记录' : '记一条渔获'}</h2>
    <form id="catch-form" class="form">
      <label>日期<input type="date" name="date" value="${esc(c.date)}" required></label>
      <label>鱼种
        <select name="speciesId" required>
          <option value="">请选择</option>
          ${SPECIES.map((s) => `<option value="${s.id}" ${s.id === c.speciesId ? 'selected' : ''}>${s.emoji} ${esc(s.name)}</option>`).join('')}
        </select>
      </label>
      <label>拟饵
        <select name="lureId">
          <option value="">不记录</option>
          ${LURES.map((l) => `<option value="${l.id}" ${l.id === c.lureId ? 'selected' : ''}>${l.emoji} ${esc(l.name)}</option>`).join('')}
        </select>
      </label>
      <div class="form-2col">
        <label>重量（斤）<input type="number" step="0.1" min="0" name="weight" value="${esc(c.weight)}" placeholder="选填"></label>
        <label>长度（cm）<input type="number" step="1" min="0" name="length" value="${esc(c.length)}" placeholder="选填"></label>
      </div>
      <label>钓点<input type="text" name="spot" value="${esc(c.spot)}" placeholder="如：西湾大坝左侧桦尖"></label>
      <label>天气<input type="text" name="weather" value="${esc(c.weather)}" placeholder="如：阴 22℃ 微风"></label>
      <label>笔记<textarea name="notes" rows="2" placeholder="手法、标点、心得…">${esc(c.notes)}</textarea></label>
      <label class="photo-label">照片
        <input type="file" name="photo" accept="image/*" capture="environment" hidden>
        <div class="photo-preview" id="photo-preview">${c.photo ? `<img src="${c.photo}" alt="预览">` : '<span>📷 点击拍照 / 选图</span>'}</div>
      </label>
      <div class="btn-row">
        <button type="submit" class="btn primary">保存</button>
        <button type="button" class="btn" id="cancel-btn">取消</button>
      </div>
    </form>
  `,
    (sheet, close) => {
      let photo = c.photo;
      const fileInput = sheet.querySelector('input[name=photo]');
      const preview = sheet.querySelector('#photo-preview');
      preview.addEventListener('click', () => fileInput.click());
      fileInput.addEventListener('change', async () => {
        if (!fileInput.files[0]) return;
        try {
          photo = await compressImage(fileInput.files[0]);
          preview.innerHTML = `<img src="${photo}" alt="预览">`;
        } catch {
          toast('图片处理失败');
        }
      });
      sheet.querySelector('#cancel-btn').addEventListener('click', close);
      sheet.querySelector('#catch-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const fd = new FormData(e.target);
        await put('catches', {
          ...c,
          date: fd.get('date'),
          speciesId: fd.get('speciesId'),
          lureId: fd.get('lureId'),
          weight: fd.get('weight'),
          length: fd.get('length'),
          spot: fd.get('spot').trim(),
          weather: fd.get('weather').trim(),
          notes: fd.get('notes').trim(),
          photo,
        });
        close();
        toast(isEdit ? '已更新' : '已记录，恭喜中鱼！🎉');
        onSaved();
      });
    }
  );
}

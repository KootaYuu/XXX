// 钓获日志页：记录 + 筛选搜索 + 备份
import { LURES, LURE_MAP } from '../data.js';
import { getAll, put, remove, uid, compressImage } from '../db.js';
import { getAllSpecies, openAddSpeciesSheet } from '../species.js';
import { exportToFile, importFromFile, needBackupNudge } from '../backup.js';
import { fetchLocalWeather } from '../weather.js';
import { esc, toast, openSheet, confirmDialog, fmtDate } from '../ui.js';

// 筛选条件跨渲染保留
const filter = { q: '', species: '', lure: '' };

export async function renderLog(el) {
  const [catches, speciesList] = await Promise.all([getAll('catches'), getAllSpecies()]);
  catches.sort((a, b) => (b.date || '').localeCompare(a.date || ''));
  const spMap = Object.fromEntries(speciesList.map((s) => [s.id, s]));

  el.innerHTML = `
    <header class="page-head">
      <h1>📓 钓获日志</h1>
      <p class="sub">共 ${catches.length} 条记录 · 解锁 ${new Set(catches.map((c) => c.speciesId)).size} 种鱼</p>
    </header>
    ${
      needBackupNudge(catches.length)
        ? `<div class="banner" id="backup-banner">
             <span>📦 记录越来越多了，超过 30 天没备份，建议导出保存</span>
             <button class="btn small" id="banner-export">立即导出</button>
           </div>`
        : ''
    }
    <div class="btn-row">
      <button id="add-catch" class="btn primary">＋ 记一条</button>
      <button id="export-data" class="btn">导出备份</button>
      <button id="import-data" class="btn">导入</button>
      <input type="file" id="import-file" accept="application/json" hidden>
    </div>
    <div class="filter-row">
      <input type="search" id="log-search" class="search-input" placeholder="搜钓点 / 笔记 / 鱼种…" value="${esc(filter.q)}">
    </div>
    <div class="filter-row">
      <select id="filter-species">
        <option value="">全部鱼种</option>
        ${speciesList.map((s) => `<option value="${s.id}" ${s.id === filter.species ? 'selected' : ''}>${s.emoji} ${esc(s.name)}</option>`).join('')}
      </select>
      <select id="filter-lure">
        <option value="">全部拟饵</option>
        ${LURES.map((l) => `<option value="${l.id}" ${l.id === filter.lure ? 'selected' : ''}>${l.emoji} ${esc(l.name)}</option>`).join('')}
      </select>
    </div>
    <section id="catch-list"></section>
  `;

  const listEl = el.querySelector('#catch-list');
  const applyFilter = () => {
    const q = filter.q.trim().toLowerCase();
    const shown = catches.filter((c) => {
      if (filter.species && c.speciesId !== filter.species) return false;
      if (filter.lure && c.lureId !== filter.lure) return false;
      if (q) {
        const sp = spMap[c.speciesId];
        const hay = [sp ? sp.name : '', c.speciesName, c.spot, c.notes, c.weather]
          .join(' ')
          .toLowerCase();
        if (!hay.includes(q)) return false;
      }
      return true;
    });
    listEl.innerHTML =
      shown.length > 0
        ? shown.map((c) => catchCard(c, spMap)).join('')
        : catches.length > 0
          ? '<p class="empty">没有符合筛选条件的记录</p>'
          : '<p class="empty">还没有记录，中鱼了就来记一条吧 🎣</p>';
  };
  applyFilter();

  el.querySelector('#log-search').addEventListener('input', (e) => {
    filter.q = e.target.value;
    applyFilter();
  });
  el.querySelector('#filter-species').addEventListener('change', (e) => {
    filter.species = e.target.value;
    applyFilter();
  });
  el.querySelector('#filter-lure').addEventListener('change', (e) => {
    filter.lure = e.target.value;
    applyFilter();
  });

  el.querySelector('#add-catch').addEventListener('click', () =>
    openForm(null, speciesList, () => renderLog(el))
  );

  const doExport = async () => {
    await exportToFile();
    renderLog(el); // 刷新备份提醒条
  };
  el.querySelector('#export-data').addEventListener('click', doExport);
  el.querySelector('#banner-export')?.addEventListener('click', doExport);

  const fileInput = el.querySelector('#import-file');
  el.querySelector('#import-data').addEventListener('click', () => fileInput.click());
  fileInput.addEventListener('change', async () => {
    const file = fileInput.files[0];
    if (!file) return;
    try {
      await importFromFile(file);
      renderLog(el);
    } catch (err) {
      toast('导入失败：' + err.message);
    }
  });

  listEl.addEventListener('click', async (e) => {
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
      openForm(record, speciesList, () => renderLog(el));
    }
  });
}

function catchCard(c, spMap) {
  const sp = spMap[c.speciesId];
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

function speciesOptions(speciesList, selected) {
  return `
    <option value="">请选择</option>
    ${speciesList.map((s) => `<option value="${s.id}" ${s.id === selected ? 'selected' : ''}>${s.emoji} ${esc(s.name)}</option>`).join('')}
    <option value="__add">＋ 新建自定义鱼种…</option>`;
}

function openForm(record, speciesList, onSaved) {
  const isEdit = !!record;
  const c = record || {
    id: uid(),
    date: new Date().toISOString().slice(0, 10),
    speciesId: '', lureId: '', spot: '', weather: '', weight: '', length: '', notes: '', photo: '',
  };
  const localSpecies = [...speciesList];

  openSheet(
    `
    <h2>${isEdit ? '编辑记录' : '记一条渔获'}</h2>
    <form id="catch-form" class="form">
      <label>日期<input type="date" name="date" value="${esc(c.date)}" required></label>
      <label>鱼种
        <select name="speciesId" required>${speciesOptions(localSpecies, c.speciesId)}</select>
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
      <label>天气
        <div class="weather-row">
          <input type="text" name="weather" value="${esc(c.weather)}" placeholder="如：阴 22℃ 微风">
          <button type="button" class="btn" id="auto-weather">📍 自动</button>
        </div>
      </label>
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

      // 鱼种下拉里的「新建自定义鱼种」
      const spSelect = sheet.querySelector('select[name=speciesId]');
      let prevSpecies = c.speciesId;
      spSelect.addEventListener('change', () => {
        if (spSelect.value !== '__add') {
          prevSpecies = spSelect.value;
          return;
        }
        spSelect.value = prevSpecies; // 先复位，等新建成功再选中
        openAddSpeciesSheet((sp) => {
          localSpecies.push(sp);
          spSelect.innerHTML = speciesOptions(localSpecies, sp.id);
          prevSpecies = sp.id;
        });
      });

      // 天气自动获取
      const weatherBtn = sheet.querySelector('#auto-weather');
      const weatherInput = sheet.querySelector('input[name=weather]');
      weatherBtn.addEventListener('click', async () => {
        weatherBtn.disabled = true;
        weatherBtn.textContent = '获取中…';
        try {
          weatherInput.value = await fetchLocalWeather();
        } catch (err) {
          toast(err.message || '天气获取失败');
        } finally {
          weatherBtn.disabled = false;
          weatherBtn.textContent = '📍 自动';
        }
      });

      sheet.querySelector('#cancel-btn').addEventListener('click', close);
      sheet.querySelector('#catch-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const fd = new FormData(e.target);
        const speciesId = fd.get('speciesId');
        const sp = localSpecies.find((s) => s.id === speciesId);
        await put('catches', {
          ...c,
          date: fd.get('date'),
          speciesId,
          speciesName: sp ? sp.name : c.speciesName || '', // 快照，防自定义鱼种被删后显示丢失
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

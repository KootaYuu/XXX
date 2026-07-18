// 鱼类解锁图鉴页：钓获日志里记录过的鱼种自动解锁；支持自定义鱼种
import { LURE_MAP } from '../data.js';
import { getAll } from '../db.js';
import { getAllSpecies, openAddSpeciesSheet, removeCustomSpecies } from '../species.js';
import { esc, openSheet, confirmDialog, toast, fmtDate } from '../ui.js';

export async function renderDex(el) {
  const [catches, speciesList] = await Promise.all([getAll('catches'), getAllSpecies()]);
  const bySpecies = {};
  for (const c of catches) {
    (bySpecies[c.speciesId] ||= []).push(c);
  }
  const unlockedCount = speciesList.filter((s) => bySpecies[s.id]).length;

  el.innerHTML = `
    <header class="page-head">
      <div class="head-row">
        <h1>🐟 鱼类图鉴</h1>
        <button id="add-species" class="btn small">＋ 自定义鱼种</button>
      </div>
      <p class="sub">已解锁 ${unlockedCount} / ${speciesList.length} 种 — 钓到并记录即可解锁</p>
      <div class="dex-progress"><div class="dex-progress-bar" style="width:${(unlockedCount / speciesList.length) * 100}%"></div></div>
    </header>
    <div class="dex-grid">
      ${speciesList.map((s) => {
        const records = bySpecies[s.id];
        const unlocked = !!records;
        // 自定义鱼种是用户自己建的，名称始终可见
        const showName = unlocked || s.custom;
        return `
        <button class="dex-card ${unlocked ? 'unlocked' : 'locked'}" data-id="${s.id}">
          <span class="dex-emoji">${showName ? s.emoji : '❓'}</span>
          <span class="dex-name">${showName ? esc(s.name) : '？？？'}${s.custom ? '<span class="dex-custom-tag">自定义</span>' : ''}</span>
          ${unlocked ? `<span class="dex-count">×${records.length}</span>` : '<span class="dex-count">未解锁</span>'}
        </button>`;
      }).join('')}
    </div>
  `;

  el.querySelector('#add-species').addEventListener('click', () =>
    openAddSpeciesSheet(() => renderDex(el))
  );

  el.querySelector('.dex-grid').addEventListener('click', (e) => {
    const card = e.target.closest('.dex-card');
    if (!card) return;
    const sp = speciesList.find((s) => s.id === card.dataset.id);
    openDetail(sp, bySpecies[sp.id] || [], () => renderDex(el));
  });
}

function openDetail(sp, records, onChanged) {
  const unlocked = records.length > 0;
  const sorted = [...records].sort((a, b) => (a.date || '').localeCompare(b.date || ''));
  const first = sorted[0];
  const best = records.reduce((m, c) => (parseFloat(c.weight) > parseFloat(m?.weight || 0) ? c : m), null);
  const topLures = Object.entries(sp.lures || {})
    .sort((a, b) => b[1] - a[1])
    .slice(0, 3)
    .map(([id]) => LURE_MAP[id])
    .filter(Boolean);

  const showName = unlocked || sp.custom;
  const facts = [
    sp.difficulty ? ['难度', '🔥'.repeat(sp.difficulty)] : null,
    sp.seasons ? ['活跃季节', sp.seasons.join('、')] : null,
    sp.layer ? ['泳层', esc(sp.layer)] : null,
    sp.habitat ? ['栖息环境', esc(sp.habitat)] : null,
    topLures.length ? ['推荐拟饵', topLures.map((l) => `${l.emoji} ${esc(l.name)}`).join('　')] : null,
    sp.tip ? ['攻略', esc(sp.tip)] : null,
  ].filter(Boolean);

  openSheet(
    `
    <div class="dex-detail">
      <div class="dex-detail-head">
        <span class="dex-detail-emoji ${showName ? '' : 'silhouette'}">${sp.emoji}</span>
        <div>
          <h2>${showName ? esc(sp.name) : '？？？'}</h2>
          <p class="sub">${sp.custom ? '自定义鱼种' : unlocked ? esc(sp.latin) : '钓到并记录后解锁完整资料'}</p>
        </div>
      </div>
      ${
        unlocked
          ? `
        <div class="dex-badges">
          <span class="badge">首次解锁 ${esc(fmtDate(first.date))}</span>
          <span class="badge">共 ${records.length} 尾</span>
          ${best && best.weight ? `<span class="badge">最大 ${esc(best.weight)} 斤</span>` : ''}
        </div>`
          : ''
      }
      ${facts.length ? `<dl class="dex-facts">${facts.map(([k, v]) => `<div><dt>${k}</dt><dd>${v}</dd></div>`).join('')}</dl>` : ''}
      ${sp.custom ? '<div class="btn-row" style="margin-top:14px"><button class="btn danger" id="del-species">删除该鱼种</button></div>' : ''}
    </div>
  `,
    (sheet, close) => {
      sheet.querySelector('#del-species')?.addEventListener('click', async () => {
        const warn = records.length
          ? `删除「${sp.name}」？已有的 ${records.length} 条钓获记录会保留，但不再关联图鉴。`
          : `删除「${sp.name}」？`;
        if (await confirmDialog(warn)) {
          await removeCustomSpecies(sp.id);
          close();
          toast('已删除');
          onChanged();
        }
      });
    }
  );
}

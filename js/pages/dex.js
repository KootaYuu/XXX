// 鱼类解锁图鉴页：钓获日志里记录过的鱼种自动解锁
import { SPECIES, LURE_MAP } from '../data.js';
import { getAll } from '../db.js';
import { esc, openSheet, fmtDate } from '../ui.js';

export async function renderDex(el) {
  const catches = await getAll('catches');
  const bySpecies = {};
  for (const c of catches) {
    (bySpecies[c.speciesId] ||= []).push(c);
  }
  const unlockedCount = SPECIES.filter((s) => bySpecies[s.id]).length;

  el.innerHTML = `
    <header class="page-head">
      <h1>🐟 鱼类图鉴</h1>
      <p class="sub">已解锁 ${unlockedCount} / ${SPECIES.length} 种 — 钓到并记录即可解锁</p>
      <div class="dex-progress"><div class="dex-progress-bar" style="width:${(unlockedCount / SPECIES.length) * 100}%"></div></div>
    </header>
    <div class="dex-grid">
      ${SPECIES.map((s) => {
        const records = bySpecies[s.id];
        const unlocked = !!records;
        return `
        <button class="dex-card ${unlocked ? 'unlocked' : 'locked'}" data-id="${s.id}">
          <span class="dex-emoji">${unlocked ? s.emoji : '❓'}</span>
          <span class="dex-name">${unlocked ? esc(s.name) : '？？？'}</span>
          ${unlocked ? `<span class="dex-count">×${records.length}</span>` : '<span class="dex-count">未解锁</span>'}
        </button>`;
      }).join('')}
    </div>
  `;

  el.querySelector('.dex-grid').addEventListener('click', (e) => {
    const card = e.target.closest('.dex-card');
    if (!card) return;
    const sp = SPECIES.find((s) => s.id === card.dataset.id);
    openDetail(sp, bySpecies[sp.id] || []);
  });
}

function openDetail(sp, records) {
  const unlocked = records.length > 0;
  const sorted = [...records].sort((a, b) => (a.date || '').localeCompare(b.date || ''));
  const first = sorted[0];
  const best = records.reduce((m, c) => (parseFloat(c.weight) > parseFloat(m?.weight || 0) ? c : m), null);
  const topLures = Object.entries(sp.lures)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 3)
    .map(([id]) => LURE_MAP[id])
    .filter(Boolean);

  openSheet(
    `
    <div class="dex-detail">
      <div class="dex-detail-head">
        <span class="dex-detail-emoji ${unlocked ? '' : 'silhouette'}">${sp.emoji}</span>
        <div>
          <h2>${unlocked ? esc(sp.name) : '？？？'}</h2>
          <p class="sub">${unlocked ? esc(sp.latin) : '钓到并记录后解锁完整资料'}</p>
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
      <dl class="dex-facts">
        <div><dt>难度</dt><dd>${'🔥'.repeat(sp.difficulty)}</dd></div>
        <div><dt>活跃季节</dt><dd>${sp.seasons.join('、')}</dd></div>
        <div><dt>泳层</dt><dd>${esc(sp.layer)}</dd></div>
        <div><dt>栖息环境</dt><dd>${esc(sp.habitat)}</dd></div>
        <div><dt>推荐拟饵</dt><dd>${topLures.map((l) => `${l.emoji} ${esc(l.name)}`).join('　')}</dd></div>
        <div><dt>攻略</dt><dd>${esc(sp.tip)}</dd></div>
      </dl>
    </div>
  `,
    () => {}
  );
}

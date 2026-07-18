// 实用工具页：线组换算、前导搭配、钓组图解
import { LINE_TABLE, RIGS } from '../data.js';
import { esc } from '../ui.js';

export function renderTools(el) {
  el.innerHTML = `
    <header class="page-head">
      <h1>🧰 实用工具</h1>
      <p class="sub">线组换算 · 前导搭配 · 钓组图解</p>
    </header>

    <section class="card">
      <h2 class="card-title">PE 线搭配前导</h2>
      <label class="field-label">主线 PE 号数</label>
      <div class="chips" id="pe-chips">
        ${LINE_TABLE.map((r, i) => `<button class="chip ${i === 3 ? 'on' : ''}" data-i="${i}">PE ${r.pe}</button>`).join('')}
      </div>
      <div id="leader-result" class="leader-result"></div>
    </section>

    <section class="card">
      <h2 class="card-title">线径 / 拉力对照表</h2>
      <div class="table-wrap">
        <table class="line-table">
          <thead><tr><th>PE</th><th>拉力</th><th>线径 mm</th><th>建议碳前导</th></tr></thead>
          <tbody>
            ${LINE_TABLE.map((r) => `<tr><td>${r.pe}</td><td>${r.peLb} lb</td><td>${r.dia}</td><td>${esc(r.carbon)}</td></tr>`).join('')}
          </tbody>
        </table>
      </div>
      <p class="note">数值为常见品牌近似值，不同品牌略有差异，以包装标注为准。</p>
    </section>

    <section class="card">
      <h2 class="card-title">常用钓组图解</h2>
      <div id="rig-list">
        ${RIGS.map(
          (r) => `
          <div class="rig-item">
            <h3>${esc(r.name)}</h3>
            <div class="rig-svg">${rigSVG(r.id)}</div>
            <p class="rig-desc">${esc(r.desc)}</p>
            <p class="rig-usage">💡 ${esc(r.usage)}</p>
          </div>`
        ).join('')}
      </div>
    </section>
  `;

  const chips = el.querySelector('#pe-chips');
  const result = el.querySelector('#leader-result');
  const showLeader = (i) => {
    const r = LINE_TABLE[i];
    result.innerHTML = `
      <p>PE ${r.pe}（约 ${r.peLb} lb）建议搭配碳线前导：<b>${esc(r.carbon)}</b></p>
      <p class="note">通用原则：前导拉力 ≈ 主线的 70%–100%；打障碍区可加粗一档，微物泳层可减细一档。前导长度 1–1.5 米，FG 结或电车结连接。</p>`;
  };
  chips.addEventListener('click', (e) => {
    const btn = e.target.closest('.chip');
    if (!btn) return;
    chips.querySelectorAll('.chip').forEach((c) => c.classList.toggle('on', c === btn));
    showLeader(Number(btn.dataset.i));
  });
  showLeader(3);
}

// 简化示意图（SVG）
function rigSVG(id) {
  const line = (d) => `<path d="${d}" class="svg-line" fill="none"/>`;
  const hookAt = (x, y, flip = 1) =>
    `<path d="M${x} ${y} v14 a8 8 0 0 0 ${14 * flip} 2 l ${2 * flip} -6" class="svg-hook" fill="none"/>`;
  const worm = (x, y, rot = 0) =>
    `<path d="M${x} ${y} q10 -8 20 0 q10 8 20 0 q10 -8 18 -2" class="svg-worm" fill="none" transform="rotate(${rot} ${x} ${y})"/>`;

  const svgs = {
    texas: `
      ${line('M150 8 V52')}
      <path d="M143 52 L157 52 L150 78 Z" class="svg-weight"/>
      ${line('M150 78 V92')}
      ${hookAt(150, 92)}
      ${worm(150, 112, 20)}
      <text x="170" y="60" class="svg-label">子弹铅</text>
      <text x="196" y="118" class="svg-label">软虫藏钩尖</text>`,
    dropshot: `
      ${line('M150 8 V70')}
      ${hookAt(150, 70, 1)}
      ${worm(166, 82, -8)}
      ${line('M150 96 V128')}
      <ellipse cx="150" cy="138" rx="9" ry="12" class="svg-weight"/>
      <text x="180" y="70" class="svg-label">钩在上 · 离底悬浮</text>
      <text x="170" y="142" class="svg-label">铅在底</text>`,
    jighead: `
      ${line('M150 8 V72')}
      <circle cx="150" cy="84" r="12" class="svg-weight"/>
      ${hookAt(158, 84)}
      <path d="M170 104 q14 6 10 18 q-4 10 8 12" class="svg-worm" fill="none"/>
      <text x="176" y="86" class="svg-label">铅头钩 + 卷尾蛆</text>`,
    ned: `
      ${line('M150 8 V96')}
      <path d="M138 108 a12 7 0 0 1 24 0 Z" class="svg-weight"/>
      <rect x="144" y="66" width="12" height="34" rx="6" class="svg-worm-solid"/>
      <path d="M40 118 H260" class="svg-bottom"/>
      <text x="176" y="100" class="svg-label">落底后软虫直立</text>`,
    carolina: `
      ${line('M20 60 H90')}
      <ellipse cx="102" cy="60" rx="12" ry="8" class="svg-weight"/>
      <circle cx="122" cy="60" r="4" class="svg-bead"/>
      <rect x="132" y="55" width="10" height="10" rx="2" class="svg-swivel"/>
      ${line('M142 60 H225')}
      ${hookAt(225, 60)}
      ${worm(238, 78, 12)}
      <text x="72" y="42" class="svg-label">通心铅</text>
      <text x="112" y="86" class="svg-label">挡珠+八字环</text>
      <text x="216" y="42" class="svg-label">子线 60–100cm</text>`,
  };
  return `<svg viewBox="0 0 300 160" role="img" aria-label="钓组示意图">${svgs[id] || ''}</svg>`;
}

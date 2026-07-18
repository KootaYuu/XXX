// 拟饵推荐页
import { SPECIES } from '../data.js';
import { recommend, currentSeason } from '../recommend-engine.js';
import { esc, stars } from '../ui.js';

const SEASONS = ['春', '夏', '秋', '冬'];
const TIMES = ['清晨', '白天', '傍晚', '夜晚'];
const CLARITY = ['清澈', '微浊', '浑浊'];
const WATERS = ['水库', '湖泊', '河流', '野塘', '溪流', '海边'];

const state = {
  speciesId: SPECIES[0].id,
  season: currentSeason(),
  timeOfDay: defaultTime(),
  clarity: '微浊',
  water: '水库',
};

function defaultTime() {
  const h = new Date().getHours();
  if (h >= 5 && h < 9) return '清晨';
  if (h >= 9 && h < 17) return '白天';
  if (h >= 17 && h < 20) return '傍晚';
  return '夜晚';
}

function chipGroup(key, options, current) {
  return `<div class="chips" data-key="${key}">
    ${options.map((o) => `<button class="chip ${o === current ? 'on' : ''}" data-val="${esc(o)}">${esc(o)}</button>`).join('')}
  </div>`;
}

export function renderRecommend(el) {
  el.innerHTML = `
    <header class="page-head">
      <h1>🎯 拟饵推荐</h1>
      <p class="sub">选好条件，看今天该绑什么饵</p>
    </header>
    <section class="card">
      <label class="field-label">对象鱼</label>
      <div class="chips" data-key="speciesId">
        ${SPECIES.map((s) => `<button class="chip ${s.id === state.speciesId ? 'on' : ''}" data-val="${s.id}">${s.emoji} ${esc(s.name)}</button>`).join('')}
      </div>
      <label class="field-label">季节</label>
      ${chipGroup('season', SEASONS, state.season)}
      <label class="field-label">时段</label>
      ${chipGroup('timeOfDay', TIMES, state.timeOfDay)}
      <label class="field-label">水色</label>
      ${chipGroup('clarity', CLARITY, state.clarity)}
      <label class="field-label">水域</label>
      ${chipGroup('water', WATERS, state.water)}
    </section>
    <section id="rec-results"></section>
  `;

  el.querySelectorAll('.chips').forEach((group) => {
    group.addEventListener('click', (e) => {
      const btn = e.target.closest('.chip');
      if (!btn) return;
      state[group.dataset.key] = btn.dataset.val;
      group.querySelectorAll('.chip').forEach((c) => c.classList.toggle('on', c === btn));
      renderResults(el.querySelector('#rec-results'));
    });
  });

  renderResults(el.querySelector('#rec-results'));
}

function renderResults(container) {
  const { results, colorAdvice, seasonNote, speciesTip } = recommend(state);
  const medals = ['🥇', '🥈', '🥉', '4️⃣'];
  container.innerHTML = `
    <h2 class="section-title">推荐结果</h2>
    ${results
      .map(
        (r, i) => `
      <div class="card lure-card">
        <div class="lure-head">
          <span class="lure-rank">${medals[i]}</span>
          <span class="lure-name">${r.lure.emoji} ${esc(r.lure.name)}</span>
          <span class="lure-stars">${stars(r.stars)}</span>
        </div>
        <p class="lure-tech">${esc(r.lure.technique)}</p>
      </div>`
      )
      .join('')}
    <div class="card tip-card">
      <p><b>🎨 颜色建议</b>　${esc(colorAdvice)}</p>
      <p><b>🗓️ 季节要点</b>　${esc(seasonNote)}</p>
      <p><b>🐟 对象鱼攻略</b>　${esc(speciesTip)}</p>
    </div>
  `;
}

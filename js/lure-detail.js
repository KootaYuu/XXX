// 拟饵百科详情弹层
import { esc, openSheet } from './ui.js';

export function openLureSheet(lure) {
  const d = lure.detail;
  if (!d) return;
  openSheet(`
    <div class="lure-detail">
      <h2>${lure.emoji} ${esc(lure.name)}</h2>
      <p class="lure-intro">${esc(d.intro)}</p>
      <h3>🎬 操作手法</h3>
      <ol>${d.steps.map((s) => `<li>${esc(s)}</li>`).join('')}</ol>
      <h3>📍 适用场景</h3>
      <p>${esc(d.scenes)}</p>
      <h3>🎣 装备搭配</h3>
      <p>${esc(d.gear)}</p>
      <h3>⚠️ 要点提醒</h3>
      <p>${esc(d.tips)}</p>
    </div>
  `);
}

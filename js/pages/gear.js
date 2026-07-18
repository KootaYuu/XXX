// 装备库页
import { GEAR_CATEGORIES } from '../data.js';
import { getAll, put, remove, uid } from '../db.js';
import { esc, toast, openSheet, confirmDialog } from '../ui.js';

const CATEGORY_ICONS = { '鱼竿': '🎣', '渔轮': '⚙️', '线 / 前导': '🧵', '拟饵': '🐠', '其他': '🎒' };

export async function renderGear(el) {
  const items = await getAll('gear');

  el.innerHTML = `
    <header class="page-head">
      <h1>🎣 我的装备</h1>
      <p class="sub">共 ${items.length} 件装备</p>
    </header>
    <div class="btn-row"><button id="add-gear" class="btn primary">＋ 添加装备</button></div>
    <section id="gear-list">
      ${
        items.length === 0
          ? '<p class="empty">还没有装备，把你的竿轮线饵记进来吧</p>'
          : GEAR_CATEGORIES.filter((cat) => items.some((g) => g.category === cat))
              .map(
                (cat) => `
        <h2 class="section-title">${CATEGORY_ICONS[cat] || ''} ${esc(cat)}</h2>
        ${items
          .filter((g) => g.category === cat)
          .map(
            (g) => `
          <div class="card gear-card" data-id="${g.id}">
            <div class="gear-info">
              <div class="gear-name">${esc(g.name)}</div>
              ${g.spec ? `<div class="gear-spec">${esc(g.spec)}</div>` : ''}
              ${g.notes ? `<div class="gear-notes">${esc(g.notes)}</div>` : ''}
            </div>
            <button class="del-btn" aria-label="删除">✕</button>
          </div>`
          )
          .join('')}`
              )
              .join('')
      }
    </section>
  `;

  el.querySelector('#add-gear').addEventListener('click', () => openForm(null, () => renderGear(el)));

  el.querySelector('#gear-list').addEventListener('click', async (e) => {
    const card = e.target.closest('.gear-card');
    if (!card) return;
    const item = items.find((g) => g.id === card.dataset.id);
    if (!item) return;
    if (e.target.closest('.del-btn')) {
      if (await confirmDialog(`删除「${item.name}」？`)) {
        await remove('gear', item.id);
        toast('已删除');
        renderGear(el);
      }
    } else {
      openForm(item, () => renderGear(el));
    }
  });
}

function openForm(item, onSaved) {
  const isEdit = !!item;
  const g = item || { id: uid(), category: GEAR_CATEGORIES[0], name: '', spec: '', notes: '' };

  openSheet(
    `
    <h2>${isEdit ? '编辑装备' : '添加装备'}</h2>
    <form id="gear-form" class="form">
      <label>分类
        <select name="category">
          ${GEAR_CATEGORIES.map((c) => `<option ${c === g.category ? 'selected' : ''}>${esc(c)}</option>`).join('')}
        </select>
      </label>
      <label>名称<input type="text" name="name" value="${esc(g.name)}" placeholder="如：达瓦 CROSSFIRE 662ML" required></label>
      <label>规格<input type="text" name="spec" value="${esc(g.spec)}" placeholder="如：1.98m / ML调 / 饵重 5-21g"></label>
      <label>备注<textarea name="notes" rows="2" placeholder="搭配、心得…">${esc(g.notes)}</textarea></label>
      <div class="btn-row">
        <button type="submit" class="btn primary">保存</button>
        <button type="button" class="btn" id="cancel-btn">取消</button>
      </div>
    </form>
  `,
    (sheet, close) => {
      sheet.querySelector('#cancel-btn').addEventListener('click', close);
      sheet.querySelector('#gear-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const fd = new FormData(e.target);
        await put('gear', {
          ...g,
          category: fd.get('category'),
          name: fd.get('name').trim(),
          spec: fd.get('spec').trim(),
          notes: fd.get('notes').trim(),
        });
        close();
        toast(isEdit ? '已更新' : '已添加');
        onSaved();
      });
    }
  );
}

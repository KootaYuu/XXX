// 鱼种：内置 + 用户自定义（存 IndexedDB 'species'）
import { SPECIES } from './data.js';
import { getAll, put, remove, uid } from './db.js';
import { esc, toast, openSheet } from './ui.js';

export const SPECIES_EMOJIS = ['🐟', '🐠', '🐡', '🦈', '🐍', '🦐', '🦀', '🐋', '🌊', '🎣'];

export async function getAllSpecies() {
  const custom = (await getAll('species')).sort((a, b) =>
    (a.createdAt || '').localeCompare(b.createdAt || '')
  );
  return [...SPECIES, ...custom];
}

export function removeCustomSpecies(id) {
  return remove('species', id);
}

// 新建自定义鱼种弹层；保存成功后调用 onCreated(newSpecies)
export function openAddSpeciesSheet(onCreated) {
  openSheet(
    `
    <h2>新建自定义鱼种</h2>
    <form id="species-form" class="form">
      <label>名称<input type="text" name="name" required maxlength="12" placeholder="如：鳡鱼"></label>
      <label class="field-label">图标</label>
      <div class="chips" id="emoji-chips">
        ${SPECIES_EMOJIS.map((e, i) => `<button type="button" class="chip ${i === 0 ? 'on' : ''}" data-e="${e}">${e}</button>`).join('')}
      </div>
      <label>攻略笔记（选填）<textarea name="tip" rows="2" placeholder="习性、用饵、标点…"></textarea></label>
      <div class="btn-row">
        <button type="submit" class="btn primary">保存</button>
        <button type="button" class="btn" id="sp-cancel">取消</button>
      </div>
    </form>
  `,
    (sheet, close) => {
      let emoji = SPECIES_EMOJIS[0];
      const chips = sheet.querySelector('#emoji-chips');
      chips.addEventListener('click', (e) => {
        const btn = e.target.closest('.chip');
        if (!btn) return;
        emoji = btn.dataset.e;
        chips.querySelectorAll('.chip').forEach((c) => c.classList.toggle('on', c === btn));
      });
      sheet.querySelector('#sp-cancel').addEventListener('click', close);
      sheet.querySelector('#species-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const fd = new FormData(e.target);
        const sp = {
          id: 'c' + uid(),
          custom: true,
          name: fd.get('name').trim(),
          emoji,
          tip: fd.get('tip').trim(),
          createdAt: new Date().toISOString(),
        };
        await put('species', sp);
        close();
        toast(`已添加鱼种「${sp.name}」`);
        onCreated(sp);
      });
    }
  );
}

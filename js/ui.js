// 通用 UI 小工具

export function esc(s) {
  return String(s ?? '').replace(/[&<>"']/g, (c) => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
  }[c]));
}

export function toast(msg) {
  let el = document.querySelector('.toast');
  if (!el) {
    el = document.createElement('div');
    el.className = 'toast';
    document.body.appendChild(el);
  }
  el.textContent = msg;
  el.classList.add('show');
  clearTimeout(el._timer);
  el._timer = setTimeout(() => el.classList.remove('show'), 2200);
}

// 底部弹层。contentHTML 渲染进弹层后调用 onMount(sheetEl, close)
export function openSheet(contentHTML, onMount) {
  const overlay = document.createElement('div');
  overlay.className = 'sheet-overlay';
  overlay.innerHTML = `<div class="sheet">${contentHTML}</div>`;
  document.body.appendChild(overlay);
  document.body.style.overflow = 'hidden';

  const close = () => {
    overlay.classList.remove('open');
    overlay.style.pointerEvents = 'none';
    document.body.style.overflow = '';
    document.removeEventListener('keydown', onKey);
    setTimeout(() => overlay.remove(), 200);
  };
  const onKey = (e) => {
    if (e.key === 'Escape') close();
  };
  document.addEventListener('keydown', onKey);
  overlay.addEventListener('click', (e) => {
    if (e.target === overlay) close();
  });
  requestAnimationFrame(() => overlay.classList.add('open'));
  if (onMount) onMount(overlay.querySelector('.sheet'), close);
  return close;
}

export function confirmDialog(msg) {
  return Promise.resolve(window.confirm(msg));
}

export function stars(n) {
  return '★'.repeat(n) + '<span class="star-dim">' + '★'.repeat(5 - n) + '</span>';
}

export function fmtDate(iso) {
  if (!iso) return '';
  const d = new Date(iso);
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
}

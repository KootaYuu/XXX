// 应用外壳：hash 路由 + 底部导航
import { renderRecommend } from './pages/recommend.js';
import { renderLog } from './pages/log.js';
import { renderDex } from './pages/dex.js';
import { renderTools } from './pages/tools.js';
import { renderGear } from './pages/gear.js';

const ROUTES = {
  recommend: renderRecommend,
  log: renderLog,
  dex: renderDex,
  tools: renderTools,
  gear: renderGear,
};

const pageEl = document.getElementById('page');

function currentRoute() {
  const name = (location.hash.replace(/^#\//, '') || 'recommend').split('?')[0];
  return ROUTES[name] ? name : 'recommend';
}

async function render() {
  const route = currentRoute();
  document.querySelectorAll('#tabbar a').forEach((a) => {
    a.classList.toggle('active', a.dataset.route === route);
  });
  pageEl.innerHTML = '';
  pageEl.scrollTop = 0;
  await ROUTES[route](pageEl);
}

window.addEventListener('hashchange', render);
render();

// PWA：注册 Service Worker + 新版本更新提示
if ('serviceWorker' in navigator && location.protocol !== 'file:') {
  navigator.serviceWorker
    .register('sw.js')
    .then((reg) => {
      if (reg.waiting) showUpdateBar(reg);
      reg.addEventListener('updatefound', () => {
        const next = reg.installing;
        next?.addEventListener('statechange', () => {
          if (next.state === 'installed' && navigator.serviceWorker.controller) {
            showUpdateBar(reg);
          }
        });
      });
    })
    .catch(() => {});

  let reloaded = false;
  navigator.serviceWorker.addEventListener('controllerchange', () => {
    if (!reloaded) {
      reloaded = true;
      location.reload();
    }
  });
}

function showUpdateBar(reg) {
  if (document.querySelector('.update-bar')) return;
  const bar = document.createElement('div');
  bar.className = 'update-bar';
  bar.innerHTML = '<span>🎉 发现新版本</span><button class="btn small primary">立即更新</button>';
  bar.querySelector('button').addEventListener('click', () => {
    reg.waiting?.postMessage('skipWaiting');
    bar.remove();
  });
  document.body.appendChild(bar);
}

// 申请持久化存储，降低浏览器自动清理 IndexedDB 的风险
if (navigator.storage?.persist) {
  navigator.storage.persist().catch(() => {});
}

// 备份提醒：每天最多提示一次
import('./db.js').then(async ({ getAll }) => {
  const { needBackupNudge } = await import('./backup.js');
  const { toast } = await import('./ui.js');
  const catches = await getAll('catches');
  if (!needBackupNudge(catches.length)) return;
  const today = new Date().toISOString().slice(0, 10);
  if (localStorage.getItem('lure.backupNudgedOn') === today) return;
  localStorage.setItem('lure.backupNudgedOn', today);
  setTimeout(() => toast('📦 已超过 30 天未备份，记得到日志页导出保存'), 1500);
});

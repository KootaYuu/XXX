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

// PWA：注册 Service Worker
if ('serviceWorker' in navigator && location.protocol !== 'file:') {
  navigator.serviceWorker.register('sw.js').catch(() => {});
}

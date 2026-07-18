# 🎣 路亚宝典

移动端优先的路亚钓鱼助手 PWA。纯静态、零构建、零依赖，数据全部保存在手机本地（IndexedDB），可添加到主屏幕、离线使用。

## 功能

| 模块 | 说明 |
| --- | --- |
| 🎯 拟饵推荐 | 按对象鱼、季节、时段、水色、水域，用规则引擎推荐拟饵 + 操作手法 + 颜色建议 |
| 📓 钓获日志 | 记录日期、鱼种、用饵、钓点、天气、尺寸、照片（自动压缩），支持 JSON 导出 / 导入备份 |
| 🐟 鱼类图鉴 | 12 种国内常见路亚对象鱼；钓到并记录后自动解锁，含习性、标点、攻略 |
| 🧰 实用工具 | PE 线径 / 拉力对照表、前导搭配建议、5 种常用钓组 SVG 图解 |
| 🎣 装备库 | 按分类管理竿、轮、线、饵 |

## 本地运行

任何静态服务器都可以：

```bash
python3 -m http.server 8000
# 打开 http://localhost:8000
```

## 部署（推荐 GitHub Pages）

仓库 Settings → Pages → Source 选择分支根目录即可。部署后用手机浏览器打开，
选择「添加到主屏幕」，即可像 App 一样使用（Service Worker 提供离线缓存）。

## 技术说明

- 无框架、无构建：原生 ES Modules + hash 路由单页应用
- 数据存储：IndexedDB（`js/db.js` 封装），照片压缩为最长边 900px 的 JPEG dataURL
- 推荐逻辑：`js/recommend-engine.js`，基于鱼种偏好基础分 + 季节 / 时段 / 水色 / 水域修正
- PWA：`manifest.webmanifest` + `sw.js`（应用壳缓存优先、后台更新）

## 目录结构

```
index.html             入口 + 底部导航
css/style.css          全部样式（深色水域主题）
js/app.js              路由与应用外壳
js/data.js             拟饵 / 鱼种 / 钓组 / 线径静态数据
js/recommend-engine.js 推荐规则引擎
js/db.js               IndexedDB 封装 + 备份导入导出 + 图片压缩
js/ui.js               弹层 / Toast / 工具函数
js/pages/*.js          五个页面模块
icons/                 应用图标（SVG + PNG）
```

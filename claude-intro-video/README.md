# Claude 介绍视频

一段约 64 秒、1920×1080 / 30fps 的中文动画短片，介绍 Anthropic 打造的 AI 助手 Claude。

成片：[`claude-intro.mp4`](claude-intro.mp4)

## 分镜

| 时间 | 章节 | 内容 |
| --- | --- | --- |
| 0:00 | 开场 | 光芒标志展开，“Claude — 由 Anthropic 打造的 AI 助手” |
| 0:07 | 01 认识 Claude | Anthropic 与 AI 安全；可靠 · 可解释 · 可引导 |
| 0:15 | 02 它能做什么 | 写作、编程、分析推理、多语言、视觉理解、长文本 |
| 0:25 | 03 对话体验 | 对话演示：“用一句话解释什么是递归？” |
| 0:35 | 04 模型家族 | Haiku / Sonnet / Opus 的定位（示意） |
| 0:43 | 05 随时随地 | Claude 应用、Claude Code、Claude API |
| 0:51 | 06 核心原则 | 有帮助 · 诚实 · 无害，宪法式 AI |
| 0:58 | 结尾 | “你好，我是 Claude。有什么可以帮你的？” claude.ai |

背景音乐由 `music.py` 用 numpy 合成（C 大调 Cmaj7–Am7–Fmaj7–G6 循环，章节切换处有提示音），无版权问题。

## 如何重新生成

依赖：Node + Playwright（Chromium）、Python 3 + numpy、ffmpeg（没有系统 ffmpeg 时会使用 `imageio-ffmpeg`）。

```bash
./build.sh
```

- `index.html` —— 全部画面。`window.render(t)` 按时间确定性地绘制第 t 秒的画面，可直接在浏览器中打开调试。
- `render.js` —— 用 Playwright 逐帧截图并通过管道交给 ffmpeg 编码；`node render.js --preview 5,20,40` 可导出指定秒数的静帧。
- `music.py` —— 合成背景音乐。
- `fetch_fonts.py` —— 按页面实际用到的字符下载 Noto Sans SC / Noto Serif SC / JetBrains Mono 子集到 `fonts/`，渲染时无需联网。

修改文案后请重新运行 `python3 fetch_fonts.py`，以便字体子集包含新字符。

> 本视频为介绍性作品，并非 Anthropic 官方出品；片中标志为自行绘制的示意图形。

# Claude 介绍视频

一段 64 秒、1920×1080 / 30fps 的中文科技风动画短片，介绍 Anthropic 打造的 AI 助手 Claude。

成片：[`claude-intro.mp4`](claude-intro.mp4)

## 视觉语言

- 深色画布，暖橙色光效，HUD 界面元素（取景角标、时间码、章节编号、进度轨道）
- 实时绘制的 3D 神经网络粒子球，贯穿全片，在每一幕里变换位置和形态
- 星空穿梭、透视网格地面、胶片颗粒、扫描线、暗角
- 文字“解码”效果（乱码逐字解析）、逐字模糊入场、描边大字
- 转场使用故障风切片（glitch）和闪光

## 分镜

| 时间 | 序列 | 内容 |
| --- | --- | --- |
| 0:00 | SEQ 00 · BOOT | 终端启动日志 → 星空穿梭 → 粒子汇聚成球 → CLAUDE 解码出现 |
| 0:08 | SEQ 01 · NEURAL CORE | “会思考的 AI 伙伴”，Anthropic 与 AI 安全；可靠、可解释、可引导 |
| 0:16 | SEQ 02 · CAPABILITIES | 能力矩阵：写作、编程、推理、多语言、视觉、长文本，每项配动态小图 |
| 0:26 | SEQ 03 · INTERFACE | 终端风格对话 + 思考轨迹（界面为示意） |
| 0:35 | SEQ 04 · MODEL FAMILY | 核心球 + 三条轨道：Haiku / Sonnet / Opus |
| 0:43 | SEQ 05 · EVERYWHERE | 数据链路连接 Claude 应用、Claude Code、Claude API |
| 0:50 | SEQ 06 · PRINCIPLES | HELPFUL / HONEST / HARMLESS 描边大字，宪法式 AI |
| 0:56 | SEQ 07 · HELLO | 粒子球坍缩 → 光环爆发 → 标志与“你好，我是 Claude。” |

## 配乐

`music.py` 用 numpy + scipy 合成的电子配乐（A 小调，120 BPM），无版权问题：
启动音效 → 穿梭冲击（3.4s）→ 脉冲琶音 → 底鼓/军鼓/镲片律动与侧链压缩 → 每次转场前的上升音效和转场冲击 → 50–56s 间奏 → 加速鼓点推向 59.1s 坍缩 → 余音淡出。

## 如何重新生成

依赖：Node + Playwright（Chromium）、Python 3 + numpy + scipy、ffmpeg（没有系统 ffmpeg 时会使用 `imageio-ffmpeg`）。

```bash
./build.sh
```

- `index.html`：全部画面（canvas 粒子特效 + DOM 文字）。`window.render(t)` 按时间确定性地绘制第 t 秒的画面，可直接在浏览器中打开调试。
- `render.js`：用 Playwright 逐帧截图，通过管道交给 ffmpeg 编码。`node render.js --preview 5,20,40` 可导出指定秒数的静帧。
- `music.py`：合成配乐。
- `fetch_fonts.py`：按页面实际用到的字符，下载 Noto Sans SC / Space Grotesk / JetBrains Mono 的子集到 `fonts/`，渲染时无需联网。

修改文案后请重新运行 `python3 fetch_fonts.py`，让字体子集包含新字符。

> 本视频为介绍性作品，并非 Anthropic 官方出品；片中标志为自行绘制的示意图形。

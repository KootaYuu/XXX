# Claude 介绍视频

一段 64 秒、1920×1080 / 30fps 的中文科技风动画短片，介绍 Anthropic 打造的 AI 助手 Claude。

成片：[`claude-intro.mp4`](claude-intro.mp4)

## 动效设计

全片没有静态页面，镜头和粒子始终在运动。

- **一套粒子，全程变形**：约 2400 个粒子贯穿全片，不断重组形态：
  尘埃 → 爆炸 → 拼出 CLAUDE → 神经网络球 → 文字行 → 代码雨 → 神经网络信号流 → 语言环 → 像素图表 → 时空隧道 → 光环 → 三层轨道 → 数据地球 → 波动地形 → 再聚成球 → 坍缩 → 光芒标志。
  形态之间的过渡带有逐粒子延迟和漩涡轨迹。
- **3D 镜头**：环绕、推拉、俯仰持续变化，冲击点有镜头震动。
- **动态文字**：乱码解码、3D 翻转入场、遮罩擦除、逐字模糊入场、大字穿过镜头、切片故障转场。
- **跟随 3D 物体的标注**：标签和引线实时追踪旋转球体、轨道环、地球上的点。
- **能力快剪**：六个 1.6 秒节拍，每个节拍都有专属的粒子形态和画面元素（代码输入、环绕的多语言文字、识别框、页数计数）。

## 分镜

| 时间 | 序列 | 内容 |
| --- | --- | --- |
| 0:00 | SEQ 00 · BOOT | 终端启动日志 → 显像管关机效果 → 星空穿梭 → 粒子爆炸后拼出 CLAUDE |
| 0:08 | SEQ 01 · NEURAL CORE | 镜头推近神经网络球；3D 翻转标题“会思考的 AI 伙伴”；球面标注：可靠 · 可解释 · 可引导 |
| 0:16 | SEQ 02 · CAPABILITIES | 写作 / 编程 / 推理 / 多语言 / 视觉 / 长上下文 六拍快剪 |
| 0:26 | SEQ 03 · INTERFACE | 3D 终端飞入：提问 → 思考 → 回答，逐字流式输出和思考轨迹（界面为示意） |
| 0:35 | SEQ 04 · MODEL FAMILY | 三层轨道依次点亮：Haiku / Sonnet / Opus |
| 0:43 | SEQ 05 · EVERYWHERE | 数据地球 + 引线连接 Claude 应用、Claude Code、Claude API |
| 0:50 | SEQ 06 · PRINCIPLES | 飞越波动地形，HELPFUL / HONEST / HARMLESS 依次穿过镜头 |
| 0:56 | SEQ 07 · HELLO | 粒子重新聚成球并加速旋转 → 坍缩 → 冲击波 → 光芒标志与“你好，我是 Claude。” |

## 配乐

`music.py` 用 numpy + scipy 合成的电子配乐（A 小调，120 BPM），无版权问题：
启动音效 → 穿梭冲击（3.4s）→ 脉冲琶音 → 底鼓/军鼓/镲片律动与侧链压缩 → 每次转场前的上升音效和转场冲击，能力快剪每拍都有呼啸声和打击音 → 50–56s 间奏，大字飞过镜头时配呼啸声 → 加速鼓点推向 59.1s 坍缩 → 余音淡出。

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

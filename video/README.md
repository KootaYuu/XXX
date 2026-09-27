# 《书页里的人》动画制作

简笔画默剧动画，全部由代码生成：画面用 [skia-python](https://github.com/kyamagu/skia-python) 逐帧绘制，配乐用 numpy 合成。

| 文件 | 作用 |
| --- | --- |
| `sketch.py` | 绘图库：手绘抖动线条、水彩色块、手写字、人物（林晚 / 许知行 / 周老师）和道具 |
| `scenes.py` | 27 个分镜镜头，与 `../分镜.md` 一一对应 |
| `music.py` | 原创配乐（八音盒 + 钢琴 + 铺底），80 BPM，与镜头逐小节对齐 |
| `render.py` | 渲染入口：静帧预览、联系表、完整视频 |

## 运行

```bash
pip install skia-python numpy imageio-ffmpeg
# Linux 上 skia 还需要 libEGL / libGL：apt-get install -y libegl1 libgl1

python3 render.py sheet               # 每个镜头 3 帧的联系表 -> build/sheet.png
python3 render.py preview 87 150      # 指定秒数的静帧 -> build/preview_*.png
python3 render.py full                # 完整视频 -> build/书页里的人.mp4
```

首次运行会自动下载字体[霞鹜文楷](https://github.com/lxgw/LxgwWenKai)（SIL OFL 协议）到 `fonts/`。

规格：1920×1080，24fps，225 秒。

<div align="center">
  <img src="https://raw.githubusercontent.com/BrokenSource/DepthFlow/main/DepthFlow/Resources/Images/DepthFlow.png" width="210">
  <h1 style="margin-top: 0">DepthFlow</h1>
  <b>Images to → 3D Parallax</b> effect video • A free and open source <a href="https://www.immersity.ai/" target="_blank"><b>ImmersityAI</b></a> alternative
  <br>
  <br>
  <a href="https://pypi.org/project/depthflow/"><img src="https://img.shields.io/pypi/v/depthflow?label=PyPI&color=blue"></a>
  <a href="https://pypi.org/project/depthflow/"><img src="https://img.shields.io/pypi/dw/depthflow?label=Installs&color=blue"></a>
  <a href="https://github.com/BrokenSource/DepthFlow/"><img src="https://img.shields.io/github/v/tag/BrokenSource/BrokenSource?label=GitHub&color=orange"></a>
  <a href="https://github.com/BrokenSource/DepthFlow/stargazers"><img src="https://img.shields.io/github/stars/BrokenSource/DepthFlow?label=Stars&style=flat&color=orange"></a>
  <a href="https://github.com/BrokenSource/DepthFlow/releases/"><img src="https://img.shields.io/github/v/release/BrokenSource/DepthFlow?label=Release&color=light-green"></a>
  <a href="https://github.com/BrokenSource/DepthFlow/releases/"><img src="https://img.shields.io/github/downloads/BrokenSource/DepthFlow/total?label=Downloads&color=light-green"></a>
  <a href="https://discord.gg/KjqvcYwRHm"><img src="https://img.shields.io/discord/1184696441298485370?label=Discord&style=flat&color=purple"></a>
  <br>
  <br>
  <b>
    Links •
    <a href="https://brokensrc.dev/get/">✅ Installation</a> •
    <a href="https://brokensrc.dev/depthflow/">📦 Documentation</a> •
    <a href="https://github.com/akatz-ai/ComfyUI-Depthflow-Nodes">⭐️ ComfyUI</a> •
    <a href="https://github.com/BrokenSource/DepthFlow/issues">🔥 Issues</a> •
    <a href="https://brokensrc.dev/about/sponsors">❤️ Funding</a>
  </b>
  <br>
  <sub>
    <a href="https://www.youtube.com/@Tremeschin">YouTube</a> •
    <a href="https://www.github.com/BrokenSource/DepthFlow">GitHub</a> •
    <a href="https://brokensrc.dev/about/contact">Contact</a> •
    <a href="https://brokensrc.dev/about/changelog">Changelog</a> •
    <a href="https://brokensrc.dev/get/uninstalling">Uninstalling</a> •
    <a href="https://brokensrc.dev/about/license">License</a>
  </sub>
  <br>
  <br>
</div>

<video src="https://github.com/user-attachments/assets/ea9e3c4e-7e62-4cf7-b0a9-265b9323f83d" loop controls autoplay></video>

```bash
ttps://brokensrc.dev/depthflow/

pip install depthflow
pip install transformers "httpx[socks]"
depthflow gradio --help

depthflow gradio --share

#### 要求有声卡 (使用windows)
pip install pianola

#### 安装 fluidsynth 并配置路径
https://github.com/FluidSynth/fluidsynth

pianola main --help

pianola main --output record.mp4
```

### 在目录 D:\software_ins\Anaconda\envs\py311\Lib\site-packages\Pianola 下运行下面的脚本

```python
import os
import re
import urllib.parse
from pathlib import Path

# 配置参数
PIANOLA_FILE = r"D:\software_ins\Anaconda\envs\py311\Lib\site-packages\Pianola\Pianola.py"
PYTHON_EXE = r"D:\software_ins\Anaconda\envs\py311\python.exe"
PIANOLA_CMD = r"D:\software_ins\Anaconda\envs\py311\Scripts\pianola.exe"  # 假设这是可执行文件路径
CHARACTERS = [
    "七七", "丽莎", "久岐忍", "九条裟罗", "云堇", "五郎", "优菈", "克洛琳德",
    "八重神子", "凝光", "凯亚", "刻晴", "北斗", "千织", "卡维", "可莉",
    "嘉明", "坎蒂丝", "埃洛伊", "夏沃蕾", "夏洛蒂", "多莉", "夜兰", "妮露",
    "娜维娅", "安柏", "宵宫", "希格雯", "托马", "提纳里", "早柚", "林尼",
    "枫原万叶", "柯莱", "流浪者", "温迪", "烟绯", "珊瑚宫心海", "珐露珊",
    "班尼特", "琳妮特", "琴", "瑶瑶", "甘雨", "申鹤", "白术", "砂糖",
    "神里绫人", "神里绫华", "米卡", "纳西妲", "绮良良", "罗莎莉亚", "胡桃",
    "艾尔海森", "艾梅莉埃", "芙宁娜", "芭芭拉", "荒泷一斗", "莫娜", "莱依拉",
    "莱欧斯利", "菲米尼", "菲谢尔", "行秋", "诺艾尔", "赛索斯", "赛诺",
    "辛焱", "达达利亚", "迪卢克", "迪奥娜", "迪希雅", "那维莱特", "重云",
    "钟离", "闲云", "阿蕾奇诺", "阿贝多", "雷泽", "雷电将军", "香菱", "魈",
    "鹿野院平藏"
]
BASE_URL = "https://huggingface.co/datasets/svjack/Genshin_Impact_Character_Background_MIDI/resolve/main/{}_basic_pitch.mid"

def update_pianola_file(character: str):
    """更新Pianola.py文件中的TheEntertainer URL"""
    with open(PIANOLA_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    # 对字符进行URL编码
    encoded_character = urllib.parse.quote(character)
    new_url = BASE_URL.format(encoded_character)

    # 替换TheEntertainer的URL
    pattern = r'TheEntertainer = "https://[^"]+"'
    new_content = re.sub(pattern, f'TheEntertainer = "{new_url}"', content)

    # 写回文件
    with open(PIANOLA_FILE, "w", encoding="utf-8") as f:
        f.write(new_content)

def render_character(character: str):
    """使用指定的Python环境渲染指定角色的MIDI"""
    output_file = f"{character}.mp4"
    cmd = f'{PIANOLA_CMD} main --output "{output_file}"'
    print(f"正在渲染: {output_file}")
    os.system(cmd)

def main():
    for character in CHARACTERS:
        print(f"处理角色: {character}")

        # 1. 更新Pianola.py文件
        update_pianola_file(character)
        print(f"已更新TheEntertainer为{character}的MIDI")

        # 2. 执行渲染命令
        render_character(character)
        print(f"已完成{character}的渲染\n")

if __name__ == "__main__":
    main()

```

## 🔥 Description

**DepthFlow** is an advanced _image-to-video_ converter that transforms static pictures into stunning 3D parallax animations. Bring photos to life with motion, featuring high quality and custom presets, perfect for digital art, social media, stock footage, fillers and more.

<small>✨ It works by combining an source image and its depthmap with the power of mathmagic!</small>

- [x] **High quality** results with seamless loops and artifact-free edges, ensuring a polished and professional look for your animations. Enhance your creations with upscalers and add a touch of magic with lens distortion, depth of field, vignette post effects!
- [x] **Fast processing** with an heavily optimized GLSL Shader running on the GPU. Render up to 8k50fps with an RTX 3060, export videos with any resolution, codec, supersampling.
- [x] **Commercial** use is encouraged • Kindly [retribute back](https://brokensrc.dev/about/sponsors/) if you got value from it ❤️
- [x] **Powerful** WebUI built with [Gradio](https://gradio.app), for an user-friendly experience:

<img src="https://github.com/user-attachments/assets/05b81504-d736-4c95-8e6f-9b4901c9eebd">

- [x] **Use your** own depthmaps, or let them be estimated with the latest AI models available!
- [x] **Customizable** with a wide range of projection parameters, allowing you to precisely tweak the effect to your liking. Automate it with [Python scripts](https://github.com/BrokenSource/DepthFlow/tree/main/Examples) for mass production!
- [x] **Self hosted** with no watermarks, unlimited usage, portable ready-to-run executables. It's free and open source, no strings attached.

❤️ **Loving it?** Your [**support**](https://brokensrc.dev/about/sponsors/) is essential!

<br>

## 📦 Installation

Head out to the [**Official Website**](https://brokensrc.dev/get) for the latest installation instructions and more!

<a href="https://brokensrc.dev/get">
  <img src="https://github.com/user-attachments/assets/8470c0d2-46de-4068-b9ce-a1261a6c0e69">
</a>

## ⭐️ Usage

See all [**Quick Start**](https://brokensrc.dev/depthflow/quick/) options in the website as well!

<a href="https://brokensrc.dev/depthflow/quick/">
  <img src="https://github.com/user-attachments/assets/a32e5709-d8ea-48e6-bdc2-f9540f5323de">
</a>

## ♻️ Community

<small>✅ **Be featured here** if you're using DepthFlow in your projects!</small>

Check out amazing community work built on top of DepthFlow:

- ⭐️ [**ComfyUI Node Pack**](https://github.com/akatz-ai/ComfyUI-Depthflow-Nodes) by [@akatz-ai](https://github.com/akatz-ai/), also in [CivitAI](https://civitai.com/models/855031)


# Micro QR Code 生成器

一个基于 Python 与 segno 的 Micro QR Code 生成工具，提供命令行与简洁的图形界面（tkinter）。支持自动选择最小可用的 Micro QR 版本，输出 PNG / SVG 两种格式。

## ✨ 特性
- 自动选择 Micro QR 版本（M1–M4），无需手动指定
- 输出格式：PNG、SVG
- 尺寸以像素为单位（GUI），直观控制导出尺寸
- 可配置边框宽度
- 现代化简单 GUI，所见即所得
- 配置文件驱动默认参数（可选）

## 📦 安装
- Python 3.8+
- 安装依赖：
  ```bash
  pip install -r requirements.txt
  ```
  或
  ```bash
  pip install segno Pillow
  ```

## 🚀 快速开始

### 图形界面（推荐）
```bash
python micro_qr_gui.py
```
- 输入内容 → 选择输出格式（PNG / SVG）→ 设定 尺寸(px) / 边框 → 即时预览或保存
- 预览区会根据设定尺寸(px) 直接生成目标像素，避免模糊
- 默认尺寸：240px；范围：60–2048px（可在配置文件中修改）

### 命令行
- 保存为 PNG：
  ```bash
  python micro_qr_generator.py "内容" --format png -o qr.png
  ```
- 输出 SVG 到标准输出（可重定向保存）：
  ```bash
  python micro_qr_generator.py "内容" --format svg > qr.svg
  ```
- 自定义边框：
  ```bash
  python micro_qr_generator.py "内容" --format png --border 2 -o qr.png
  ```

提示：当指定输出文件名（-o）为相对路径时，程序会按需自动创建 `qrcodes/` 目录并保存到其中；未指定文件名时，SVG 输出到标准输出。

## ⚙️ 配置（可选）
项目支持通过 `micro_qr_config.json` 自定义默认参数与界面设置：
```json
{
  "gui": {
    "window_width": 720,
    "window_height": 880,
    "max_preview_size": 320,
    "base_qr_size": 30
  },
  "defaults": {
    "format": "png",
    "size_px": 240,
    "border": 1,
    "error_correction": "L"
  },
  "ui": {
    "language": "zh_CN",
    "theme": "clam",
    "font_family": "Microsoft YaHei UI",
    "font_size": 12
  }
}
```
- 通过 `config.py` 的全局 `config` 实例进行读取：
  ```python
  from config import config
  default_size_px = config.get_default("size_px", 240)
  ```

## 📁 目录结构
```
Micro QR Code/
├── micro_qr_generator.py   # 命令行工具
├── micro_qr_gui.py         # 图形界面（tkinter）
├── config.py               # 配置加载/保存与访问封装
├── micro_qr_config.json    # 配置文件（按需生成，可手工修改）
├── requirements.txt        # 依赖
└── README.md
```

## ❗ 注意事项
- Micro QR Code 不支持所有容错等级；一般使用 L/M/Q，H 级通常不可用。
- 通常无需手动指定版本，程序会自动选择可用的最小版本，以获得更小尺寸。
- 当以相对路径保存输出时，会自动在项目根目录按需创建 `qrcodes/` 目录。

## 📊 Micro QR Code 版本容量
| 版本 | 尺寸   | 数字容量 | 字母容量 | 二进制容量 |
|------|--------|----------|----------|------------|
| M1   | 11×11  | 20       | 14       | 7 bytes    |
| M2   | 13×13  | 38       | 26       | 14 bytes   |
| M3   | 15×15  | 58       | 40       | 22 bytes   |
| M4   | 17×17  | 84       | 58       | 32 bytes   |

## 🧾 许可协议
MIT



# Micro QR Code Generator

一个基于 Python 的 Micro QR Code 生成工具，支持自动识别 Micro QR Code 版本，命令行与现代化 GUI 均可用。

## 特性
* 支持 Micro QR Code 自动识别版本（无需手动选择）
* 输出格式：PNG、SVG、文本
* 命令行与图形界面双模式
* 可自定义二维码尺寸（scale=1~10，默认1，预览区scale=1时为30×30像素）、边框（border=1~10，默认1），二维码预览区等比例缩放
* 现代化美观界面，所有参数均自动选择，无需手动设置版本和ECC

## 安装依赖

推荐使用 Python 3.8+，需安装：
```bash
pip install segno Pillow
```

## 命令行用法

生成 Micro QR Code 并保存 PNG：
```bash
python micro_qr_generator.py "内容" --format png -o qr.png
```

生成 SVG 或文本：
```bash
python micro_qr_generator.py "内容" --format svg -o qr.svg
python micro_qr_generator.py "内容" --format text -o qr.txt
```

指定版本与容错等级：
```bash
python micro_qr_generator.py "内容" -v 4 -e Q -o qr.png
```

自定义尺寸与边框：
```bash
python micro_qr_generator.py "内容" --scale 10 --border 2 -o qr.png
```

## 图形界面（推荐）

直接运行 GUI：
```bash
python micro_qr_gui.py
```

界面特性：
* 现代化美观布局，支持窗口自适应
* 所有参数可视化设置，Version/ECC均为Auto自动选择，scale默认1（最小），border默认1（最细）
* 预览区自动居中显示二维码，支持 PNG/SVG/Text，二维码可等比例缩放，scale=1时预览区为30×30像素
* 一键保存二维码

## Micro QR Code 版本容量

| 版本 | 尺寸     | 数字容量 | 字母容量 | 二进制容量 |
|------|----------|----------|----------|------------|
| M1   | 11×11    | 20       | 14       | 7 bytes    |
| M2   | 13×13    | 38       | 26       | 14 bytes   |
| M3   | 15×15    | 58       | 40       | 22 bytes   |
| M4   | 17×17    | 84       | 58       | 32 bytes   |

## 依赖
- [segno](https://pypi.org/project/segno/)：Micro QR Code 生成核心库
- [Pillow](https://pypi.org/project/Pillow/)：二维码图片预览与保存

## License

MIT


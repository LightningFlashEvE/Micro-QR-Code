#!/usr/bin/env python3
"""
Micro QR Code 生成器

使用 segno 库生成 Micro QR Code (M1-M4) 的命令行工具。
Micro QR Code 是 QR Code 的小型变体，专为最小数据存储而设计。

特性:
- 支持所有 4 个 Micro QR Code 版本 (M1-M4)
- 自动版本识别，无需手动选择
- 支持 SVG、PNG 输出格式
- 命令行界面
"""

import sys
import os
import argparse
from typing import Optional
import segno


def generate_micro_qr(data: str, version: Optional[int] = None, error_correction: str = 'L') -> segno.QRCode:
    """
    生成 Micro QR Code
    
    Args:
        data: 要编码的文本数据
        version: Micro QR Code 版本 (1-4)，None 表示自动选择
        error_correction: 容错等级 ('L', 'M', 'Q', 'H')
    
    Returns:
        segno.QRCode: 生成的 Micro QR Code 对象
    
    Raises:
        ValueError: 当数据过长或无法生成指定版本时
    """
    if version is None:
        qr = segno.make(data, micro=True, error=error_correction)
        if not qr.is_micro:
            raise ValueError('数据过长，无法生成 Micro QR Code')
        return qr
    else:
        try:
            qr = segno.make_micro(data, version=version, error=error_correction)
        except Exception as e:
            raise ValueError(f'无法生成指定版本的 Micro QR Code: {e}') from e


def save_svg(qr: segno.QRCode, filename: str, scale: int = 8, border: int = 4) -> None:
    """保存 SVG 格式的 QR Code"""
    qr.save(filename, kind='svg', scale=scale, border=border)
    print(f"SVG 已保存到 {filename}")


def save_png(qr: segno.QRCode, filename: str, scale: int = 8, border: int = 4) -> None:
    """保存 PNG 格式的 QR Code"""
    qr.save(filename, kind='png', scale=scale, border=border)
    print(f"PNG 已保存到 {filename}")


def get_output_path(filename: Optional[str]) -> Optional[str]:
    """
    获取输出文件路径
    
    Args:
        filename: 文件名，None 表示输出到标准输出
    
    Returns:
        完整的文件路径，None 表示输出到标准输出
    """
    if not filename:
        return None
    if not os.path.isabs(filename):
        # 确保 qrcodes 目录存在
        os.makedirs('qrcodes', exist_ok=True)
        return os.path.join('qrcodes', filename)
    return filename


def main() -> None:
    """主函数"""
    parser = argparse.ArgumentParser(
        description="使用 segno 生成 Micro QR Code (M1-M4)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s "Hello, world!"           # 自动选择最合适的 Micro QR
  %(prog)s "Tiny" -v 2               # 强制生成 M2
  %(prog)s "Hello" --format png -o qr.png
        """
    )
    parser.add_argument('data', help='要编码的文本数据')
    parser.add_argument('-v', '--version', type=int, default=None, choices=[1, 2, 3, 4],
                        help='Micro QR Code 版本 (M1-M4)，默认: 自动选择')
    parser.add_argument('-e', '--error-correction', default='L',
                        choices=['L', 'M', 'Q', 'H'],
                        help='容错等级: L=7%%, M=15%%, Q=25%%, H=30%% (默认: L)')
    parser.add_argument('-o', '--output',
                        help='输出文件名 (默认: 保存到 qrcodes/ 目录，SVG 未指定文件名时输出 data URI 到标准输出)')
    parser.add_argument('--format', choices=['svg', 'png'], default='svg',
                        help='输出格式 (默认: svg)')
    parser.add_argument('--scale', type=int, default=8,
                        help='缩放比例 (默认: 8)')
    parser.add_argument('--border', type=int, default=4,
                        help='边框大小，以模块为单位 (默认: 4)')
    args = parser.parse_args()

    try:
        qr = generate_micro_qr(args.data, args.version, args.error_correction)
        
        if args.format == 'svg':
            out_path = get_output_path(args.output)
            if out_path:
                save_svg(qr, out_path, args.scale, args.border)
            else:
                print(qr.svg_data_uri(scale=args.scale, border=args.border))
        elif args.format == 'png':
            out_path = get_output_path(args.output)
            if not out_path:
                print("错误: PNG 格式需要指定输出文件名 (-o)")
                sys.exit(1)
            save_png(qr, out_path, args.scale, args.border)
    except Exception as e:
        print(f"生成 Micro QR Code 时出错: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

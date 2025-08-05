#!/usr/bin/env python3
"""
Micro QR Code Generator

This script generates Micro QR Codes (M1-M4) using the qrcodegen library.
Micro QR Codes are smaller variants of QR Codes designed for minimal data storage.

Features:
- Supports all 4 Micro QR Code versions (M1-M4)
- Generates SVG output to stdout or file
- Generates PNG image files
- Command-line interface
"""


import sys
import argparse
import segno

# segno版 Micro QR Code 生成主逻辑
def generate_micro_qr(data, version=None, error_correction='L'):
    if version is None:
        qr = segno.make(data, micro=True, error=error_correction)
        if not qr.is_micro:
            raise ValueError('数据过长，无法生成 Micro QR Code')
        return qr
    else:
        try:
            qr = segno.make_micro(data, version=version, error=error_correction)
        except Exception as e:
            raise ValueError(f'无法生成指定版本的 Micro QR Code: {e}')
        return qr

def qr_to_text(qr):
    return qr.terminal(border=1)

def save_svg(qr, filename, scale=8, border=4):
    qr.save(filename, kind='svg', scale=scale, border=border)
    print(f"SVG saved to {filename}")

def save_png(qr, filename, scale=8, border=4):
    qr.save(filename, kind='png', scale=scale, border=border)
    print(f"PNG saved to {filename}")

def main():
    parser = argparse.ArgumentParser(
        description="Generate Micro QR Codes (M1-M4) using segno",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "Hello, world!"           # 自动选择最合适的 Micro QR
  %(prog)s "Tiny" -v 2               # 强制生成 M2
  %(prog)s "Hello" --format png -o qr.png
        """
    )
    parser.add_argument('data', help='Text data to encode')
    parser.add_argument('-v', '--version', type=int, default=None, choices=[1, 2, 3, 4],
                        help='Micro QR Code version (M1-M4), default: auto')
    parser.add_argument('-e', '--error-correction', default='L',
                        choices=['L', 'M', 'Q', 'H'],
                        help='Error correction level: L=7%%, M=15%%, Q=25%%, H=30%% (default: L)')
    parser.add_argument('-o', '--output',
                        help='Output filename (default: qrcodes/ 下保存，stdout for SVG/text)')
    parser.add_argument('--format', choices=['svg', 'png', 'text'], default='svg',
                        help='Output format (default: svg)')
    parser.add_argument('--scale', type=int, default=8,
                        help='Scale (default: 8)')
    parser.add_argument('--border', type=int, default=4,
                        help='Border size in modules (default: 4)')
    args = parser.parse_args()

    try:
        qr = generate_micro_qr(args.data, args.version, args.error_correction)
        def get_output_path(filename):
            import os
            if not filename:
                return None
            if not os.path.isabs(filename):
                # 自动存到 qrcodes 文件夹
                return os.path.join('qrcodes', filename)
            return filename

        if args.format == 'text':
            text_output = qr_to_text(qr)
            out_path = get_output_path(args.output)
            if out_path:
                with open(out_path, 'w', encoding='utf-8') as f:
                    f.write(text_output)
                print(f"Text Micro QR Code saved to {out_path}")
            else:
                print(text_output)
        elif args.format == 'svg':
            out_path = get_output_path(args.output)
            if out_path:
                save_svg(qr, out_path, args.scale, args.border)
            else:
                print(qr.svg_data_uri(scale=args.scale, border=args.border))
        elif args.format == 'png':
            out_path = get_output_path(args.output)
            if not out_path:
                print("Error: PNG format requires an output filename (-o)")
                sys.exit(1)
            save_png(qr, out_path, args.scale, args.border)
    except Exception as e:
        print(f"Error generating Micro QR Code: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

"""
Micro QR Code 生成器 - 图形界面

基于 tkinter 的现代化 Micro QR Code 生成工具，提供直观的图形界面。
"""

import os
import tempfile
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Optional, Tuple
import segno
from PIL import Image, ImageTk
from config import config
import tkinter.font as tkfont
import platform
import ctypes


class MicroQRGeneratorGUI:
    """Micro QR Code 生成器图形界面类"""
    
    def __init__(self, root: tk.Tk):
        """
        初始化 GUI
        
        Args:
            root: tkinter 根窗口
        """
        self.root = root
        self.root.title("Micro QR Code 生成器")
        
        # 从配置文件获取窗口尺寸
        window_width = config.get_gui_setting("window_width", 600)
        window_height = config.get_gui_setting("window_height", 760)
        self.root.geometry(f"{window_width}x{window_height}")
        self.root.resizable(True, True)
        # 设置最小尺寸，避免控件被截断
        try:
            self.root.minsize(640, 760)
        except Exception:
            pass

        # 控件变量 - 从配置文件获取默认值
        self.data_var = tk.StringVar()
        self.format_var = tk.StringVar(value=config.get_default("format", "png"))
        # 尺寸（像素）优先从 defaults.size_px 读取；默认 240px
        default_size_px = config.get_default("size_px", None)
        if default_size_px is None:
            default_size_px = 240
        self.size_px_var = tk.IntVar(value=int(default_size_px))
        self.border_var = tk.IntVar(value=config.get_default("border", 1))

        # 字体设置（优先使用配置；否则按平台选择最佳可用字体）
        self.ui_font_size: int = config.get("ui.font_size", 12)
        # 文本预览字号相对主字号略小，避免拥挤
        self.preview_font_size: int = max(9, self.ui_font_size - 2)
        self.ui_font_family: str = self._resolve_ui_font_family()
        self.mono_font_family: str = self._choose_monospace_font()

        # 预览刷新防抖任务句柄
        self._preview_update_job: Optional[str] = None

        # 图片引用（防止被垃圾回收）
        self.qr_img: Optional[ImageTk.PhotoImage] = None
        self.tk_img: Optional[ImageTk.PhotoImage] = None

        # 参数变更自动刷新预览
        self.size_px_var.trace_add('write', self._on_param_change)
        self.border_var.trace_add('write', self._on_param_change)
        self.format_var.trace_add('write', self._on_param_change)

        self.build_ui()
    
    def _resolve_ui_font_family(self) -> str:
        """返回可用的界面字体：优先配置；若配置不可用，则回退系统最佳。"""
        configured = config.get("ui.font_family")
        families = set(tkfont.families())
        if configured and configured in families:
            return configured
        return self._choose_best_font()

    def _choose_best_font(self) -> str:
        """根据平台选择最佳中文/系统字体（若配置未指定或不可用）。"""
        families = set(tkfont.families())
        system_name = platform.system()
        if system_name == 'Windows':
            candidates = [
                'Microsoft YaHei UI', 'Microsoft YaHei', 'Segoe UI',
                'Microsoft JhengHei UI', 'Microsoft JhengHei'
            ]
        elif system_name == 'Darwin':  # macOS
            candidates = ['PingFang SC', 'SF Pro Text', 'Helvetica Neue', 'Heiti SC']
        else:  # Linux / other
            candidates = ['Noto Sans CJK SC', 'WenQuanYi Micro Hei', 'DejaVu Sans']
        for name in candidates:
            if name in families:
                return name
        return tkfont.nametofont('TkDefaultFont').actual().get('family', 'TkDefaultFont')

    def _choose_monospace_font(self) -> str:
        """选择可用的等宽字体用于文本预览。"""
        families = set(tkfont.families())
        candidates = [
            'Consolas', 'Cascadia Mono', 'Menlo', 'Courier New',
            'SF Mono', 'DejaVu Sans Mono', 'Liberation Mono', 'Monaco'
        ]
        for name in candidates:
            if name in families:
                return name
        return tkfont.nametofont('TkFixedFont').actual().get('family', 'TkFixedFont')

    def build_ui(self) -> None:
        """构建用户界面"""
        # 主框架
        frm = ttk.Frame(self.root, padding=18, style="Modern.TFrame")
        frm.pack(fill=tk.BOTH, expand=True)
        
        # 样式配置
        self._configure_styles()
        
        # 标题
        ttk.Label(
            frm, 
            text="Micro QR Code 生成器", 
            style="Modern.TLabel", 
            font=(self.ui_font_family, self.ui_font_size + 6, "bold")
        ).pack(pady=(0, 16))

        # 数据输入区域
        self._build_data_input(frm)
        
        # 选项区域
        self._build_options_area(frm)
        
        # 格式和参数区域
        self._build_format_area(frm)
        
        # 按钮区域
        self._build_buttons(frm)
        
        # 预览区域
        self._build_preview_area(frm)
        
        # 状态栏
        self._build_status_bar(frm)

    def _configure_styles(self) -> None:
        """配置界面样式"""
        style = ttk.Style()
        theme = config.get("ui.theme", "clam")
        
        style.theme_use(theme)
        style.configure("Modern.TFrame", background="#f8f9fa")
        style.configure("Modern.TLabel", background="#f8f9fa", font=(self.ui_font_family, 13))
        style.configure("Modern.TButton", font=(self.ui_font_family, self.ui_font_size), padding=6)
        style.configure("Modern.TRadiobutton", background="#f8f9fa", font=(self.ui_font_family, self.ui_font_size))
        style.configure("Modern.TSpinbox", font=(self.ui_font_family, self.ui_font_size))
        # 放大 Spinbox 箭头与高度
        style.configure("Large.TSpinbox", font=(self.ui_font_family, self.ui_font_size), arrowsize=18, padding=4)

    def _build_data_input(self, parent: ttk.Frame) -> None:
        """构建数据输入区域"""
        ttk.Label(parent, text="数据:", style="Modern.TLabel").pack(anchor=tk.W)
        ttk.Entry(
            parent, 
            textvariable=self.data_var, 
            width=50, 
            font=(self.ui_font_family, self.ui_font_size)
        ).pack(fill=tk.X, pady=6)

    def _build_options_area(self, parent: ttk.Frame) -> None:
        """构建选项区域"""
        optfrm = ttk.Frame(parent, style="Modern.TFrame")
        optfrm.pack(fill=tk.X, pady=6)
        
        ttk.Label(optfrm, text="版本:", style="Modern.TLabel").pack(side=tk.LEFT)
        ttk.Label(optfrm, text="自动 (最小)", style="Modern.TLabel").pack(side=tk.LEFT, padx=2)
        ttk.Label(optfrm, text="容错:", style="Modern.TLabel").pack(side=tk.LEFT, padx=(18, 0))
        ttk.Label(optfrm, text="自动", style="Modern.TLabel").pack(side=tk.LEFT, padx=2)

    def _build_format_area(self, parent: ttk.Frame) -> None:
        """构建格式和参数区域"""
        fmtfrm = ttk.Frame(parent, style="Modern.TFrame")
        fmtfrm.pack(fill=tk.X, pady=6)
        
        # 格式选择
        ttk.Label(fmtfrm, text="格式:", style="Modern.TLabel").pack(side=tk.LEFT)
        for fmt in ["png", "svg"]:
            ttk.Radiobutton(
                fmtfrm, 
                text=fmt.upper(), 
                variable=self.format_var, 
                value=fmt, 
                style="Modern.TRadiobutton"
            ).pack(side=tk.LEFT, padx=2)
        
        # 尺寸参数（像素）
        ttk.Label(fmtfrm, text="尺寸:", style="Modern.TLabel").pack(side=tk.LEFT, padx=(12, 0))
        ttk.Spinbox(
            fmtfrm, 
            from_=60, 
            to=2048, 
            textvariable=self.size_px_var, 
            width=4, 
            font=(self.ui_font_family, self.ui_font_size),
            style="Large.TSpinbox"
        ).pack(side=tk.LEFT)
        ttk.Label(fmtfrm, text="px", style="Modern.TLabel").pack(side=tk.LEFT, padx=(4, 0))
        
        # 边框参数
        ttk.Label(fmtfrm, text="边框:", style="Modern.TLabel").pack(side=tk.LEFT, padx=(12, 0))
        ttk.Spinbox(
            fmtfrm, 
            from_=1, 
            to=10, 
            textvariable=self.border_var, 
            width=4, 
            font=(self.ui_font_family, self.ui_font_size),
            style="Large.TSpinbox"
        ).pack(side=tk.LEFT)

    def _build_buttons(self, parent: ttk.Frame) -> None:
        """构建按钮区域"""
        ttk.Button(
            parent, 
            text="生成", 
            command=self.generate_qr, 
            style="Modern.TButton"
        ).pack(fill=tk.X, pady=8)
        
        ttk.Button(
            parent, 
            text="保存", 
            command=self.save_qr, 
            style="Modern.TButton"
        ).pack(fill=tk.X, pady=4)

    def _build_preview_area(self, parent: ttk.Frame) -> None:
        """构建预览区域"""
        self.preview = tk.Label(
            parent, 
            bg="#e9ecef", 
            width=48, 
            height=40, 
            anchor=tk.CENTER, 
            relief=tk.RIDGE
        )
        self.preview.pack(fill=tk.BOTH, expand=True, pady=16)

    def _build_status_bar(self, parent: ttk.Frame) -> None:
        """构建状态栏"""
        self.status_var = tk.StringVar(value="就绪")
        ttk.Label(
            parent, 
            textvariable=self.status_var, 
            anchor=tk.W, 
            relief=tk.SUNKEN, 
            style="Modern.TLabel"
        ).pack(fill=tk.X, pady=(0, 6))

    def _on_param_change(self, *args) -> None:
        """参数变更时，自动刷新预览（防抖）。"""
        data = self.data_var.get().strip()
        if not data:
            # 无数据时清空预览，不弹错误
            self.preview.config(image="", text="")
            self.status_var.set("请输入数据")
            return
        self._schedule_preview_refresh()

    def _schedule_preview_refresh(self) -> None:
        # 60ms 节流：若已有挂起任务则不再重复安排
        if self._preview_update_job is not None:
            return
        self._preview_update_job = self.root.after(60, self._run_preview_update)

    def _run_preview_update(self) -> None:
        self._preview_update_job = None
        self.generate_qr()

    def _generate_qr_code(self) -> Optional[segno.QRCode]:
        """
        生成 QR Code
        
        Returns:
            生成的 QR Code 对象，失败时返回 None
        """
        data = self.data_var.get().strip()
        if not data:
            self.status_var.set("请输入数据")
            return None
        
        try:
            return segno.make(data, micro=True)
        except Exception as e:
            self.status_var.set(f"错误: {type(e).__name__}: {e}")
            messagebox.showerror("二维码生成失败", f"{type(e).__name__}: {e}")
            return None

    def _create_preview_image(self, qr: segno.QRCode) -> Optional[ImageTk.PhotoImage]:
        """
        创建预览图片（直接用 segno 生成到目标像素尺寸，避免二次缩放导致模糊）。
        """
        try:
            max_preview_size = config.get_gui_setting("max_preview_size", 320)
            border = self.border_var.get()
            # 目标像素直接取自 size_px，且预览不超过 max_preview_size
            target_px = max(1, int(self.size_px_var.get() or 1))
            target_px = min(max(1, target_px), max_preview_size)

            # 计算 scale：以 scale=1 的像素宽度为基准，取不超过 target_px 的最大整数 scale
            base_w, _ = qr.symbol_size(scale=1, border=border)
            if base_w <= 0:
                base_w = 1
            best_scale = max(1, min(100, target_px // base_w))
            if best_scale < 1:
                best_scale = 1

            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
                tmp_path = tmp_file.name

            qr.save(tmp_path, kind="png", scale=best_scale, border=border)

            img = Image.open(tmp_path)
            tk_img = ImageTk.PhotoImage(img)

            try:
                os.unlink(tmp_path)
            except OSError:
                pass

            return tk_img

        except Exception as e:
            self.status_var.set(f"预览图片生成失败: {e}")
            return None

    def generate_qr(self) -> None:
        """生成 QR Code 并显示预览"""
        qr = self._generate_qr_code()
        if qr is None:
            self.preview.config(image="", text="")
            return
        
        fmt = self.format_var.get()
        
        try:
            if fmt == "png":
                # 生成 PNG 预览（按最大尺寸计算scale，避免模糊）
                self.tk_img = self._create_preview_image(qr)
                if self.tk_img:
                    self.preview.config(image=self.tk_img, text="")
                    self.qr_img = self.tk_img  # 防止图片被垃圾回收
                else:
                    self.preview.config(image="", text="预览生成失败")
                    
            elif fmt == "svg":
                # SVG 格式预览
                self.preview.config(
                    image="", 
                    text="SVG 生成成功，可保存文件查看", 
                    font=(self.mono_font_family, self.preview_font_size)
                )
            # 不再支持 text 预览
            
            self.status_var.set(f"Micro QR 已生成: {qr.designator}")
            
        except Exception as e:
            self.preview.config(image="", text="")
            self.status_var.set(f"预览生成失败: {type(e).__name__}: {e}")
            messagebox.showerror("预览生成失败", f"{type(e).__name__}: {e}")

    def save_qr(self) -> None:
        """保存 QR Code 到文件"""
        qr = self._generate_qr_code()
        if qr is None:
            return
        
        fmt = self.format_var.get()
        ext = fmt if fmt != "text" else "txt"
        
        # 选择保存路径
        file = filedialog.asksaveasfilename(
            defaultextension=f".{ext}",
            filetypes=[(f"{fmt.upper()} 文件", f"*.{ext}"), ("所有文件", "*.*")]
        )
        
        if not file:
            return
        
        try:
            border = self.border_var.get()
            if fmt in ("png", "svg"):
                # 依据目标像素计算 scale
                target_px = max(1, int(self.size_px_var.get() or 1))
                base_w, _ = qr.symbol_size(scale=1, border=border)
                if base_w <= 0:
                    base_w = 1
                save_scale = max(1, min(100, target_px // base_w))
                kind = "png" if fmt == "png" else "svg"
                qr.save(file, kind=kind, scale=save_scale, border=border)
            else:
                # 非法格式（理应不会出现），直接返回
                self.status_var.set("不支持的格式")
                return
            
            self.status_var.set(f"已保存: {file}")
            
        except Exception as e:
            self.status_var.set(f"保存失败: {type(e).__name__}: {e}")
            messagebox.showerror("保存失败", f"{type(e).__name__}: {e}")


def _set_windows_dpi_awareness() -> None:
    """在 Windows 上启用高 DPI 感知，减少系统缩放带来的模糊。"""
    if platform.system() != 'Windows':
        return
    try:
        # 优先 Per-Monitor V2
        awareness_ctx = -4  # DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2
        ctypes.windll.user32.SetProcessDpiAwarenessContext(ctypes.c_void_p(awareness_ctx))
    except Exception:
        try:
            # 回退到 Per-Monitor（Win8.1+）
            ctypes.windll.shcore.SetProcessDpiAwareness(2)  # PROCESS_PER_MONITOR_DPI_AWARE
        except Exception:
            try:
                # 最后回退到 System DPI aware（Vista+）
                ctypes.windll.user32.SetProcessDPIAware()
            except Exception:
                pass


def _apply_tk_scaling(root: tk.Tk) -> None:
    """根据系统缩放设置 tk 的 scaling，提升清晰度。"""
    try:
        if platform.system() == 'Windows':
            # 0 = 主显示器
            scale_percent = ctypes.c_int()
            hr = ctypes.windll.shcore.GetScaleFactorForDevice(0, ctypes.byref(scale_percent))
            if hr == 0 and scale_percent.value:
                root.tk.call('tk', 'scaling', scale_percent.value / 100.0)
    except Exception:
        pass


def main() -> None:
    """主函数"""
    _set_windows_dpi_awareness()
    root = tk.Tk()
    _apply_tk_scaling(root)
    MicroQRGeneratorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()

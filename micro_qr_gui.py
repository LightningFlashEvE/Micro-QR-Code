
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import segno
from PIL import Image, ImageTk

class MicroQRGeneratorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Micro QR Code Generator")
        self.root.geometry("600x760")
        self.root.resizable(False, False)

        # 控件变量
        self.data_var = tk.StringVar()
        # 只保留自动识别版本，无需变量
        # ECC自动识别，无需变量
        self.format_var = tk.StringVar(value="png")
        self.scale_var = tk.IntVar(value=1)
        self.border_var = tk.IntVar(value=1)

        self.qr_img = None
        self.tk_img = None

        self.build_ui()

    def build_ui(self):
        frm = ttk.Frame(self.root, padding=18, style="Modern.TFrame")
        frm.pack(fill=tk.BOTH, expand=True)
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Modern.TFrame", background="#f8f9fa")
        style.configure("Modern.TLabel", background="#f8f9fa", font=("Segoe UI", 13))
        style.configure("Modern.TButton", font=("Segoe UI", 12), padding=6)
        style.configure("Modern.TRadiobutton", background="#f8f9fa", font=("Segoe UI", 12))
        style.configure("Modern.TSpinbox", font=("Segoe UI", 12))

        ttk.Label(frm, text="Micro QR Code Generator", style="Modern.TLabel", font=("Segoe UI", 20, "bold")).pack(pady=(0, 16))

        ttk.Label(frm, text="Data:", style="Modern.TLabel").pack(anchor=tk.W)
        ttk.Entry(frm, textvariable=self.data_var, width=50, font=("Segoe UI", 12)).pack(fill=tk.X, pady=6)

        optfrm = ttk.Frame(frm, style="Modern.TFrame")
        optfrm.pack(fill=tk.X, pady=6)
        ttk.Label(optfrm, text="Version:", style="Modern.TLabel").pack(side=tk.LEFT)
        ttk.Label(optfrm, text="Auto (最小)", style="Modern.TLabel").pack(side=tk.LEFT, padx=2)
        ttk.Label(optfrm, text="ECC:", style="Modern.TLabel").pack(side=tk.LEFT, padx=(18,0))
        ttk.Label(optfrm, text="Auto", style="Modern.TLabel").pack(side=tk.LEFT, padx=2)

        fmtfrm = ttk.Frame(frm, style="Modern.TFrame")
        fmtfrm.pack(fill=tk.X, pady=6)
        ttk.Label(fmtfrm, text="Format:", style="Modern.TLabel").pack(side=tk.LEFT)
        for f in ["png", "svg", "text"]:
            ttk.Radiobutton(fmtfrm, text=f.upper(), variable=self.format_var, value=f, style="Modern.TRadiobutton").pack(side=tk.LEFT, padx=2)
        ttk.Label(fmtfrm, text="Scale:", style="Modern.TLabel").pack(side=tk.LEFT, padx=(18,0))
        ttk.Spinbox(fmtfrm, from_=1, to=10, textvariable=self.scale_var, width=5, font=("Segoe UI", 12)).pack(side=tk.LEFT)
        ttk.Label(fmtfrm, text="Border:", style="Modern.TLabel").pack(side=tk.LEFT, padx=(18,0))
        ttk.Spinbox(fmtfrm, from_=1, to=10, textvariable=self.border_var, width=5, font=("Segoe UI", 12)).pack(side=tk.LEFT)

        ttk.Button(frm, text="Generate", command=self.generate_qr, style="Modern.TButton").pack(fill=tk.X, pady=8)
        ttk.Button(frm, text="Save", command=self.save_qr, style="Modern.TButton").pack(fill=tk.X, pady=4)

        self.preview = tk.Label(frm, bg="#e9ecef", width=48, height=40, anchor=tk.CENTER, relief=tk.RIDGE)
        self.preview.pack(fill=tk.BOTH, expand=True, pady=16)

        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(frm, textvariable=self.status_var, anchor=tk.W, relief=tk.SUNKEN, style="Modern.TLabel").pack(fill=tk.X, pady=(0,6))

    def generate_qr(self):
        import os
        data = self.data_var.get().strip()
        if not data:
            self.status_var.set("Please enter data")
            self.preview.config(image="", text="")
            return
        try:
            # 只用自动识别版本
            qr = segno.make(data, micro=True)
            fmt = self.format_var.get()
            if fmt == "png":
                tmpfile = "_preview_microqr.png"
                qr.save(tmpfile, kind="png", scale=self.scale_var.get(), border=self.border_var.get())
                img = Image.open(tmpfile)
                # 根据 scale 参数动态缩放预览区图片，最大边限制在 320 像素
                base_size = 30 * self.scale_var.get()
                size = min(base_size, 320)
                img = img.resize((size, size))
                self.tk_img = ImageTk.PhotoImage(img)
                self.preview.config(image=self.tk_img, text="")
                self.qr_img = self.tk_img  # 防止图片被垃圾回收
                # 删除临时文件
                try:
                    os.remove(tmpfile)
                except Exception:
                    pass
            elif fmt == "svg":
                self.preview.config(image="", text="SVG生成成功，可保存文件查看", font=("Consolas", 10))
            else:
                term_txt = qr.terminal(border=self.border_var.get())
                if term_txt is not None:
                    self.preview.config(image="", text=term_txt, font=("Consolas", 10))
                else:
                    self.preview.config(image="", text="无法字符渲染该二维码", font=("Consolas", 10))
            self.status_var.set(f"Micro QR generated: {qr.designator}")
        except Exception as e:
            self.preview.config(image="", text="")
            self.status_var.set(f"Error: {type(e).__name__}: {e}")
            messagebox.showerror("二维码生成失败", f"{type(e).__name__}: {e}")

    def save_qr(self):
        data = self.data_var.get().strip()
        if not data:
            self.status_var.set("Please enter data")
            return
        fmt = self.format_var.get()
        ext = fmt if fmt != "text" else "txt"
        file = filedialog.asksaveasfilename(defaultextension=f".{ext}", filetypes=[(f"{fmt.upper()} files", f"*.{ext}"), ("All files", "*.*")])
        if not file:
            return
        try:
            qr = segno.make(data, micro=True)
            if fmt == "png":
                qr.save(file, kind="png", scale=self.scale_var.get(), border=self.border_var.get())
            elif fmt == "svg":
                qr.save(file, kind="svg", scale=self.scale_var.get(), border=self.border_var.get())
            else:
                term_txt = qr.terminal(border=self.border_var.get())
                if term_txt is not None:
                    with open(file, "w", encoding="utf-8") as f:
                        f.write(term_txt)
                    self.status_var.set(f"Saved: {file}")
                else:
                    self.status_var.set("无法字符渲染该二维码，未保存")
                    return
            self.status_var.set(f"Saved: {file}")
        except Exception as e:
            self.status_var.set(f"Error saving: {type(e).__name__}: {e}")

def main():
    root = tk.Tk()
    MicroQRGeneratorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()

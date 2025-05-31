import os, json, hmac, hashlib, tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import List
from PIL import Image, ImageTk  # type: ignore

WIDTH, HEIGHT = 20, 20
PAIRS_PER_STEP = 5
MS_DELAY = 1
SCALE = 10

IDX = lambda x, y: y * WIDTH + x

# ───────── helpers ─────────

def image_to_list(img: Image.Image) -> List[tuple[int, int, int]]:
    img = img.convert("RGB")
    if (img.width, img.height) != (WIDTH, HEIGHT):
        raise ValueError(f"Изображение должно быть {WIDTH}×{HEIGHT} пикселей")
    return list(img.getdata())


def list_to_image(px: List[tuple[int, int, int]]):
    im = Image.new("RGB", (WIDTH, HEIGHT))
    im.putdata(px)
    return im

# ───────── крипто‑PRNG ─────────

def _rand_stream(key: bytes, step: int):
    seed = hmac.digest(key, step.to_bytes(8, "big"), "sha256")
    while True:
        for i in range(0, len(seed), 4):
            yield int.from_bytes(seed[i : i + 4], "big")
        seed = hashlib.sha256(seed).digest()


def _next_indices(key: bytes, step: int, pool: List[int], n: int):
    rs = _rand_stream(key, step)
    return [pool[next(rs) % len(pool)] for _ in range(n)]

# ───────── GUI ─────────

class PixelSwapperApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Pixel Swapper 20×20")
        self.resizable(False, False)

        # tk variables
        self.src_var = tk.StringVar()
        self.dst_var = tk.StringVar()
        self.key_var = tk.StringVar()

        self._build_layout()
        self._running = False

    # Build layout
    def _build_layout(self):
        row = 0
        tk.Label(self, text="Исходная:").grid(row=row, column=0, sticky="e")
        tk.Entry(self, textvariable=self.src_var, width=28).grid(row=row, column=1)
        tk.Button(self, text="…", command=self._browse_src).grid(row=row, column=2)

        row += 1
        tk.Label(self, text="Полотно:").grid(row=row, column=0, sticky="e")
        tk.Entry(self, textvariable=self.dst_var, width=28).grid(row=row, column=1)
        tk.Button(self, text="…", command=self._browse_dst).grid(row=row, column=2)

        row += 1
        tk.Label(self, text="HEX‑ключ (64):").grid(row=row, column=0, sticky="e")
        tk.Entry(self, textvariable=self.key_var, width=34).grid(row=row, column=1)

        row += 1
        btn = tk.Frame(self)
        btn.grid(row=row, column=0, columnspan=3, pady=6)
        self.run_btn = tk.Button(btn, text="Старт", command=self._start)
        self.run_btn.pack(side="left", padx=(0, 4))
        self.stop_btn = tk.Button(btn, text="Стоп", state="disabled", command=self._stop)
        self.stop_btn.pack(side="left")

        row += 1
        self.progress = ttk.Progressbar(self, length=240, mode="determinate")
        self.progress.grid(row=row, column=0, columnspan=3)

        row += 1
        self.status = tk.Label(self, text="Готов.")
        self.status.grid(row=row, column=0, columnspan=3)

        row += 1
        prev = tk.Frame(self)
        prev.grid(row=row, column=0, columnspan=3, pady=4)
        self.src_lbl = tk.Label(prev)
        self.src_lbl.pack(side="left", padx=4)
        self.dst_lbl = tk.Label(prev)
        self.dst_lbl.pack(side="left", padx=4)

    # Dialog helpers
    def _browse_src(self):
        p = filedialog.askopenfilename(title="20×20 PNG", filetypes=[("PNG", "*.png")])
        if p:
            self.src_var.set(p)

    def _browse_dst(self):
        p = filedialog.askopenfilename(title="20×20 PNG", filetypes=[("PNG", "*.png")])
        if p:
            self.dst_var.set(p)

    # Start algorithm
    def _start(self):
        if self._running:
            return
        src, dst = self.src_var.get().strip(), self.dst_var.get().strip()
        if not src or not dst:
            messagebox.showerror("Ошибка", "Выберите обе картинки")
            return
        key_hex = self.key_var.get().strip()
        if key_hex and len(key_hex) != 64:
            messagebox.showerror("Ошибка", "HEX‑ключ должен быть 64 символа")
            return

        # Init state
        self.goal = image_to_list(Image.open(src))
        self.A = self.goal.copy()
        self.B = image_to_list(Image.open(dst))
        self.unlocked = [i for i in range(WIDTH * HEIGHT) if self.B[i] != self.goal[i]]
        self.pool = list(range(WIDTH * HEIGHT))
        self.key = os.urandom(32) if not key_hex else bytes.fromhex(key_hex)
        self.key_hex = self.key.hex()
        self.key_hash = hashlib.sha256(self.key).hexdigest()
        self.step = 0
        self.log: List[dict] = []
        self._running = True

        self._update_preview()
        self.run_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.status.config(text="Анимация…")
        self.progress.config(value=0, maximum=100)
        self.after(MS_DELAY, self._animate)

    def _stop(self):
        self._running = False
        self.run_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.status.config(text="Остановлено.")

    # Update previews
    def _update_preview(self):
        self._src_photo = ImageTk.PhotoImage(list_to_image(self.A).resize((WIDTH * SCALE, HEIGHT * SCALE), Image.NEAREST))
        self._dst_photo = ImageTk.PhotoImage(list_to_image(self.B).resize((WIDTH * SCALE, HEIGHT * SCALE), Image.NEAREST))
        self.src_lbl.config(image=self._src_photo)
        self.dst_lbl.config(image=self._dst_photo)

    # Main loop
    def _animate(self):
        if not self._running:
            return
        if not self.unlocked:
            self._finish()
            return

        dst_idx = _next_indices(self.key, self.step, self.unlocked, PAIRS_PER_STEP)
        src_idx = _next_indices(self.key, self.step + 1234, self.pool, PAIRS_PER_STEP)
        for ia, ib in zip(src_idx, dst_idx):
            self.A[ia], self.B[ib] = self.B[ib], self.A[ia]
        self.unlocked = [i for i in self.unlocked if self.B[i] != self.goal[i]]
        self.log.append({"step": self.step, "src": src_idx, "dst": dst_idx})
        self.step += 1

        self._update_preview()
        progress_val = int(100 * (1 - len(self.unlocked) / (WIDTH * HEIGHT)))
        self.progress.config(value=progress_val)
        self.after(MS_DELAY, self._animate)

    # Finish
    def _finish(self):
        self._running = False
        self.run_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.progress.config(value=100)
        with open("swap_log.json", "w", encoding="utf-8") as fp:
            json.dump({
                "key_hex": self.key_hex,
                "key_hash": self.key_hash,
                "steps": self.step,
                "log": self.log,
                "width": WIDTH,
                "height": HEIGHT,
                "pairs_per_step": PAIRS_PER_STEP,
            }, fp, indent=2, ensure_ascii=False)
        self.status.config(text="Готово. Журнал: swap_log.json")

# Run
if __name__ == "__main__":
    PixelSwapperApp().mainloop()

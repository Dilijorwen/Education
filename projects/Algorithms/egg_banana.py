import hashlib
import tkinter as tk
from tkinter import ttk

# ───── размеры и цвета ────────────────────────────────────────────────────
SIDE, PIX = 20, 24
CANVAS = SIDE * PIX

ON_COLOR_IN,  BG_COLOR_IN  = "#00e0ff", "#001a33"   # левое (input) поле
ON_COLOR_OUT, BG_COLOR_OUT = "#ff0066", "#33001a"   # правое (output) поле
GRID_COLOR = "#444444"

# ───── 1)  банан / яйцо ───────────────────────────────────────────────────
BANANA_BITS = [0]*(SIDE*SIDE)
EGG_BITS    = [0]*(SIDE*SIDE)

def _init_bitmaps():
    for y in range(SIDE):
        for x in range(SIDE):
            # банан-дуга
            if 4**2 <= (x-10)**2 + (y-10)**2 <= 8**2 and x >= 10 and y <= 15:
                BANANA_BITS[y*SIDE+x] = 1
            # яйцо-эллипс
            if ((x-10)**2)/25 + ((y-10)**2)/36 <= 1:
                EGG_BITS[y*SIDE+x] = 1
_init_bitmaps()

# ───── 2)  utils: 400 бит ↔ 50 байт ───────────────────────────────────────
def bits_to_bytes(bits):
    b = []
    for i in range(0, len(bits), 8):
        byte = 0
        for j in range(8):
            byte = (byte << 1) | bits[i + j]
        b.append(byte)
    return bytes(b)

def bytes_to_bits(data, length=SIDE*SIDE):
    bits = []
    for byte in data:
        for i in range(7, -1, -1):
            bits.append((byte >> i) & 1)
    return bits[:length]

# ───── 3)  400-битовый хэш (банан ↔ яйцо) ─────────────────────────────────
def _sha3_400(data: bytes) -> bytes:            # 50 байт = 400 бит
    return hashlib.sha3_512(data).digest()[:50]

MASK = bytes(a ^ b for a, b in zip(
    _sha3_400(bits_to_bytes(BANANA_BITS)),
    bits_to_bytes(EGG_BITS)
))

def hash400(bits):
    if bits == EGG_BITS:                        # яйцо → банан
        return bits_to_bytes(BANANA_BITS)
    raw = _sha3_400(bits_to_bytes(bits))        # банан → яйцо + лавина
    return bytes(a ^ b for a, b in zip(raw, MASK))

# ───── 4)  Tk-GUI ─────────────────────────────────────────────────────────
class PixelGrid(ttk.Frame):
    def __init__(self, master, editable, on_color, off_color):
        super().__init__(master)
        self.editable, self.on_color, self.off_color = editable, on_color, off_color

        self.canvas = tk.Canvas(
            self, width=CANVAS, height=CANVAS,
            highlightthickness=0, bg=off_color
        )
        self.canvas.pack()

        self.rects = [
            self.canvas.create_rectangle(
                x*PIX, y*PIX, (x+1)*PIX, (y+1)*PIX,
                outline=GRID_COLOR, fill=off_color
            )
            for y in range(SIDE) for x in range(SIDE)
        ]
        if editable:
            self.canvas.bind("<Button-1>", self._flip_pixel)

    # публичное API ---------------------------------------------------------
    def load_bits(self, bits):
        for idx, bit in enumerate(bits):
            self.canvas.itemconfig(
                self.rects[idx],
                fill=self.on_color if bit else self.off_color
            )

    def get_bits(self):
        return [
            0 if self.canvas.itemcget(r, "fill") == self.off_color else 1
            for r in self.rects
        ]

    # внутренняя обработка клика -------------------------------------------
    def _flip_pixel(self, ev):
        if not self.editable:
            return
        x, y = ev.x // PIX, ev.y // PIX
        if 0 <= x < SIDE and 0 <= y < SIDE:
            idx  = y * SIDE + x
            fill = self.canvas.itemcget(self.rects[idx], "fill")
            new  = self.off_color if fill != self.off_color else self.on_color
            self.canvas.itemconfig(self.rects[idx], fill=new)

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Banana ↔ Egg 400-bit hash demo")

        ttk.Label(self, text="Input").grid (row=0, column=0, pady=(4, 0))
        ttk.Label(self, text="Output").grid(row=0, column=2, pady=(4, 0))

        self.in_grid  = PixelGrid(self, True,  ON_COLOR_IN,  BG_COLOR_IN)
        self.out_grid = PixelGrid(self, False, ON_COLOR_OUT, BG_COLOR_OUT)

        self.in_grid.grid (row=1, column=0, padx=8, pady=8)
        self.out_grid.grid(row=1, column=2, padx=8, pady=8)

        # Кнопки -------------------------------------------------------------
        ttk.Button(self, text="Hash",
                   command=self._hash)\
            .grid(row=2, column=0, pady=(0, 10))

        ttk.Button(self, text="Swap",
                   command=self._swap)\
            .grid(row=2, column=2, pady=(0, 10))

        # Шаблоны для быстрой проверки
        ttk.Button(self, text="Load BANANA",
                   command=lambda: self.in_grid.load_bits(BANANA_BITS))\
            .grid(row=3, column=0, pady=(0, 4))
        ttk.Button(self, text="Load EGG",
                   command=lambda: self.in_grid.load_bits(EGG_BITS))\
            .grid(row=3, column=2, pady=(0, 4))

        self.in_grid.load_bits(BANANA_BITS)          # стартуем с банана

    # ── обработчики кнопок --------------------------------------------------
    def _hash(self):
        """Вычислить хэш левого поля и показать его справа."""
        inp_bits  = self.in_grid.get_bits()
        hashed    = bytes_to_bits(hash400(inp_bits))
        self.out_grid.load_bits(hashed)

    def _swap(self):
        """Поменять местами содержимое левого и правого полей."""
        left_bits  = self.in_grid.get_bits()
        right_bits = self.out_grid.get_bits()
        self.in_grid.load_bits(right_bits)
        self.out_grid.load_bits(left_bits)

# ───── запуск ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    App().mainloop()

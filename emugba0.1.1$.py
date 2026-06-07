import os
import sys
import tkinter as tk
from tkinter import messagebox

GBA_ROM_BASE = 0x08000000
GBA_MEMORY_SIZE = 0x04000000
GBA_CYCLES_PER_FRAME = 280896

# Built-in demo ROM (no external files needed)
DEFAULT_ROM = bytes.fromhex(
    "2e0000ea"
    "00000000000000000000000000000000"
    "00000000000000000000000000000000"
    "00000000000000000000000000000000"
    "00000000000000000000000000000000"
    "00000000000000000000000000000000"
    "44454d4f000000000000000000000000"
    "00000000000000000000000000000000"
    "00000000000000000000000000000000"
    "00000000000000000000000000000000"
    "00000000000000000000000000000000"
    "000000a0e3feffffea"
)


class MewGBACore:
    def __init__(self) -> None:
        self.pc = GBA_ROM_BASE
        self.memory = bytearray(GBA_MEMORY_SIZE)
        self.rom_label: str | None = None
        self.is_loaded = False

    def load_rom_bytes(self, rom: bytes, label: str = "Demo (built-in)") -> bool:
        if not rom:
            return False

        self.memory = bytearray(GBA_MEMORY_SIZE)
        for i, byte in enumerate(rom):
            if i + GBA_ROM_BASE >= GBA_MEMORY_SIZE:
                break
            self.memory[GBA_ROM_BASE + i] = byte

        self.pc = GBA_ROM_BASE
        self.rom_label = label
        self.is_loaded = True
        return True

    def step_frame(self) -> None:
        if not self.is_loaded:
            return

        cycles = 0
        while cycles < GBA_CYCLES_PER_FRAME:
            self.pc += 4
            cycles += 4


class MewGBAEmulator:
    def __init__(self, root: tk.Tk, rom_bytes: bytes | None = None, rom_label: str = "Demo (built-in)") -> None:
        self.root = root
        self.root.title("emugba0.1$")
        self.root.geometry("600x400")
        self.root.resizable(False, False)

        self.bg_color = "#0a192f"
        self.text_color = "#00b4d8"
        self.button_bg = "#000000"
        self.button_fg = "#00b4d8"
        self.screen_bg = "#020c1b"

        self.root.configure(bg=self.bg_color)

        self.core = MewGBACore()
        self.rom_bytes = rom_bytes if rom_bytes is not None else DEFAULT_ROM
        self.rom_label = rom_label
        self.core.load_rom_bytes(self.rom_bytes, self.rom_label)
        self.is_running = False

        self.setup_ui()

    def setup_ui(self) -> None:
        control_frame = tk.Frame(self.root, bg=self.bg_color)
        control_frame.pack(fill=tk.X, padx=10, pady=10)

        btn_style = {
            "bg": self.button_bg,
            "fg": self.button_fg,
            "activebackground": self.text_color,
            "activeforeground": self.button_bg,
            "font": ("Arial", 9, "bold"),
            "bd": 1,
            "relief": "solid",
        }

        self.run_btn = tk.Button(control_frame, text="Play", command=self.toggle_execution, **btn_style)
        self.run_btn.pack(side=tk.LEFT, padx=5)

        reset_btn = tk.Button(control_frame, text="Reset", command=self.reset_emulator, **btn_style)
        reset_btn.pack(side=tk.LEFT, padx=5)

        self.status_label = tk.Label(
            control_frame,
            text=f"ROM: {self.rom_label} (paused)",
            bg=self.bg_color,
            fg=self.text_color,
            font=("Arial", 10),
        )
        self.status_label.pack(side=tk.LEFT, padx=10)

        self.display_canvas = tk.Canvas(
            self.root,
            width=480,
            height=320,
            bg=self.screen_bg,
            highlightthickness=1,
            highlightbackground=self.text_color,
        )
        self.display_canvas.pack(pady=5)

    def reset_emulator(self) -> None:
        self.is_running = False
        self.run_btn.config(text="Play")
        self.core.load_rom_bytes(self.rom_bytes, self.rom_label)
        self.status_label.config(text=f"ROM: {self.rom_label} (paused)")

    def toggle_execution(self) -> None:
        if not self.core.is_loaded:
            messagebox.showwarning("Warning", "No ROM loaded.")
            return

        if not self.is_running:
            self.is_running = True
            self.run_btn.config(text="Pause")
            self.status_label.config(text=f"ROM: {self.rom_label} (running)")
            self.emulator_loop()
        else:
            self.is_running = False
            self.run_btn.config(text="Play")
            self.status_label.config(text=f"ROM: {self.rom_label} (paused)")

    def emulator_loop(self) -> None:
        if not self.is_running:
            return

        self.core.step_frame()
        self.root.after(16, self.emulator_loop)


def _load_startup_rom() -> tuple[bytes, str]:
    if len(sys.argv) >= 2:
        path = os.path.abspath(sys.argv[1])
        try:
            with open(path, "rb") as f:
                data = f.read()
            if data:
                return data, os.path.basename(path)
        except OSError as exc:
            messagebox.showerror("ROM Error", f"Could not load ROM:\n{exc}\nUsing built-in demo.")
    return DEFAULT_ROM, "Demo (built-in)"


if __name__ == "__main__":
    root = tk.Tk()
    rom, label = _load_startup_rom()
    MewGBAEmulator(root, rom, label)
    root.mainloop()

import os
import sys

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)

# ---------------------------------------------------------
# Compile the Cython extension on the fly (see gba_core.pyx)
# ---------------------------------------------------------
try:
    import pyximport
    pyximport.install(setup_args={"include_dirs": []}, language_level=3)
    from gba_core import MewGBACore
except Exception as e:
    print(f"Compilation warning: Make sure a C compiler (GCC/MSVC) is installed. Using fallback engine mode.")
    class MewGBACore:
        def __init__(self): self.is_loaded = False
        def load_rom(self, path): return True
        def step_frame(self): pass

# ---------------------------------------------------------
# STEP 3: Setup the mGBA-Inspired Blue Hue Tkinter GUI
# ---------------------------------------------------------
import tkinter as tk
from tkinter import filedialog, messagebox

class MewGBAEmulator:
    def __init__(self, root):
        self.root = root
        self.root.title("emugba0.1$")
        self.root.geometry("600x400")
        self.root.resizable(False, False)

        # Style Palette Configuration
        self.bg_color = "#0a192f"       # Deep blue hue background
        self.text_color = "#00b4d8"     # Bright blue text
        self.button_bg = "#000000"     # Black button background
        self.button_fg = "#00b4d8"     # Blue text color for buttons
        self.screen_bg = "#020c1b"     # Dark screen viewport

        self.root.configure(bg=self.bg_color)
        
        # Initialize Cython backend core engine
        self.core = MewGBACore()
        self.is_running = False

        self.setup_ui()

    def setup_ui(self):
        # Top Header Control layout
        control_frame = tk.Frame(self.root, bg=self.bg_color)
        control_frame.pack(fill=tk.X, padx=10, pady=10)

        btn_style = {
            "bg": self.button_bg,
            "fg": self.button_fg,
            "activebackground": self.text_color,
            "activeforeground": self.button_bg,
            "font": ("Arial", 9, "bold"),
            "bd": 1,
            "relief": "solid"
        }

        # Control UI interaction buttons
        load_btn = tk.Button(control_frame, text="Load GBA ROM", command=self.open_rom, **btn_style)
        load_btn.pack(side=tk.LEFT, padx=5)

        self.run_btn = tk.Button(control_frame, text="Play", command=self.toggle_execution, **btn_style)
        self.run_btn.pack(side=tk.LEFT, padx=5)

        self.status_label = tk.Label(
            control_frame, 
            text="System Status: Ready", 
            bg=self.bg_color, 
            fg=self.text_color,
            font=("Arial", 10)
        )
        self.status_label.pack(side=tk.LEFT, padx=10)

        # Main Display Screen (Simulated GBA LCD Viewport)
        self.display_canvas = tk.Canvas(
            self.root,
            width=480,
            height=320,
            bg=self.screen_bg,
            highlightthickness=1,
            highlightbackground=self.text_color
        )
        self.display_canvas.pack(pady=5)

    def open_rom(self):
        file_path = filedialog.askopenfilename(
            title="Open Game Boy Advance ROM",
            filetypes=[("GBA ROMs", "*.gba"), ("All Files", "*.*")]
        )
        if file_path:
            success = self.core.load_rom(file_path)
            if success:
                filename = os.path.basename(file_path)
                self.status_label.config(text=f"ROM: {filename}")
            else:
                messagebox.showerror("Error", "Failed to parse binary file structure.")

    def toggle_execution(self):
        if not self.is_running:
            self.is_running = True
            self.run_btn.config(text="Pause")
            self.emulator_loop()
        else:
            self.is_running = False
            self.run_btn.config(text="Play")

    def emulator_loop(self):
        if not self.is_running:
            return
            
        # Run emulation code loop safely
        self.core.step_frame()
        self.root.after(16, self.emulator_loop)

if __name__ == "__main__":
    root = tk.Tk()
    app = MewGBAEmulator(root)
    root.mainloop()
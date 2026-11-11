
import cv2
import numpy as np
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk, ImageDraw
from pathlib import Path
import os

# ==========================================
# KONFIGURASI APLIKASI
# ==========================================

APP_NAME = "IMAGE PROCESSING STUDIO"
BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "hasil"
OUTPUT_DIR.mkdir(exist_ok=True)

FILTERS = [
    "Mean 3x3",
    "Mean 5x5",
    "Gaussian 3x3",
    "Gaussian 5x5",
    "Median 3x3",
    "Median 5x5",
    "Sharpening"
]


# ==========================================
# CLASS APLIKASI
# ==========================================

class ImageProcessingApp:

    def __init__(self, root):

        self.root = root
        self.root.title(APP_NAME)
        self.root.geometry("1250x850")
        self.root.minsize(1000, 700)
        self.root.configure(bg="#101827")

        self.original = None
        self.gray = None
        self.current_result = None
        self.current_filter = None
        self.results = {}

        self.original_photo = None
        self.result_photo = None
        self.grid_photos = []

        self.setup_style()
        self.create_interface()

    # ======================================
    # STYLE
    # ======================================

    def setup_style(self):

        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "TCombobox",
            fieldbackground="#263449",
            background="#263449",
            foreground="white",
            arrowcolor="white"
        )

        style.configure(
            "Treeview",
            background="#1D2A3D",
            foreground="white",
            fieldbackground="#1D2A3D",
            rowheight=28,
            borderwidth=0
        )

        style.configure(
            "Treeview.Heading",
            background="#263449",
            foreground="white",
            font=("Segoe UI", 9, "bold")
        )

        style.map(
            "Treeview",
            background=[("selected", "#2563EB")]
        )

    # ======================================
    # MEMBUAT INTERFACE
    # ======================================

    def create_interface(self):

        header = tk.Frame(
            self.root,
            bg="#17243A",
            height=85
        )
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(
            header,
            text="IMAGE PROCESSING STUDIO",
            font=("Segoe UI", 20, "bold"),
            fg="#FFFFFF",
            bg="#17243A"
        ).pack(anchor="w", padx=25, pady=(15, 0))

        tk.Label(
            header,
            text="DIGITAL IMAGE PROCESSING | SPATIAL FILTER",
            font=("Segoe UI", 9),
            fg="#94A3B8",
            bg="#17243A"
        ).pack(anchor="w", padx=27)

        # MAIN CONTAINER

        main = tk.Frame(
            self.root,
            bg="#101827"
        )
        main.pack(fill="both", expand=True, padx=22, pady=18)

        # CONTROL PANEL

        control = tk.Frame(
            main,
            bg="#1D2A3D",
            padx=15,
            pady=15
        )
        control.pack(fill="x", pady=(0, 15))

        tk.Label(
            control,
            text="PENGATURAN FILTER",
            font=("Segoe UI", 11, "bold"),
            fg="white",
            bg="#1D2A3D"
        ).grid(row=0, column=0, sticky="w", pady=(0, 12))

        tk.Button(
            control,
            text="  Buka Citra  ",
            command=self.open_image,
            bg="#2563EB",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            cursor="hand2"
        ).grid(row=1, column=0, padx=(0, 15), sticky="w")

        self.filter_var = tk.StringVar(
            value="Mean 3x3"
        )

        self.filter_box = ttk.Combobox(
            control,
            textvariable=self.filter_var,
            values=FILTERS,
            state="readonly",
            width=20
        )
        self.filter_box.grid(
            row=1, column=1, padx=10
        )

        tk.Button(
            control,
            text="  Proses Filter  ",
            command=self.process_filter,
            bg="#059669",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            cursor="hand2"
        ).grid(row=1, column=2, padx=10)

        tk.Button(
            control,
            text="  Proses Semua  ",
            command=self.process_all,
            bg="#7C3AED",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            cursor="hand2"
        ).grid(row=1, column=3, padx=10)

        tk.Button(
            control,
            text="  Simpan Hasil  ",
            command=self.save_result,
            bg="#D97706",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            cursor="hand2"
        ).grid(row=1, column=4, padx=10)

        # IMAGE PREVIEW

        preview = tk.Frame(
            main,
            bg="#101827"
        )
        preview.pack(fill="both", expand=True)

        self.original_frame = self.create_preview(
            preview,
            "CITRA ASLI",
            0
        )

        self.result_frame = self.create_preview(
            preview,
            "HASIL FILTER",
            1
        )

        # STATISTICS

        stats_container = tk.Frame(
            main,
            bg="#1D2A3D",
            padx=12,
            pady=12
        )
        stats_container.pack(fill="x", pady=(15, 0))

        tk.Label(
            stats_container,
            text="STATISTIK INTENSITAS CITRA",
            font=("Segoe UI", 11, "bold"),
            fg="white",
            bg="#1D2A3D"
        ).pack(anchor="w", pady=(0, 10))

        columns = (
            "Metode",
            "Rata-rata",
            "Std Deviasi",
            "Minimum",
            "Maksimum",
            "Tepi Canny (%)"
        )

        self.table = ttk.Treeview(
            stats_container,
            columns=columns,
            show="headings",
            height=4
        )

        for col in columns:
            self.table.heading(col, text=col)
            self.table.column(
                col,
                width=140,
                anchor="center"
            )

        self.table.pack(fill="x")

        # STATUS BAR

        self.status = tk.Label(
            self.root,
            text="Siap. Silakan buka citra untuk memulai.",
            bg="#17243A",
            fg="#94A3B8",
            font=("Segoe UI", 9),
            anchor="w",
            padx=20,
            pady=10
        )
        self.status.pack(fill="x")

    # ======================================
    # PREVIEW FRAME
    # ======================================

    def create_preview(self, parent, title, column):

        frame = tk.Frame(
            parent,
            bg="#1D2A3D",
            padx=12,
            pady=12
        )

        frame.pack(
            side="left",
            fill="both",
            expand=True,
            padx=7
        )

        tk.Label(
            frame,
            text=title,
            font=("Segoe UI", 11, "bold"),
            fg="white",
            bg="#1D2A3D"
        ).pack(anchor="w", pady=(0, 10))

        image_label = tk.Label(
            frame,
            text="Belum ada gambar",
            bg="#263449",
            fg="#94A3B8",
            font=("Segoe UI", 11),
            width=40,
            height=15
        )

        image_label.pack(
            fill="both",
            expand=True
        )

        if column == 0:
            self.original_label = image_label
        else:
            self.result_label = image_label

        return frame

    # ======================================
    # MEMBUKA CITRA
    # ======================================

    def open_image(self):

        path = filedialog.askopenfilename(
            title="Pilih Citra",
            filetypes=[
                ("Image Files", "*.png *.jpg *.jpeg *.bmp"),
                ("All Files", "*.*")
            ]
        )

        if not path:
            return

        image = cv2.imread(path)

        if image is None:
            messagebox.showerror(
                "Error",
                "Gambar tidak dapat dibaca."
            )
            return

        self.original = image

        self.gray = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2GRAY
        )

        self.results.clear()
        self.current_result = None
        self.current_filter = None

        self.display_image(
            self.gray,
            self.original_label,
            "original"
        )

        self.result_label.config(
            image="",
            text="Pilih filter untuk memulai"
        )

        self.clear_table()

        h, w = self.gray.shape

        self.status.config(
            text=f"Citra berhasil dibuka: {os.path.basename(path)} | Resolusi: {w} x {h}"
        )

    # ======================================
    # PROSES FILTER
    # ======================================

    def apply_filter(self, name):

        if name == "Mean 3x3":

            return cv2.blur(
                self.gray,
                (3, 3)
            )

        elif name == "Mean 5x5":

            return cv2.blur(
                self.gray,
                (5, 5)
            )

        elif name == "Gaussian 3x3":

            return cv2.GaussianBlur(
                self.gray,
                (3, 3),
                0
            )

        elif name == "Gaussian 5x5":

            return cv2.GaussianBlur(
                self.gray,
                (5, 5),
                0
            )

        elif name == "Median 3x3":

            return cv2.medianBlur(
                self.gray,
                3
            )

        elif name == "Median 5x5":

            return cv2.medianBlur(
                self.gray,
                5
            )

        elif name == "Sharpening":

            blurred = cv2.GaussianBlur(
                self.gray,
                (5, 5),
                0
            )

            sharpened = cv2.addWeighted(
                self.gray,
                1.5,
                blurred,
                -0.5,
                0
            )

            return sharpened

    # ======================================
    # HITUNG STATISTIK
    # ======================================

    def calculate_metrics(self, image):

        mean = np.mean(image)

        std = np.std(image)

        minimum = np.min(image)

        maximum = np.max(image)

        edges = cv2.Canny(
            image,
            80,
            160
        )

        edge_percentage = (
            np.count_nonzero(edges) /
            edges.size
        ) * 100

        return {
            "mean": mean,
            "std": std,
            "min": minimum,
            "max": maximum,
            "edge": edge_percentage
        }

    # ======================================
    # PROSES SATU FILTER
    # ======================================

    def process_filter(self):

        if self.gray is None:

            messagebox.showwarning(
                "Peringatan",
                "Silakan buka gambar terlebih dahulu."
            )
            return

        name = self.filter_var.get()

        result = self.apply_filter(name)

        self.current_result = result
        self.current_filter = name

        self.results[name] = result

        self.display_image(
            result,
            self.result_label,
            "result"
        )

        self.update_table(name, result)

        self.status.config(
            text=f"Berhasil memproses: {name}"
        )

    # ======================================
    # PROSES SEMUA FILTER
    # ======================================

    def process_all(self):

        if self.gray is None:

            messagebox.showwarning(
                "Peringatan",
                "Silakan buka gambar terlebih dahulu."
            )
            return

        self.results.clear()

        self.clear_table()

        # Statistik citra asli

        self.update_table(
            "Citra Asli",
            self.gray
        )

        # Seluruh filter

        for name in FILTERS:

            result = self.apply_filter(name)

            self.results[name] = result

            self.update_table(
                name,
                result
            )

        self.current_result = None
        self.current_filter = None

        self.status.config(
            text="Semua filter berhasil diproses."
        )

        self.show_all_results()

    # ======================================
    # TAMPILKAN SEMUA HASIL
    # ======================================

    def show_all_results(self):

        window = tk.Toplevel(self.root)

        window.title("Perbandingan Filter Spasial")

        window.geometry("1100x750")

        window.configure(bg="#101827")

        tk.Label(
            window,
            text="PERBANDINGAN HASIL FILTER SPASIAL",
            font=("Segoe UI", 17, "bold"),
            fg="white",
            bg="#101827"
        ).pack(pady=15)

        container = tk.Frame(
            window,
            bg="#101827"
        )
        container.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=10
        )

        self.grid_photos = []

        all_images = {
            "Citra Asli": self.gray,
            **self.results
        }

        for index, (name, image) in enumerate(all_images.items()):

            card = tk.Frame(
                container,
                bg="#1D2A3D",
                padx=10,
                pady=10
            )

            card.grid(
                row=index // 4,
                column=index % 4,
                padx=8,
                pady=8,
                sticky="nsew"
            )

            tk.Label(
                card,
                text=name,
                bg="#1D2A3D",
                fg="white",
                font=("Segoe UI", 10, "bold")
            ).pack(pady=(0, 8))

            pil_image = Image.fromarray(image)

            pil_image.thumbnail((230, 180))

            photo = ImageTk.PhotoImage(pil_image)

            self.grid_photos.append(photo)

            tk.Label(
                card,
                image=photo,
                bg="#263449"
            ).pack()

            metrics = self.calculate_metrics(image)

            tk.Label(
                card,
                text=f"Mean: {metrics['mean']:.2f}\n"
                     f"Std: {metrics['std']:.2f}",
                bg="#1D2A3D",
                fg="#94A3B8",
                font=("Segoe UI", 9)
            ).pack(pady=5)

        for col in range(4):
            container.grid_columnconfigure(
                col,
                weight=1
            )

    # ======================================
    # TAMPILKAN GAMBAR
    # ======================================

    def display_image(self, image, label, target):

        pil_image = Image.fromarray(image)

        pil_image.thumbnail((480, 350))

        photo = ImageTk.PhotoImage(pil_image)

        label.config(
            image=photo,
            text=""
        )

        if target == "original":
            self.original_photo = photo
        else:
            self.result_photo = photo

    # ======================================
    # UPDATE TABEL STATISTIK
    # ======================================

    def update_table(self, name, image):

        metrics = self.calculate_metrics(image)

        values = (
            name,
            f"{metrics['mean']:.2f}",
            f"{metrics['std']:.2f}",
            int(metrics["min"]),
            int(metrics["max"]),
            f"{metrics['edge']:.2f}"
        )

        self.table.insert(
            "",
            "end",
            values=values
        )

    def clear_table(self):

        for item in self.table.get_children():

            self.table.delete(item)

    # ======================================
    # SIMPAN HASIL FILTER
    # ======================================

    def save_result(self):

        if self.current_result is None:

            messagebox.showwarning(
                "Peringatan",
                "Proses satu filter terlebih dahulu sebelum menyimpan."
            )
            return

        path = filedialog.asksaveasfilename(
            title="Simpan Hasil Filter",
            initialdir=OUTPUT_DIR,
            initialfile=f"{self.current_filter.replace(' ', '_')}.png",
            defaultextension=".png",
            filetypes=[
                ("PNG Image", "*.png"),
                ("JPEG Image", "*.jpg")
            ]
        )

        if not path:
            return

        success = cv2.imwrite(
            path,
            self.current_result
        )

        if success:

            messagebox.showinfo(
                "Berhasil",
                f"Hasil berhasil disimpan:\n{path}"
            )

    # ======================================
    # JALANKAN APLIKASI
    # ======================================


if __name__ == "__main__":

    root = tk.Tk()

    app = ImageProcessingApp(root)

    root.mainloop()

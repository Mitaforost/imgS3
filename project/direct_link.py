import tkinter as tk
from tkinter import ttk
import requests
from PIL import Image
import io
import os
from tkinter import filedialog, messagebox
import threading

class FileDownloaderFrame(tk.Frame):
    def __init__(self, master, title, is_custom=False):
        super().__init__(master)
        self.configure(bg="#f9f9f9")
        self.title_label = tk.Label(self, text=title, font=("Arial", 16, "bold"), bg="#f9f9f9")
        self.title_label.pack(pady=15)
        self.is_custom = is_custom

class DirectLinkFrame(FileDownloaderFrame):
    def __init__(self, master):
        super().__init__(master, "Direct Link")
        self.found_files = {}
        self.viewed_images = {}
        self.download_folder = None
        self.create_widgets()

    def create_widgets(self):
        # Input Frame
        self.input_frame = tk.Frame(self, bg="#f9f9f9")
        self.input_frame.pack(padx=20, pady=10, fill="x")

        # URL and File Name Input
        self.create_url_entry()
        self.create_file_name_entry()
        self.create_file_extension_entry()
        self.create_range_selection()

        # File Count Label
        self.file_count_var = tk.StringVar(value="Found 0 files.")
        self.file_count_label = tk.Label(self.input_frame, textvariable=self.file_count_var, bg="#f9f9f9", font=("Arial", 10))
        self.file_count_label.grid(row=8, column=0, columnspan=2, pady=5, sticky="w")

        # Find Button
        self.find_button = tk.Button(self.input_frame, text="Find Files", command=self.find_files, bg="#4CAF50", fg="white", font=("Arial", 12))
        self.find_button.grid(row=9, column=0, columnspan=2, pady=10, sticky="ew")

        # Output Frame (Right)
        self.right_frame = tk.Frame(self, bg="#f9f9f9")
        self.right_frame.pack(padx=20, pady=10, fill="both", expand=True)

        # File Table
        self.file_table = ttk.Treeview(self.right_frame, columns=("num", "filename", "filesize", "width", "height"),
                                       show="headings", style="Custom.Treeview")
        self.file_table.heading("num", text="No.")
        self.file_table.heading("filename", text="File Name")
        self.file_table.heading("filesize", text="Size (KB)")
        self.file_table.heading("width", text="Width (px)")
        self.file_table.heading("height", text="Height (px)")
        self.file_table.bind("<Double-1>", self.preview_file)

        self.file_table.pack(fill=tk.BOTH, expand=True, pady=10)

        # # Progress Bar
        # self.progress = ttk.Progressbar(self.right_frame, orient="horizontal", length=300, mode="determinate")
        # self.progress.pack(pady=10)

        # Download Button
        self.download_button = tk.Button(self.right_frame, text="Download Files", state=tk.DISABLED,
                                         command=self.select_download_folder, bg="#2196F3", fg="white", font=("Arial", 12))
        self.download_button.pack(pady=10)

        # Custom Style for Treeview
        self.style = ttk.Style()
        self.style.configure("Custom.Treeview", background="#4CAF50", foreground="#000000", fieldbackground="#ffffff")
        self.style.configure("Custom.Treeview.Heading", background="#4CAF50", foreground="orange")

    def create_url_entry(self):
        tk.Label(self.input_frame, text="Base URL:", bg="#f9f9f9", font=("Arial", 10)).grid(row=1, column=0, sticky="w")
        self.url_entry = tk.Entry(self.input_frame, width=80, font=("Arial", 12))
        self.url_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        self.url_entry.insert(0, "https://pixeland-meducate.s3.eu-west-2.amazonaws.com/art/art_basics/")

    def create_file_name_entry(self):
        tk.Label(self.input_frame, text="Base File Name:", bg="#f9f9f9", font=("Arial", 10)).grid(row=2, column=0, sticky="w")
        self.base_name_entry = tk.Entry(self.input_frame, width=30, font=("Arial", 12))
        self.base_name_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        self.base_name_entry.insert(0, "Art_B_L")

    def create_file_extension_entry(self):
        tk.Label(self.input_frame, text="File Extension:", bg="#f9f9f9", font=("Arial", 10)).grid(row=3, column=0, sticky="w")
        self.file_extension_entry = tk.Entry(self.input_frame, width=10, font=("Arial", 12))
        self.file_extension_entry.grid(row=3, column=1, padx=5, pady=5, sticky="w")
        self.file_extension_entry.insert(0, "png")

    def create_range_selection(self):
        tk.Label(self.input_frame, text="Range N:", bg="#f9f9f9", font=("Arial", 10)).grid(row=4, column=0, sticky="w")
        self.range_n_menu = ttk.Combobox(self.input_frame, font=("Arial", 12))
        self.range_n_menu['values'] = ['1-6']
        self.range_n_menu.grid(row=4, column=1, padx=5, pady=5, sticky="ew")

        tk.Label(self.input_frame, text="Range M:", bg="#f9f9f9", font=("Arial", 10)).grid(row=5, column=0, sticky="w")
        self.range_m_menu = ttk.Combobox(self.input_frame, font=("Arial", 12))
        self.range_m_menu['values'] = ['1-25']
        self.range_m_menu.grid(row=5, column=1, padx=5, pady=5, sticky="ew")

        tk.Label(self.input_frame, text="Range A:", bg="#f9f9f9", font=("Arial", 10)).grid(row=6, column=0, sticky="w")
        self.range_a_menu = ttk.Combobox(self.input_frame, font=("Arial", 12))
        self.range_a_menu['values'] = ['1-6']
        self.range_a_menu.grid(row=6, column=1, padx=5, pady=5, sticky="ew")

    def find_files(self):
        self.file_table.delete(*self.file_table.get_children())
        self.file_count_var.set("Finding files...")
        if not self.validate_inputs():
            return
        thread = threading.Thread(target=self.search_files)
        thread.start()

    def validate_inputs(self):
        if not self.url_entry.get().strip():
            self.show_error("Base URL cannot be empty.")
            return False

        if not self.base_name_entry.get().strip():
            self.show_error("Base File Name cannot be empty.")
            return False

        if not self.file_extension_entry.get().strip():
            self.show_error("File Extension cannot be empty.")
            return False

        for menu in [self.range_n_menu, self.range_m_menu, self.range_a_menu]:
            try:
                values = list(map(int, menu.get().split('-')))
                if len(values) != 2 or values[0] > values[1]:
                    self.show_error(f"Invalid range in {menu.get()}. Use 'start-end'.")
                    return False
            except ValueError:
                self.show_error(f"Invalid range in {menu.get()}. Use 'start-end'.")
                return False

        return True

    def search_files(self):
        base_url = self.url_entry.get().rstrip('/')
        base_file_name = self.base_name_entry.get()
        file_extension = self.file_extension_entry.get()
        range_n = list(map(int, self.range_n_menu.get().split('-')))
        range_m = list(map(int, self.range_m_menu.get().split('-')))
        range_a = list(map(int, self.range_a_menu.get().split('-')))

        range_n = range(range_n[0], range_n[1] + 1)
        range_m = range(range_m[0], range_m[1] + 1)
        range_a = range(range_a[0], range_a[1] + 1)

        self.found_files = {}

        for n in range_n:
            file_name = f"{base_file_name}{n}_1.{file_extension}"
            file_url = f"{base_url}/{file_name}"
            print(f"Searching for: {file_url}")

            if not self.file_exists(file_url):
                print(f"Not found: {file_url}, skipping further search for n={n}")
                continue

            file_info = self.get_file_info(file_url)
            self.add_file(file_url, file_name, file_info)
            self.update_file_table()

            self.search_nested_files(n, base_file_name, file_extension, base_url, range_m, range_a)

        self.file_count_var.set(f"Found {len(self.found_files)} files.")
        self.download_button.config(state=tk.NORMAL if self.found_files else tk.DISABLED)

    def search_nested_files(self, base_n, base_file_name, file_extension, base_url, range_m, range_a):
        for m in range_m:
            file_name = f"{base_file_name}{base_n}_{m}.{file_extension}"
            file_url = f"{base_url}/{file_name}"
            print(f"Searching for: {file_url}")

            # Пробуем найти файл n_m
            if not self.file_exists(file_url):
                print(f"Not found: {file_url}, but continuing search for n={base_n}, m={m}")

                # Пробуем искать хотя бы один файл n_m-a
                if not self.search_a_files(base_n, m, base_file_name, file_extension, base_url, range_a):
                    print(f"Skipping further search for n={base_n}, m={m} as no n_m-a files found.")
                    break
                else:
                    # Если хотя бы один файл n_m-a найден, продолжаем
                    continue

            file_info = self.get_file_info(file_url)
            self.add_file(file_url, file_name, file_info)
            self.update_file_table()

            # Поиск файлов по a
            self.search_a_files(base_n, m, base_file_name, file_extension, base_url, range_a)

    def search_a_files(self, base_n, m, base_file_name, file_extension, base_url, range_a):
        found_any_a_file = False  # Флаг, нашли ли мы хотя бы один файл в диапазоне a

        for a in range_a:
            file_name = f"{base_file_name}{base_n}_{m}-{a}.{file_extension}"
            file_url = f"{base_url}/{file_name}"
            print(f"Searching for: {file_url}")

            if not self.file_exists(file_url):
                print(f"Not found: {file_url}, skipping file {file_name}")
                continue

            # Если найден файл n_m-a, устанавливаем флаг и добавляем файл
            found_any_a_file = True
            file_info = self.get_file_info(file_url)
            self.add_file(file_url, file_name, file_info)
            self.update_file_table()

        return found_any_a_file  # Возвращаем True, если найден хотя бы один файл n_m-a

    def file_exists(self, file_url):
        try:
            response = requests.head(file_url, allow_redirects=True)
            return response.status_code == 200
        except requests.RequestException as e:
            print(f"Error checking file: {e}")
            return False

    def get_file_info(self, file_url):
        try:
            response = requests.get(file_url, stream=True)
            img = Image.open(io.BytesIO(response.content))
            width, height = img.size
            size_kb = len(response.content) / 1024
            return size_kb, width, height
        except Exception as e:
            print(f"Error getting file info: {e}")
            return 0, 0, 0

    def add_file(self, file_url, file_name, file_info):
        size_kb, width, height = file_info
        if file_name not in self.found_files:
            self.found_files[file_name] = {
                "url": file_url,
                "size_kb": size_kb,
                "width": width,
                "height": height
            }

    def update_file_table(self):
        self.file_table.delete(*self.file_table.get_children())
        for idx, (file_name, file_info) in enumerate(self.found_files.items(), start=1):
            self.file_table.insert("", "end", values=(idx, file_name, f"{file_info['size_kb']:.2f}", file_info['width'], file_info['height']))

    def select_download_folder(self):
        self.download_folder = filedialog.askdirectory()
        if not self.download_folder:
            return
        self.download_files()

    def download_files(self):
        if not self.download_folder:
            self.show_error("Download folder is not set.")
            return

        for file_name, file_info in self.found_files.items():
            file_url = file_info["url"]
            file_path = os.path.join(self.download_folder, file_name)
            self.download_file(file_url, file_path)

        messagebox.showinfo("Download Complete", f"Files have been downloaded to {self.download_folder}.")

    def download_file(self, file_url, file_path):
        try:
            response = requests.get(file_url, stream=True)
            with open(file_path, "wb") as f:
                f.write(response.content)
        except Exception as e:
            print(f"Error downloading file {file_url}: {e}")

    def preview_file(self, event):
        selected_item = self.file_table.selection()
        if not selected_item:
            return
        item = self.file_table.item(selected_item)
        file_url = next((file_info["url"] for file_name, file_info in self.found_files.items() if file_name == item["values"][1]), None)
        if file_url:
            self.show_image_preview(file_url)

    def show_image_preview(self, file_url):
        try:
            response = requests.get(file_url)
            img = Image.open(io.BytesIO(response.content))
            img.show()
        except Exception as e:
            print(f"Error displaying image: {e}")

    def on_right_click(self, event):
        menu = tk.Menu(self.file_table, tearoff=0)
        menu.add_command(label="Preview", command=self.preview_file)
        menu.post(event.x_root, event.y_root)

    def show_error(self, message):
        messagebox.showerror("Error", message)

class CustomLinkFrame(FileDownloaderFrame):
    def __init__(self, master):
        super().__init__(master, "Custom Link", True)
        self.create_widgets()

    def create_widgets(self):
        self.input_frame = tk.Frame(self, bg="#f0f0f0")
        self.input_frame.pack(padx=20, pady=20, fill="x")

        self.create_base_url_entry()
        self.create_base_file_name_entry()
        self.create_file_extension_entry()
        self.create_range_selection()

        self.file_count_var = tk.StringVar()
        self.file_count_var.set("Found 0 files.")
        self.file_count_label = tk.Label(self.input_frame, textvariable=self.file_count_var, bg="#f0f0f0")
        self.file_count_label.grid(row=8, column=0, columnspan=2, pady=5)

        self.find_button = tk.Button(self.input_frame, text="Find Files", command=self.find_files, bg="#4CAF50", fg="white", font=("Arial", 12))
        self.find_button.grid(row=9, column=0, columnspan=2, pady=10, padx=5)

        self.right_frame = tk.Frame(self, bg="#f0f0f0")
        self.right_frame.pack(padx=20, pady=20, fill="both", expand=True)

        self.file_table = ttk.Treeview(self.right_frame, columns=("num", "filename", "filesize", "width", "height"),
                                       show="headings", style="Custom.Treeview")
        self.file_table.heading("num", text="No.")
        self.file_table.heading("filename", text="File Name")
        self.file_table.heading("filesize", text="Size (KB)")
        self.file_table.heading("width", text="Width (px)")
        self.file_table.heading("height", text="Height (px)")
        self.file_table.bind("<Double-1>", self.preview_file)
        self.file_table.bind("<Button-3>", self.on_right_click)

        self.file_table.pack(fill=tk.BOTH, expand=True)

        self.progress = ttk.Progressbar(self.right_frame, orient="horizontal", length=300, mode="determinate")
        self.progress.pack(pady=10)

        self.download_button = tk.Button(self.right_frame, text="Download Files", state=tk.DISABLED,
                                         command=self.select_download_folder, bg="#2196F3", fg="white", font=("Arial", 12))
        self.download_button.pack(pady=10)

        self.style = ttk.Style()
        self.style.configure("Custom.Treeview",
                             background="#ffffff",
                             foreground="#000000",
                             fieldbackground="#ffffff")
        self.style.configure("Custom.Treeview.Heading",
                             background="#4CAF50",
                             foreground="white")

    def create_base_url_entry(self):
        tk.Label(self.input_frame, text="Base URL:", bg="#f0f0f0").grid(row=1, column=0, sticky="w")
        self.url_entry = tk.Entry(self.input_frame, width=50, font=("Arial", 12))
        self.url_entry.grid(row=1, column=1, padx=5, pady=5)
        self.url_entry.insert(0, "https://pixeland-meducate.s3.eu-west-2.amazonaws.com/art/art_basics/")

    def create_base_file_name_entry(self):
        tk.Label(self.input_frame, text="Base File Name:", bg="#f0f0f0").grid(row=2, column=0, sticky="w")
        self.base_name_entry = tk.Entry(self.input_frame, width=50, font=("Arial", 12))
        self.base_name_entry.grid(row=2, column=1, padx=5, pady=5)
        self.base_name_entry.insert(0, "Art_B_L")

    def create_file_extension_entry(self):
        tk.Label(self.input_frame, text="File Extension:", bg="#f0f0f0").grid(row=3, column=0, sticky="w")
        self.file_extension_entry = tk.Entry(self.input_frame, width=50, font=("Arial", 12))
        self.file_extension_entry.grid(row=3, column=1, padx=5, pady=5)
        self.file_extension_entry.insert(0, "png")

    def create_range_selection(self):
        tk.Label(self.input_frame, text="Range N:", bg="#f0f0f0").grid(row=4, column=0, sticky="w")
        self.range_n_menu = ttk.Combobox(self.input_frame, font=("Arial", 12))
        self.range_n_menu['values'] = ['1-6']
        self.range_n_menu.grid(row=4, column=1, padx=5, pady=5)

        tk.Label(self.input_frame, text="Range M:", bg="#f0f0f0").grid(row=5, column=0, sticky="w")
        self.range_m_menu = ttk.Combobox(self.input_frame, font=("Arial", 12))
        self.range_m_menu['values'] = ['1-25']
        self.range_m_menu.grid(row=5, column=1, padx=5, pady=5)

        tk.Label(self.input_frame, text="Range A:", bg="#f0f0f0").grid(row=6, column=0, sticky="w")
        self.range_a_menu = ttk.Combobox(self.input_frame, font=("Arial", 12))
        self.range_a_menu['values'] = ['1-6']
        self.range_a_menu.grid(row=6, column=1, padx=5, pady=5)

    def find_files(self):
        self.file_table.delete(*self.file_table.get_children())
        self.file_count_var.set("Finding files...")

        if not self.validate_inputs():
            return

        thread = threading.Thread(target=self.search_files)
        thread.start()

    def validate_inputs(self):
        if not self.url_entry.get().strip():
            self.show_error("Base URL cannot be empty.")
            return False
        if not self.base_name_entry.get().strip():
            self.show_error("Base File Name cannot be empty.")
            return False
        if not self.file_extension_entry.get().strip():
            self.show_error("File Extension cannot be empty.")
            return False
        return True

    def search_files(self):
        base_url = self.url_entry.get().strip()
        base_n = self.base_name_entry.get().strip()
        file_extension = self.file_extension_entry.get().strip()

        range_n = self.range_n_menu.get().strip().split('-')
        range_m = self.range_m_menu.get().strip().split('-')
        range_a = self.range_a_menu.get().strip().split('-')

        n_start, n_end = int(range_n[0]), int(range_n[1])
        m_start, m_end = int(range_m[0]), int(range_m[1])
        a_start, a_end = int(range_a[0]), int(range_a[1])

        self.found_files = {}
        total_files = (n_end - n_start + 1) * (m_end - m_start + 1) * (a_end - a_start + 1)
        self.progress["maximum"] = total_files
        self.progress["value"] = 0

        for n in range(n_start, n_end + 1):
            for m in range(m_start, m_end + 1):
                for a in range(a_start, a_end + 1):
                    file_name = f"{base_n}_{n}-{m}-{a}.{file_extension}"
                    file_url = f"{base_url}/{file_name}"
                    print(f"Searching for: {file_url}")

                    if not self.file_exists(file_url):
                        print(f"Not found: {file_url}")
                        continue

                    file_info = self.get_file_info(file_url)
                    self.add_file(file_url, file_name, file_info)
                    self.update_file_table()
                    self.progress["value"] += 1

        self.file_count_var.set(f"Found {len(self.found_files)} files.")
        if len(self.found_files) > 0:
            self.download_button.config(state=tk.NORMAL)

class InformationFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.create_widgets()

    def create_widgets(self):
        self.info_text = tk.Text(self, wrap="word", height=15, width=80, font=("Arial", 12))
        self.info_text.pack(padx=20, pady=20, fill="both", expand=True)
        self.info_text.insert(tk.END, "This is the information section.\n\n")
        self.info_text.insert(tk.END, "You can add information about the functionality of the application here.")

class DownloadApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("File Downloader")
        self.geometry("1200x800")
        self.create_widgets()

    def create_widgets(self):
        self.main_menu = tk.Menu(self)
        self.config(menu=self.main_menu)

        self.file_menu = tk.Menu(self.main_menu, tearoff=0)
        self.main_menu.add_cascade(label="Menu", menu=self.file_menu)
        self.file_menu.add_command(label="Direct Link", command=self.show_direct_link_frame)
        self.file_menu.add_command(label="Custom Link", command=self.show_custom_link_frame)
        self.file_menu.add_command(label="Information", command=self.show_information_frame)
        self.file_menu.add_command(label="Exit", command=self.quit)

        self.frame_stack = tk.Frame(self)
        self.frame_stack.pack(fill="both", expand=True)

        self.show_direct_link_frame()

    def show_direct_link_frame(self):
        self.clear_frame_stack()
        self.direct_link_frame = DirectLinkFrame(self.frame_stack)
        self.direct_link_frame.pack(fill="both", expand=True)

    def show_custom_link_frame(self):
        self.clear_frame_stack()
        self.custom_link_frame = CustomLinkFrame(self.frame_stack)
        self.custom_link_frame.pack(fill="both", expand=True)

    def show_information_frame(self):
        self.clear_frame_stack()
        self.information_frame = InformationFrame(self.frame_stack)
        self.information_frame.pack(fill="both", expand=True)

    def clear_frame_stack(self):
        for widget in self.frame_stack.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    app = DownloadApp()
    app.mainloop()

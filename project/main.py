import tkinter as tk
from tkinter import ttk
from direct_link import DirectLinkFrame
from custom_link import CustomLinkFrame
from information import InformationFrame

class MainApplication(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("File Management Application")
        self.geometry("1200x800")
        self.create_widgets()

    def create_widgets(self):
        # Create a frame to hold the pages
        self.pages_frame = tk.Frame(self)
        self.pages_frame.pack(fill="both", expand=True)

        # Create the pages
        self.direct_link_frame = DirectLinkFrame(self.pages_frame)
        self.custom_link_frame = CustomLinkFrame(self.pages_frame)
        self.information_frame = InformationFrame(self.pages_frame)

        # Show the Direct Link page initially
        self.show_direct_link()

        # Create the navigation menu
        self.create_navigation_menu()

    def create_navigation_menu(self):
        menu_bar = tk.Menu(self)
        self.config(menu=menu_bar)

        pages_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Pages", menu=pages_menu)
        pages_menu.add_command(label="Direct Link", command=self.show_direct_link)
        pages_menu.add_command(label="Custom Link", command=self.show_custom_link)
        pages_menu.add_command(label="Information", command=self.show_information)

    def show_direct_link(self):
        self.show_page(self.direct_link_frame)

    def show_custom_link(self):
        self.show_page(self.custom_link_frame)

    def show_information(self):
        self.show_page(self.information_frame)

    def show_page(self, page):
        page.pack(fill="both", expand=True)
        for p in [self.direct_link_frame, self.custom_link_frame, self.information_frame]:
            if p != page:
                p.pack_forget()

if __name__ == "__main__":
    app = MainApplication()
    app.mainloop()

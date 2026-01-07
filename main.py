import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from nbtlib import load
from nbtlib.tag import Compound, List

class NBTEditor:
    def __init__(self, root, file_path=None):
        self.root = root
        self.root.title("Simple NBT Editor")

        self.nbt = None
        self.file_path = None

        # Tree view
        self.tree = ttk.Treeview(root, columns=("value", "type"), show="tree headings")
        self.tree.heading("#0", text="Name")
        self.tree.heading("value", text="Value")
        self.tree.heading("type", text="Type")
        self.tree.pack(fill="both", expand=True)

        self.tree.bind("<Double-1>", self.edit_value)

        # Menu
        menu = tk.Menu(root)
        file_menu = tk.Menu(menu, tearoff=0)
        file_menu.add_command(label="Open", command=self.open_file)
        file_menu.add_command(label="Save", command=self.save_file)
        menu.add_cascade(label="File", menu=file_menu)
        root.config(menu=menu)

        # Auto-open file if provided
        if file_path:
            self.load_file(file_path)

    def load_file(self, path):
        try:
            self.nbt = load(path)
            self.file_path = path
            self.tree.delete(*self.tree.get_children())
            self.insert_tag("", "root", self.nbt)
            self.root.title(f"NBT Editor - {path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def open_file(self):
        path = filedialog.askopenfilename(filetypes=[("NBT files", "*.dat")])
        if path:
            self.load_file(path)

    def insert_tag(self, parent, name, tag):
        if isinstance(tag, Compound):
            node = self.tree.insert(parent, "end", text=name, values=("", "Compound"))
            for k, v in tag.items():
                self.insert_tag(node, k, v)

        elif isinstance(tag, List):
            node = self.tree.insert(parent, "end", text=name, values=("", "List"))
            for i, v in enumerate(tag):
                self.insert_tag(node, f"[{i}]", v)

        else:
            self.tree.insert(
                parent,
                "end",
                text=name,
                values=(str(tag), tag.__class__.__name__)
            )

    def edit_value(self, event):
        item = self.tree.selection()
        if not item:
            return

        item = item[0]
        value, tag_type = self.tree.item(item, "values")

        if value == "":
            return

        new_value = simpledialog.askstring(
            "Edit Value",
            f"New value ({tag_type}):",
            initialvalue=value
        )

        if new_value is not None:
            self.tree.set(item, "value", new_value)

    def save_file(self):
        if not self.nbt:
            return

        def apply(node, tag):
            for child in self.tree.get_children(node):
                name = self.tree.item(child, "text")
                value, tag_type = self.tree.item(child, "values")

                if tag_type == "Compound":
                    apply(child, tag[name])
                elif tag_type == "List":
                    index = int(name.strip("[]"))
                    apply(child, tag[index])
                else:
                    tag[name].value = tag[name].__class__(value).value

        try:
            apply("", self.nbt)
            self.nbt.save(self.file_path)
            messagebox.showinfo("Saved", "NBT file saved!")
        except Exception as e:
            messagebox.showerror("Error", str(e))


# --------- ENTRY POINT ----------
if __name__ == "__main__":
    file_arg = sys.argv[1] if len(sys.argv) > 1 else None

    root = tk.Tk()
    app = NBTEditor(root, file_arg)
    root.mainloop()


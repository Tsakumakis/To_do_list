import tkinter as tk
from functools import partial
from typing import List, Optional
import storage


class App:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("My_To_do_list")
        self.root.configure(background="white")

        # top controls
        top = tk.Frame(root, background="white")
        top.pack(fill="x", padx=8, pady=6)
        tk.Label(top, text="What will you do today?", background="white", width=20, height=3).pack(side="left")
        tk.Button(top, text="Add Task", command=self.open_add_modal).pack(side="left", padx=6)
        tk.Button(top, text="Refresh", command=self.refresh_view).pack(side="left", padx=6)

        # view container
        self.view_container = tk.Frame(root)
        self.view_container.pack(fill="both", expand=True, padx=8, pady=8)

        # status label
        self.status_label = tk.Label(root, text="", background="white", fg="black")
        self.status_label.pack(side="bottom", fill="x")

        # initial populate
        self.refresh_view()

    def show_status(self, text: str, kind: str = "info", timeout: int = 3000):
        colors = {"info": "black", "success": "green", "error": "red"}
        fg = colors.get(kind, "black")
        self.status_label.config(text=text, fg=fg)
        if timeout:
            self.root.after(timeout, lambda: self.status_label.config(text=""))

    def refresh_view(self):
        for c in self.view_container.winfo_children():
            c.destroy()
        tasks = storage.load_tasks()
        for t in tasks:
            frame = tk.Frame(self.view_container)
            frame.pack(fill="x", pady=2)
            task_text = t.get("task", "")
            due = t.get("due_date")
            label_text = f"{task_text}"
            if due:
                label_text += f"  (Due: {due})"
            tk.Label(frame, text=label_text).pack(side="left", fill="x", expand=True)
            tk.Button(frame, text="Delete", command=partial(self.delete_task, t.get("id"))).pack(side="right")

    def delete_task(self, task_id: str):
        tasks = storage.load_tasks()
        tasks = [t for t in tasks if t.get("id") != task_id]
        storage.save_tasks(tasks)
        self.show_status("Task deleted.", kind="success")
        self.refresh_view()

    def open_add_modal(self):
        win = tk.Toplevel(self.root)
        win.title("Add Task")
        win.grab_set()
        tk.Label(win, text="Enter your task:").pack(padx=8, pady=6)
        entry = tk.Entry(win, width=50)
        entry.pack(padx=8, pady=6)

        tk.Label(win, text="Due date (optional, DD/MM/YYYY):").pack(padx=8, pady=(6, 0))
        due_entry = tk.Entry(win, width=30)
        due_entry.pack(padx=8, pady=6)

        def on_add():
            text = entry.get().strip()
            due = due_entry.get().strip() or None
            if not text:
                tk.Label(win, text="Please type something.", fg="red").pack()
                return
            tasks = storage.load_tasks()
            tasks.append(storage.make_task(text, due_date=due))
            storage.save_tasks(tasks)
            win.destroy()
            self.show_status("Task saved.", kind="success")
            self.refresh_view()

        tk.Button(win, text="Add", command=on_add).pack(pady=6)
        tk.Button(win, text="Cancel", command=win.destroy).pack(pady=4)
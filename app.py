import tkinter as tk
import datetime
import os
import json
import tempfile
import uuid
from functools import partial

def get_storage_path(filename="tasks.json"):
    """Return a path in a cloud-synced folder if available, else the current directory."""
    # 1) Try OneDrive (Windows)
    onedrive = os.environ.get("OneDrive")
    if onedrive:
        path = os.path.join(onedrive, filename)
        return path

    # 2) Try Dropbox common location in user profile
    home = os.path.expanduser("~")
    possible = [
        os.path.join(home, "Dropbox", filename),
        os.path.join(home, "OneDrive", filename),  # fallback
    ]
    for p in possible:
        if os.path.isdir(os.path.dirname(p)):
            return p

    # 3) Fallback: app directory (same folder as script)
    return os.path.join(os.path.dirname(__file__), filename)

def load_tasks():
    """Load tasks list from JSON file. Returns list of task dicts."""
    path = get_storage_path()
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def atomic_write_json(path, data):
    """Write JSON atomically: write to temp file then replace target."""
    dirpath = os.path.dirname(path) or "."
    fd, tmp_path = tempfile.mkstemp(dir=dirpath, text=True)
    with os.fdopen(fd, "w", encoding="utf-8") as tmp:
        json.dump(data, tmp, ensure_ascii=False, indent=2)
    # atomic replace
    os.replace(tmp_path, path)

def save_all_tasks(tasks):
    """Save full tasks list (atomic)."""
    path = get_storage_path()
    atomic_write_json(path, tasks)

#add task function
def add_task():
    win = tk.Toplevel(root)
    win.title("Add New Task")
    win.grab_set()
    tk.Label(win, text="Enter your task:").pack(padx=10, pady=6)
    entry = tk.Entry(win, width=50)
    entry.pack(padx=10, pady=6)

    def on_add():
        save_task(entry.get(), frame=win)

    tk.Button(win, text="Add Task", command=on_add).pack(pady=6)
    tk.Button(win, text="Cancel", command=win.destroy).pack(pady=6)
    
def save_task(task, frame=None):
    text = (task or "").strip()
    if not text:
        if frame is not None:
            tk.Label(frame, text="Please enter a task.", background="red", fg="white").pack()
        return

    tasks = load_tasks()
    tasks.append({
        "id": str(uuid.uuid4()),
        "task": text,
        "created_at": datetime.datetime.now().isoformat()
    })

    try:
        save_all_tasks(tasks)
    except Exception as e:
        show_status(f"Error saving task: {e}", kind="error")
        return

    show_status(f"Task '{text}' saved.", kind="success")
    if frame is not None:
        frame.destroy()
    
def view_tasks():
    # clear container
    for child in view_container.winfo_children():
        child.destroy()

    tasks = load_tasks()
    for t in tasks:
        frame = tk.Frame(view_container, background="white")
        frame.pack(padx=4, pady=4, fill="x")
        tk.Label(frame, text=t["task"]).pack(side="left", expand=True, fill="x")
        tk.Button(frame, text="Delete", command=partial(delete_task_by_id, t["id"])).pack(side="right")

def delete_task():
    tasks=load_tasks
    delete_frame=tk.Frame(root, width=200, height=200, background="white")
    tk.Label(root,Text="Which task will you delete?",background= "purple",fg="white").pack()

def delete_task_by_id(task_id):
    tasks=load_tasks()
    tasks=[t for t in tasks if t.get ("id") != task_id]
    save_all_tasks(tasks)
    show_status(f"Task delted.", kind="success")

def show_status(text, kind="info",timeout=3000):
    # kind: 'info'', 'success', 'error' -> change color optionally
    colors = {"info": "black", "success": "green", "error": "red"}
    status_Label.config(text=text, fg="black",bg="purple")
    #optional : schedule clear
    if timeout:
        root.after(timeout,lambda: status_Label.config(text=""))
def canvas_scrollable_frame(container):
    canvas=tk.Canvas(container)
    scrollbar=tk.Scrollbar(container, orient="vertical", command=canvas.yview)
    scrollable_frame=tk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    canvas.create_window((0,0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    return scrollable_frame

#Main application window
root=tk.Tk()
root.title("My_To_do_list") 
root.configure(background="Purple") 
root.minsize(640, 480) 
root.maxsize(1920, 1080)
root.geometry("1920x1080+0+0")
tk.Label(root, text="What will you do today?",background="cyan",width=20, height=10).pack()
add_task_button=tk.Button(root, text="Add Task",width=10, height=3,command=add_task)
add_task_button.place(x=170, y=620)
save_task_button=tk.Button(root, text="Save tasks",width=10, height=3, command=lambda: save_task("Manual save - no task provided"))
save_task_button.place(x=170, y=720)
view_tasks_button=tk.Button(root, text="View tasks",width=10, height=3,command=view_tasks)
view_tasks_button.place(x=170, y=820)
delete_task_button=tk.Button(root, text="Delete tasks",width=10, height=3,command=delete_task)
delete_task_button.place(x=170, y=920)
quit_button = tk.Button(root, text="Quit", command=quit,width=10, height=3)
quit_button.place(x=880, y=1020)
view_container=tk.Frame(root)
view_container.pack(padx=10, pady=10, fill="both", expand=True)
#status label so it avoids creating many frames
status_label = tk.Label(root, text="", background="yellow", fg="black")
status_label.pack(side="bottom", fill="x")

root.mainloop()


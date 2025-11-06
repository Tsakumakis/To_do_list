# main.py
import tkinter as tk
import storage
from gui import App

def main():
    # Optional migration step
    storage.migrate_pickle_to_json(old_path="tasks.pkl")
    root = tk.Tk()
    app = App(root)
    root.mainloop()

if __name__ == "__main__":
    main()
"""Clipboard utilities using tkinter."""
import tkinter as tk


def copy_to_clipboard(text: str) -> None:
    """Copy text to the system clipboard."""
    root = tk.Tk()
    root.withdraw()
    root.clipboard_clear()
    root.clipboard_append(text)
    root.update()
    root.destroy()

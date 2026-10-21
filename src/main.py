import tkinter as tk
import os
import api

api.getData()


window = tk.Tk()
window.title("Abfahrtsdisplay")
window.attributes("-fullscreen", True)

print(f"Width: {window.winfo_screenwidth()}, Height: {window.winfo_screenheight()}")

window.mainloop()

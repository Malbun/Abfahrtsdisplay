import tkinter as tk
import os
import api

api.getData()


window = tk.Tk()
window.title("Abfahrtsdisplay")
window.attributes("-zoomed", True)

window.mainloop()

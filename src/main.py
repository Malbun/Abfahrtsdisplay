import tkinter as tk
import os
import api

def toggleFullscreen(event=None):
  isFullscreen = window.attributes("-fullscreen")
  window.attributes("-fullscreen", not isFullscreen)

api.getData()


window = tk.Tk()
window.title("Abfahrtsdisplay")
window.geometry("720x1280")
window.attributes("-fullscreen", True)
window.bind("<F11>", toggleFullscreen)

window.mainloop()

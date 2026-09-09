import tkinter as tk
import os
import api

api.getData()

"""
if os.environ.get('DISPLAY', '') == '':
    os.environ['DISPLAY'] = ':0'

window = tk.Tk()
window.title("Abfahrtsdisplay")
window.attributes("-zoomed", True)

window.mainloop()
"""
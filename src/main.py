import ttkbootstrap as ttk
import api
import datetime

timeLabel = None

def getCurrentTime():
  return datetime.datetime.now().strftime("%H:%M:%S")

def toggleFullscreen(none):
  r"""
  Function for toggling the fullscreen mode
  :return:
  """
  isFullscreen = window.attributes("-fullscreen")
  window.attributes("-fullscreen", not isFullscreen)

def drawWindow(main):
  global timeLabel
  apiData, stationName = api.getData()

  for child in main.winfo_children():
    child.destroy()

  headerFrame = ttk.Frame(main, height=40)
  headerFrame.pack(fill="x")
  headerFrame.columnconfigure((0, 1, 2), weight=1, uniform="col")

  stationLabel = ttk.Label(headerFrame, text=stationName, font=("Arial", 32))
  stationLabel.grid(row=0, column=1)

  timeLabel = ttk.Label(headerFrame, text=getCurrentTime(), font=("Arial", 20))
  timeLabel.grid(row=0, column=2)

  bodyFrame = ttk.Frame(main)
  bodyFrame.pack(fill="x")

  for result in apiData:

    resultFrame = ttk.Frame(bodyFrame)
    resultFrame.pack(fill="x")

    topSeperator = ttk.Separator(resultFrame, orient="horizontal")
    topSeperator.grid(row=0, column=0, columnspan=4, sticky="ew", pady=4)

    resultFrame.columnconfigure(0, weight=0)
    resultFrame.columnconfigure(1, weight=0)
    resultFrame.columnconfigure(2, weight=1)
    resultFrame.columnconfigure(3, weight=0)

    serviceNameLabel = ttk.Label(resultFrame, text=result["details"]["lineName"], font=("Arial", 16, "bold"), width=5, anchor="w")
    serviceNameLabel.grid(row=1, column=0, sticky="w")

    destinationLabel = ttk.Label(resultFrame, text=result["details"]["destination"], font=("Arial", 13, "bold"), padding=5)
    destinationLabel.grid(row=1, column=1, sticky="w")

    nCalls = len(result["onwardCalls"]["calls"]) - 1
    if nCalls > 3:
      nCalls = 3

    if nCalls != 0:
      onwardCallsFrame = ttk.Frame(resultFrame, width=270, height=30)
      onwardCallsFrame.grid(row=1, column=2, sticky="w")

      for i in range(nCalls):
        callLabel = ttk.Label(onwardCallsFrame, text=result["onwardCalls"]["calls"][i], font=("Arial", 12))
        callLabel.grid(row=0, column=i, sticky="w", padx=3)

    rightFrame = ttk.Frame(resultFrame)
    rightFrame.grid(row=1, column=3, sticky="e")

    quayLabel = ttk.Label(rightFrame, text=result["thisCall"]["estimatedQuay"], font=("Arial Black", 20), padding=5)
    if result["thisCall"]["otherQuay"]:
      quayLabel.config(foreground="red")
    quayLabel.grid(row=0, column=0, sticky="e")

    timeFrame = ttk.Frame(rightFrame)
    timeFrame.grid(row=0, column=1, sticky="e")

    timetabledTimeLabel = ttk.Label(timeFrame, text=result["thisCall"]["timetabledTime"].strftime("%H:%M:%S"), font=("Arial", 12), padding=2, width=8)
    timetabledTimeLabel.grid(row=0, column=0, sticky="e")

    estimatedTimeLabel = ttk.Label(timeFrame, text=result["thisCall"]["estimatedTime"].strftime("%H:%M:%S"), font=("Arial", 12, "bold"), padding=2, width=8)
    estimatedTimeLabel.grid(row=1, column=0, sticky="e")

  refreshButtonFrame = ttk.Frame(bodyFrame)
  refreshButtonFrame.pack()

  buttonStyle = ttk.Style()
  buttonStyle.configure('info.TButton', font=('Arial', 20))
  refreshButton = ttk.Button(refreshButtonFrame, text="Aktualisieren", command=lambda: drawWindow(window), bootstyle="info")
  refreshButton.pack(pady=5, padx=5)


def updateTime(root):
  timeLabel.config(text=getCurrentTime())
  root.after(50, lambda: updateTime(root))

def redraw(root):
  drawWindow(root)
  root.after(20000, lambda: redraw(root))


if __name__ == "__main__":

  # Set up the tk window
  window = ttk.App(theme="pulse-dark")
  window.title("Abfahrtsdisplay")
  window.geometry("720x1280")
  window.attributes("-fullscreen", True)

  # Hotkeys
  window.bind("<F11>", toggleFullscreen)
  window.bind("<F5>", lambda Event: drawWindow(window))

  # Time Label
  drawWindow(window)

  window.after(20000, lambda: drawWindow(window))
  window.after(50, lambda: updateTime(window))

  window.mainloop()



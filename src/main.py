import tkinter as tk
from tkinter import ttk
import api
import schedule

def toggleFullscreen(none):
  r"""
  Function for toggling the fullscreen mode
  :return:
  """
  isFullscreen = window.attributes("-fullscreen")
  window.attributes("-fullscreen", not isFullscreen)

def drawWindow(main):
  apiData, stationName = api.getData()
  print(apiData)

  for child in main.winfo_children():
    child.destroy()

  headerFrame = ttk.Frame(main, height=40)
  headerFrame.pack()

  stationLabel = ttk.Label(headerFrame, text=stationName, font=("Arial", 32))
  stationLabel.pack()

  bodyFrame = ttk.Frame(main)
  bodyFrame.pack(fill="x")

  for result in apiData:

    resultFrame = ttk.Frame(bodyFrame)
    resultFrame.pack(fill="x")

    seperatorFrame = tk.Frame(resultFrame, height=3, bg="black")
    seperatorFrame.grid(row=0, column=0, columnspan=4, sticky="ew")

    topSeperator = ttk.Separator(seperatorFrame, orient="horizontal")
    topSeperator.pack()

    resultFrame.columnconfigure(0, weight=0)
    resultFrame.columnconfigure(1, weight=0)
    resultFrame.columnconfigure(2, weight=1)
    resultFrame.columnconfigure(3, weight=0)

    serviceNameLabel = ttk.Label(resultFrame, text=result["details"]["lineName"], font=("Arial", 16, "bold"), width=5, anchor=tk.W)
    serviceNameLabel.grid(row=1, column=0, sticky=tk.W)

    destinationLabel = ttk.Label(resultFrame, text=result["details"]["destination"], font=("Arial", 13, "bold"), padding=5)
    destinationLabel.grid(row=1, column=1, sticky=tk.W)

    nCalls = len(result["onwardCalls"]["calls"]) - 1
    if nCalls > 3:
      nCalls = 3

    if nCalls != 0:
      onwardCallsFrame = ttk.Frame(resultFrame, width=270, height=30, relief="solid")
      onwardCallsFrame.grid(row=1, column=2, sticky=tk.W)

      for i in range(nCalls):
        print(result["onwardCalls"]["calls"][i])
        callLabel = ttk.Label(onwardCallsFrame, text=result["onwardCalls"]["calls"][i], font=("Arial", 12), padding=2)
        callLabel.grid(row=0, column=i, sticky=tk.W)

    rightFrame = ttk.Frame(resultFrame)
    rightFrame.grid(row=1, column=3, sticky=tk.E)

    quayColor = "black"
    if result["thisCall"]["otherQuay"]:
      quayColor = "red"

    quayLabel = ttk.Label(rightFrame, text=result["thisCall"]["estimatedQuay"], font=("Arial Black", 20), padding=5, foreground=quayColor)
    quayLabel.grid(row=0, column=0, sticky=tk.E)

    timeFrame = ttk.Frame(rightFrame)
    timeFrame.grid(row=0, column=1, sticky=tk.E)

    timetabledTimeLabel = ttk.Label(timeFrame, text=result["thisCall"]["timetabledTime"].strftime("%H:%M:%S"), font=("Arial", 12), padding=2, width=8)
    timetabledTimeLabel.grid(row=0, column=0, sticky=tk.E)

    estimatedTimeLabel = ttk.Label(timeFrame, text=result["thisCall"]["estimatedTime"].strftime("%H:%M:%S"), font=("Arial", 12, "bold"), padding=2, width=8)
    estimatedTimeLabel.grid(row=1, column=0, sticky=tk.E)

  refreshButtonFrame = ttk.Frame(bodyFrame)
  refreshButtonFrame.pack()

  refreshButton = ttk.Button(refreshButtonFrame, text="Aktualisieren", command=lambda: drawWindow(window))
  refreshButton.pack(pady=5, padx=5)

if __name__ == "__main__":

  # Set up the tk window
  window = tk.Tk()
  window.title("Abfahrtsdisplay")
  window.geometry("720x1280")
  window.attributes("-fullscreen", True)

  # Hotkeys
  window.bind("<F11>", toggleFullscreen)
  window.bind("<F5>", lambda Event: drawWindow(window))

  drawWindow(window)

  def poll():
    schedule.run_pending()
    window.after(1000, poll)

  poll()

  schedule.every(20).seconds.do(lambda: drawWindow(window))

  window.mainloop()



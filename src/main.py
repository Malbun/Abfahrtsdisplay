import tkinter as tk
from tkinter import ttk
import api

def toggleFullscreen(none):
  r"""
  Function for toggling the fullscreen mode
  :return:
  """
  isFullscreen = main.attributes("-fullscreen")
  main.attributes("-fullscreen", not isFullscreen)

if __name__ == "__main__":
  # Get initial data
  apiData, stationName = api.getData()
  print(apiData)

  # Set up the tk window
  main = tk.Tk()
  main.title("Abfahrtsdisplay")
  main.geometry("720x1280")
  main.attributes("-fullscreen", True)
  main.bind("<F11>", toggleFullscreen)

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

    onwardCallsFrame = ttk.Frame(resultFrame, width=270, height=30, relief="solid")
    onwardCallsFrame.grid(row=1, column=2, sticky=tk.W)

    nCalls = len(result["onwardCalls"]["calls"]) - 1
    if nCalls > 3:
      nCalls = 3

    for i in range(nCalls):
      print(result["onwardCalls"]["calls"][i])
      callLabel = ttk.Label(onwardCallsFrame, text=result["onwardCalls"]["calls"][i], font=("Arial", 12), padding=2)
      callLabel.grid(row=0, column=i, sticky=tk.W)

    timeFrame = ttk.Frame(resultFrame)
    timeFrame.grid(row=1, column=3, sticky=tk.E)

    timetabledTimeLabel = ttk.Label(timeFrame, text=result["thisCall"]["timetabledTime"].strftime("%H:%M:%S"), font=("Arial", 12), padding=2, width=8)
    timetabledTimeLabel.grid(row=0, column=0, sticky=tk.E)

    estimatedTimeLabel = ttk.Label(timeFrame, text=result["thisCall"]["estimatedTime"].strftime("%H:%M:%S"), font=("Arial", 12, "bold"), padding=2, width=8)
    estimatedTimeLabel.grid(row=1, column=0, sticky=tk.E)

  main.mainloop()



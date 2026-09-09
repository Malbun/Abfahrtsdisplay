from collections import defaultdict

import requests
import yaml
import os
import json
from datetime import datetime, timezone
import xmltodict


def getData():
  configData = loadConfig()

  apiKey = configData["key"]
  stationName = configData["station"]

  sloid = stationNameToSLOID(stationName)

  ojpUrl = "https://api.opentransportdata.swiss/ojp20"
  headers = {
    "Content-Type": "application/xml",
    "Authorization": f"Bearer {apiKey}"
  }
  body = getBody(sloid, stationName)

  response = requests.post(
    url=ojpUrl,
    headers=headers,
    data=body
  )

  if response.status_code != 200:
    statuscode = response.status_code
    raise ApiError(f"Error during OJP 2.0 request. Response with status code {statuscode}", 2)

  responseDict = xmltodict.parse(response.content)
  stopEventResult = responseDict["OJP"]["OJPResponse"]["siri:ServiceDelivery"]["OJPStopEventDelivery"]["StopEventResult"]
  print(json.dumps(stopEventResult))

  results = []

  # iterate over each StopEvent
  for stopEvent in stopEventResult:
    currentResult = defaultdict(dict)

    # get the details
    currentResult["details"]["lineName"] = stopEvent["StopEvent"]["Service"]["PublicCode"]
    currentResult["details"]["number"] = stopEvent["StopEvent"]["Service"]["TrainNumber"]
    currentResult["details"]["destination"] = stopEvent["StopEvent"]["Service"]["DestinationText"]["Text"]["#text"]

    # check if a quay field exists (cmp. bus stops) otherwise leave it empty
    if "PlannedQuay" in stopEvent["StopEvent"]["ThisCall"]["CallAtStop"]:
      # get the planned quay
      currentResult["thisCall"]["plannedQuay"] = stopEvent["StopEvent"]["ThisCall"]["CallAtStop"]["PlannedQuay"]["Text"]["#text"]

      # check if an estimated quay is present in data. Process the estimated quay and set the other quay flag
      if "EstimatedQuay" in stopEvent["StopEvent"]["ThisCall"]["CallAtStop"]:
        currentResult["thisCall"]["estimatedQuay"] = stopEvent["StopEvent"]["ThisCall"]["CallAtStop"]["EstimatedQuay"]["Text"]["#text"]
        currentResult["thisCall"]["otherQuay"] = not currentResult["thisCall"]["estimatedQuay"] == currentResult["thisCall"]["plannedQuay"]
      else:
        currentResult["thisCall"]["estimatedQuay"] = currentResult["thisCall"]["plannedQuay"]
        currentResult["thisCall"]["otherQuay"] = False
    else:
      currentResult["thisCall"]["plannedQuay"] = ""
      currentResult["thisCall"]["estimatedQuay"] = ""
      currentResult["thisCall"]["otherQuay"] = False

    # get the timetabled time
    currentResult["thisCall"]["timetabledTime"] = datetime.fromisoformat(stopEvent["StopEvent"]["ThisCall"]["CallAtStop"]["ServiceDeparture"]["TimetabledTime"])

    # check if an estimated time is present in data. Process the estimated time and set the delayed flag
    if "EstimatedTime" in stopEvent["StopEvent"]["ThisCall"]["CallAtStop"]["ServiceDeparture"]:
      currentResult["thisCall"]["estimatedTime"] = datetime.fromisoformat(stopEvent["StopEvent"]["ThisCall"]["CallAtStop"]["ServiceDeparture"]["EstimatedTime"])
      currentResult["thisCall"]["delayed"] = (currentResult["thisCall"]["estimatedTime"] - currentResult["thisCall"]["timetabledTime"]).seconds >= 180
    else:
      currentResult["thisCall"]["estimatedTime"] = currentResult["thisCall"]["timetabledTime"]
      currentResult["thisCall"]["delayed"] = False

    # get all onward calls
    onwardCall = stopEvent["StopEvent"]["OnwardCall"]
    calls = []

    if type(onwardCall) == list:
      for call in onwardCall:
        stationName = call["CallAtStop"]["StopPointName"]["Text"]["#text"]
        calls.append(stationName)

    else:
      stationName = onwardCall["CallAtStop"]["StopPointName"]["Text"]["#text"]
      calls.append(stationName)

    currentResult["onwardCalls"] = {"calls": calls}

    results.append(dict(currentResult))

  print(results)
  return results


def stationNameToSLOID(stationName):
  r"""
  Gets the didok number by station name
  :param stationName:  exact spelling required
  :return: The corresponding didok number
  """

  requestUrl = f"https://data.sbb.ch/api/explore/v2.1/catalog/datasets/dienststellen-gemass-opentransportdataswiss/records?select=sloid&where=designationofficial%3D%22{stationName}%22&limit=1"
  response = requests.get(requestUrl)
  if response.status_code != 200:
    statuscode = response.status_code
    raise ApiError(f"Error during SLOID resolving. Response with status code {statuscode}", 1)

  else:
    sloidData = json.loads(response.content)
    sloid = sloidData["results"][0]["sloid"]
    print(sloid)
    return sloid


def loadConfig() -> dict:
  r"""
  Loads the configuration from the disk
  :return: A dict with the loaded configuration
  """

  configFilePath = os.path.dirname(os.getcwd()) + "\\Abfahrtsdisplay\\config.yml"
  with open(configFilePath, "r")as ymlFile:
    configData = yaml.load(ymlFile.read(), yaml.FullLoader)["config"]

  return configData

def getBody(sloid, stationName):
  now = datetime.now(timezone.utc)
  timestamp = now.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
  print(timestamp)
  body = f"""
    <OJP xmlns="http://www.vdv.de/ojp" xmlns:siri="http://www.siri.org.uk/siri" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xsi:schemaLocation="http://www.vdv.de/ojp" version="2.0">
    <OJPRequest>
        <siri:ServiceRequest>
            <siri:ServiceRequestContext>
                <siri:Language>de</siri:Language>
            </siri:ServiceRequestContext>
            <siri:RequestTimestamp>{timestamp}</siri:RequestTimestamp>
            <siri:RequestorRef>Malbun</siri:RequestorRef>
            <OJPStopEventRequest>
                <siri:RequestTimestamp>{timestamp}</siri:RequestTimestamp>
                <siri:MessageIdentifier>{"Abfahrtsdisplay_" + timestamp}</siri:MessageIdentifier>
                <Location>
                    <PlaceRef>
                        <siri:StopPointRef>{sloid}</siri:StopPointRef>
                        <Name>
                            <Text>{stationName}</Text>
                        </Name>
                    </PlaceRef>
                    <DepArrTime>{timestamp}</DepArrTime>
                </Location>
                <Params>
                    <NumberOfResults>10</NumberOfResults>
                    <StopEventType>departure</StopEventType>
                    <IncludePreviousCalls>false</IncludePreviousCalls>
                    <IncludeOnwardCalls>true</IncludeOnwardCalls>
                    <UseRealtimeData>full</UseRealtimeData>
                </Params>
            </OJPStopEventRequest>
        </siri:ServiceRequest>
    </OJPRequest>
    </OJP>
    """
  return body

class ApiError(Exception):
  r"""
  Custom Error; raised if an API-Request gone wrong
  """

  def __init__(self, message, error_code):
    super().__init__(message)
    self.message = message
    self.error_code = error_code

  def __str__(self):
    return f"API Exception happened: {self.message}  Error Code: {self.error_code}"



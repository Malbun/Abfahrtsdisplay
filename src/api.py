import requests
import yaml
import os
import json



def getData():
  configData = loadConfig()

  apiKey = configData["key"]
  stationName = configData["station"]

  didok = stationNameToDidok(stationName)



def stationNameToDidok(stationName):
  r"""
  Gets the didok number by station name
  :param stationName:  exact spelling required
  :return: The corresponding didok number
  """

  requestUrl = f"https://data.sbb.ch/api/explore/v2.1/catalog/datasets/dienststellen-gemass-opentransportdataswiss/records?select=number&where=designationofficial%3D%22{stationName}%22&limit=1"
  response = requests.get(requestUrl)
  if response.status_code != 200:
    statuscode = response.status_code
    raise ApiError(f"Error during DiDok resolving. Response with status code {statuscode}", 1)

  else:
    didokData = json.loads(response.content)
    didok = didokData["results"][0]["number"]
    return didok


def loadConfig() -> dict:
  r"""
  Loads the configuration from the disk
  :return: A dict with the loaded configuration
  """

  configFilePath = os.path.dirname(os.getcwd()) + "\\Abfahrtsdisplay\\config.yml"
  with open(configFilePath, "r")as ymlFile:
    configData = yaml.load(ymlFile.read(), yaml.FullLoader)["config"]

  return configData

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



import json, time
import requests

url = "https://dorm-laundry-gw.nctu.edu.tw:5000/api/status"

def get_data (url):
  """
  crawl the web and return a dict
  """
  while True:
    r = requests.get(url)
    if r.status_code != 200:
      print("reconnect ......")
    else:
      data = r.text
      info = json.loads(data)
      del info[""]
      return info

def check_status (data):
  """"
  chck DATA with event are ready, return a list of dict
  """
  result = {}
  for index in data:
    if (data[index]["event"] == "READY"):
      result[index] = data[index]
  return result

def get_status():
  """"
  return a list of dict with already machine
  """
  data = get_data(url)
  status = check_status(data)
  return status

def sort_data_with_geo(cond, data):
  """
   return a list of dict of all machine with ID starting with cond
  """
  result = {}
  for index in data:
    if (data[index]["id"].startswith(cond)):
      result[index] = data[index]
  return result

def get_duration(machine):
  """
  return how long the machine will finish (washer => 45)
  """
  data = sort_data_with_geo(machine, get_data (url))
  current_time = time.time()
  duration = (current_time - data[machine]["ts"]/1000)/60
  if (45 - duration > 0):
    return 45 - duration
  else:
    return 0

def timesup(machine):
  """
  whether to notify the user or not
  """
  duration = get_duration(machine)
  return duration > 40

def get_earilest_avaliable(cond):
  data = sort_data_with_geo(cond, get_data (url));
  rest = 50  
  for index in data:
    if get_duration(index) < rest:
      rest = get_duration(index)
  return rest
